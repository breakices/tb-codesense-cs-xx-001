#!/usr/bin/env python3
"""Supplier self-check for CS-XX-001.

    python run_selfcheck.py [--python <interpreter with tests/requirements.lock installed>]

For the untouched snapshot (NOP), the reference fix (Golden), the four
calibration patches and the two variants it does the following three times
each: copy environment/workspace/repo into a new empty directory, apply the
patch (nothing for NOP), run tests/score.py on that copy, delete the copy.
Every run therefore starts from the same snapshot and shares nothing with any
other run.  It then checks that the three runs of a case agree test by test
and that the score is the expected one, and writes the evidence next to this
file.
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

SELF = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.abspath(os.path.join(SELF, "..", "..", ".."))
# Evidence of a run on this machine goes to a directory of its own; the runs
# through the verifier entry in the task image are kept in linux-amd64/.
HERE = os.path.join(SELF, "local-%s-%s" % (platform.system().lower(), platform.machine().lower()))
os.makedirs(HERE, exist_ok=True)
REPO = os.path.join(TASK, "environment", "workspace", "repo")
SCORE = os.path.join(TASK, "tests", "score.py")

CASES = [
    # name, patch relative to the task directory, expected score
    ("nop", None, 0),
    ("golden", "solution/golden/golden.patch", 1),
    ("full_score", "tests/calibration/full_score.patch", 1),
    ("equivalent", "tests/calibration/equivalent.patch", 1),
    ("defective", "tests/calibration/defective.patch", 0),
    ("guessed", "tests/calibration/guessed.patch", 0),
    ("variant_a", "solution/variants/variant_a.patch", 1),
    ("variant_b", "solution/variants/variant_b.patch", 1),
]


def tree_digest(root):
    """One digest over every file of a tree (relative path and content)."""
    digest = hashlib.sha256()
    for directory, names, files in os.walk(root):
        names.sort()
        for name in sorted(files):
            path = os.path.join(directory, name)
            digest.update(os.path.relpath(path, root).encode("utf-8") + b"\0")
            with open(path, "rb") as handle:
                digest.update(hashlib.sha256(handle.read()).digest())
    return digest.hexdigest()


def one_run(name, patch, run, python):
    work = tempfile.mkdtemp(prefix="cs-selfcheck-%s-%d-" % (name, run))
    copy = os.path.join(work, "repo")
    try:
        shutil.copytree(REPO, copy, symlinks=True)
        before = tree_digest(copy)
        applied = ""
        if patch:
            with open(os.path.join(TASK, patch), "rb") as handle:
                proc = subprocess.run(
                    ["patch", "-p1", "--no-backup-if-mismatch", "-s"],
                    cwd=copy, stdin=handle, capture_output=True, text=True,
                )
            if proc.returncode != 0:
                raise SystemExit("%s: patch did not apply\n%s%s" % (name, proc.stdout, proc.stderr))
            applied = patch
        after = tree_digest(copy)
        out = os.path.join(HERE, "%s-run%d.json" % (name, run))
        proc = subprocess.run(
            [python, SCORE, "--repo", copy, "--out", out, "--python", python],
            capture_output=True, text=True,
        )
        with open(os.path.join(HERE, "%s-run%d.log" % (name, run)), "w", encoding="utf-8") as handle:
            handle.write("command: %s %s --repo <fresh copy of the snapshot%s> --python %s\n" % (
                python, os.path.relpath(SCORE, TASK), " + " + applied if applied else ", no change", python))
            handle.write("snapshot digest before patch: %s\n" % before)
            handle.write("tree digest when scored:      %s\n" % after)
            handle.write("exit code: %d\n--- stdout ---\n%s\n--- stderr ---\n%s\n" % (proc.returncode, proc.stdout, proc.stderr))
        document = json.load(open(out, encoding="utf-8"))
        return document, before, after
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    versions = subprocess.run(
        [args.python, "-c",
         "import sys, platform, django, pytest; print(sys.version.split()[0], platform.platform(), 'django', django.get_version(), 'pytest', pytest.__version__)"],
        capture_output=True, text=True).stdout.strip()
    summary = {
        "task": "CS-XX-001",
        "snapshot_upstream_commit": "4dc248a63 (django-oscar)",
        "snapshot_digest": tree_digest(REPO),
        "interpreter": versions,
        "host": platform.platform(),
        "cases": [],
    }
    ok = True
    for name, patch, expected in CASES:
        runs = [one_run(name, patch, run, args.python) for run in (1, 2, 3)]
        documents = [r[0] for r in runs]
        signatures = [[(x["id"], x["status"]) for x in d["results"]] for d in documents]
        failed = [x["id"] for x in documents[0]["results"] if x["status"] != "passed"]
        case = {
            "case": name,
            "patch": patch,
            "expected_score": expected,
            "scores": [d["score"] for d in documents],
            "valid": [d["valid"] for d in documents],
            "ut_passed": [d["ut_passed"] for d in documents],
            "ut_total": documents[0]["ut_total"],
            "three_runs_identical": signatures[0] == signatures[1] == signatures[2],
            "failed_ids": failed,
            "started_from_same_snapshot": len({r[1] for r in runs}) == 1 and runs[0][1] == summary["snapshot_digest"],
            "tree_changed_by_patch": runs[0][1] != runs[0][2],
        }
        case["ok"] = (
            case["scores"] == [expected] * 3 and all(case["valid"]) and case["three_runs_identical"]
            and case["started_from_same_snapshot"] and case["tree_changed_by_patch"] == bool(patch)
        )
        ok = ok and case["ok"]
        summary["cases"].append(case)
        print("%-11s score %s  passed %s/%d  identical %s  ok %s  failed %s" % (
            name, case["scores"], case["ut_passed"], case["ut_total"], case["three_runs_identical"], case["ok"], ",".join(failed) or "-"))
    summary["all_ok"] = ok
    with open(os.path.join(HERE, "SUMMARY.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    print("all ok:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
