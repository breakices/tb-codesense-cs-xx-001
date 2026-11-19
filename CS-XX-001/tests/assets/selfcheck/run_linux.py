"""Recheck the eight controls, three times each, using the official Linux verifier.

Build the task image from environment/, then run this script with its tag or ID
and a new output directory. All test processes run without network access.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

TASK = Path(__file__).resolve().parents[3]
CONTROLS = {
    "nop": (None, 0),
    "golden": ("solution/golden/golden.patch", 1),
    "full_score": ("tests/calibration/full_score.patch", 1),
    "equivalent": ("tests/calibration/equivalent.patch", 1),
    "guessed": ("tests/calibration/guessed.patch", 0),
    "defective": ("tests/calibration/defective.patch", 0),
    "variant_a": ("solution/variants/variant_a.patch", 1),
    "variant_b": ("solution/variants/variant_b.patch", 1),
}


def docker(*args):
    return subprocess.check_output(["docker", *map(str, args)], text=True).strip()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_case(image, output, name, repeat):
    patch, expected = CONTROLS[name]
    label = f"{name}-run{repeat}"
    with tempfile.TemporaryDirectory() as work:
        raw = Path(work)
        args = ["run", "--platform", "linux/amd64", "--rm", "--network", "none",
                "--user", "root", "-v", f"{TASK / 'tests'}:/tests:ro",
                "-v", f"{raw}:/logs/verifier"]
        if name == "golden":
            args += ["-v", f"{TASK / 'solution'}:/solution:ro"]
            command = "sh /solution/solve.sh && sh /tests/test.sh"
        elif patch:
            args += ["-v", f"{TASK / patch}:/control.patch:ro"]
            command = "cd /workspace/repo && patch -s -p1 < /control.patch && sh /tests/test.sh"
        else:
            command = "sh /tests/test.sh"
        docker(*args, image, "sh", "-ec", command)
        result = json.loads((raw / "result.json").read_text())
        statuses = {row["id"]: row["status"] for row in result["results"]}
        reward = int((raw / "reward.txt").read_text())
        if (not result["valid"] or reward != expected or result["score"] != expected
                or set(statuses.values()) - {"passed", "failed"}):
            raise RuntimeError(f"{label}: invalid control: reward={reward}, statuses={statuses}")
        shutil.copyfile(raw / "result.json", output / f"{label}.json")
        # Preserve the original streams, JUnit data, entrypoint output and reward.
        shutil.make_archive(str(output / label), "gztar", root_dir=raw)
        return statuses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("output", type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    image = docker("image", "inspect", "--format", "{{.Id}}", args.image)
    info = docker("run", "--platform", "linux/amd64", "--rm", "--network", "none",
                  image, "sh", "-ec",
                  "test ! -e /tests && test ! -e /solution; cd /workspace/repo; "
                  "git rev-parse HEAD^{tree}; python -V; python -m django --version; "
                  "python -m pytest --version; uname -m")
    (output / "ENVIRONMENT.txt").write_text(f"image {image}\n{info}\n", encoding="utf-8")
    summary = {}
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        jobs = {name: [pool.submit(run_case, image, output, name, repeat)
                       for repeat in range(1, 4)] for name in CONTROLS}
        for name, futures in jobs.items():
            results = [future.result() for future in futures]
            if not all(row == results[0] for row in results):
                raise RuntimeError(f"{name}: per-test outcomes changed across repeats")
            summary[name] = {"runs": len(results), "score": CONTROLS[name][1],
                             "ut_total": len(results[0]),
                             "ut_passed": sum(s == "passed" for s in results[0].values()),
                             "failed_ids": [i for i,s in results[0].items() if s == "failed"]}
            print(name, summary[name], flush=True)
    inputs = [*sorted((TASK / "tests").glob("*.py")), TASK / "tests/test.sh",
              TASK / "tests/ut_index.json", TASK / "instruction.md", TASK / "environment/Dockerfile",
              TASK / "environment/requirements.lock", TASK / "solution/solve.sh",
              *(TASK / patch for patch,_ in CONTROLS.values() if patch)]
    dump(output / "SUMMARY.json", {"controls": summary, "image_id": image, "inputs_sha256": {
        str(path.relative_to(TASK)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs
    }})


if __name__ == "__main__":
    main()
