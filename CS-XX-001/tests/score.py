#!/usr/bin/env python3
"""Scoring entry for CS-XX-001.

    python score.py --repo <path to the repository after the answer> [--out result.json]

Runs every unit test listed in ut_index.json against the given repository and
prints one JSON document:

    score          1 if every listed test passed, otherwise 0
    valid          False if the run itself is unusable (a listed test was not
                   collected, was skipped, or the test process broke); the
                   score is then 0 and must not be read as a model failure
    ut_total / ut_passed / ut_pass_rate   diagnostics only
    results        one entry per test: id, ut_name, dimension,
                   targets_badpattern, status, evidence

Scoring is done by test assertions only.  No model is called, nothing is read
from the network, and the result does not depend on time or random numbers.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_FILE = "test_money_contract.py"


def run_pytest(repo, python):
    src = os.path.join(os.path.abspath(repo), "src")
    if not os.path.isdir(os.path.join(src, "oscar")):
        raise SystemExit("no src/oscar under %s" % repo)
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", "/tmp"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": src,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONWARNINGS": "ignore",
    }
    with tempfile.TemporaryDirectory(prefix="cs-score-") as tmp:
        report = os.path.join(tmp, "junit.xml")
        cmd = [
            python, "-m", "pytest", TEST_FILE,
            "-p", "no:cacheprovider", "-p", "no:randomly",
            "--rootdir", HERE, "-c", os.devnull,
            "-q", "--tb=short", "-o", "junit_family=xunit1",
            "--junitxml", report,
        ]
        proc = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True)
        cases = {}
        if os.path.exists(report):
            for case in ET.parse(report).getroot().iter("testcase"):
                status, evidence = "passed", ""
                for child in case:
                    if child.tag in ("failure", "error"):
                        status = "failed" if child.tag == "failure" else "error"
                        evidence = (child.get("message") or "").strip()
                        text = (child.text or "").strip().splitlines()
                        tail = [line for line in text if line.startswith("E ")]
                        if tail:
                            evidence = " | ".join(line[1:].strip() for line in tail[:6])
                        location = [line for line in text if TEST_FILE in line]
                        if location:
                            evidence += " @ " + location[-1].strip()
                    elif child.tag == "skipped":
                        status, evidence = "skipped", (child.get("message") or "").strip()
                cases[case.get("name")] = (status, evidence)
        return proc, cases


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    index = json.load(open(os.path.join(HERE, "ut_index.json"), encoding="utf-8"))
    proc, cases = run_pytest(args.repo, args.python)

    listed = {entry["ut_name"] for entry in index}
    collection_error = None
    if cases and not (listed & set(cases)):
        # The test module could not be imported against this repository (for
        # example the answer left a syntax or import error in the package).
        # Every test then counts as an error of the answer.
        broken = [e for s, e in cases.values() if s == "error"]
        if broken:
            collection_error = "test module could not be loaded: " + broken[0]
            cases = {name: ("error", collection_error) for name in listed}

    results, problems = [], []
    for entry in index:
        status, evidence = cases.get(entry["ut_name"], ("not_run", "test was not collected"))
        if status in ("not_run", "skipped", "error"):
            problems.append("%s: %s" % (entry["ut_name"], status))
        results.append({
            "id": entry["id"],
            "ut_name": entry["ut_name"],
            "dimension": entry["dimension"],
            "targets_badpattern": entry.get("targets_badpattern", False),
            "status": status,
            "evidence": evidence if status != "passed" else "all assertions held",
        })
    extra = sorted(set(cases) - {entry["ut_name"] for entry in index})
    if extra:
        problems.append("tests not listed in ut_index.json: %s" % ", ".join(extra))

    # An "error" is a test that could not run its assertions (for example the
    # code under test no longer imports).  That is a failed answer, not a
    # broken scorer, as long as the test was collected; only missing or
    # skipped tests make the run unusable.
    unusable = [p for p in problems if not p.endswith(": error")]
    passed = sum(1 for r in results if r["status"] == "passed")
    total = len(results)
    document = {
        "task": "CS-XX-001",
        "valid": not unusable,
        "score": 1 if (not unusable and passed == total) else 0,
        "ut_total": total,
        "ut_passed": passed,
        "ut_pass_rate": round(passed / total, 4) if total else 0.0,
        "problems": problems,
        "pytest_exit_code": proc.returncode,
        "results": results,
    }
    if not cases:
        document["valid"] = False
        document["score"] = 0
        document["problems"].append("pytest produced no report")
        document["pytest_output_tail"] = (proc.stdout + proc.stderr)[-2000:]
    text = json.dumps(document, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
