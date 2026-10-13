#!/usr/bin/env python3
"""Assemble the Telegram digest input from per-leg self-report records.

The announce job used to bulk-fetch the run's jobs listing (600+ jobs on
full nightlies, 7+ pages of a query that 502/504s under platform stress)
plus the artifacts listing. Instead, every build leg now self-reports via
a tiny `rec-*` artifact (see the "digest record" steps in build.yml and the
manager jobs in main.yml) carrying everything the digest needs: family,
sublevel tag, flavor, root identity, conclusion, and its own AnyKernel3
artifact id (captured for free from actions/upload-artifact's artifact-id
output). The announce downloads those records with actions/download-artifact
(the runtime artifact service, not the REST API) and this script turns them
into the exact shapes telegram_digest.py already consumes:

  jobs-out:      [{"name": ..., "conclusion": ...}, ...]
  artifacts-out: [{"name": ..., "id": ...}, ...]

Synthesized job names reproduce the format the digest parser expects from
the jobs API, e.g.:

  build-android14-6-1 (next, KernelSU-Next, <40-hex>) / 6.1.157-android14-2025-12 (KernelSU-Next)

so telegram_digest.py runs unchanged. If no records are found the script
exits with status 3 and the caller falls back to the REST fetch path.
"""
import argparse
import json
import os
import sys

# Root id -> display label. Must mirror ROOT_MATRIX in main.yml (mk_entry).
ROOT_LABELS = {
    "kernelsu": "KernelSU",
    "next": "KernelSU-Next",
    "bakasu": "BakaSU",
    "sukisu-ultra": "SukiSU-Ultra",
    "kowsu": "KowSU",
    "none": "No Root",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", required=True,
                    help="directory holding merged rec-*.json record files")
    ap.add_argument("--jobs-out", required=True)
    ap.add_argument("--artifacts-out", required=True)
    args = ap.parse_args()

    recdir = args.records_dir
    if not os.path.isdir(recdir):
        print(f"assemble-digest: records dir {recdir} missing", file=sys.stderr)
        return 3

    jobs, artifacts = [], []
    kernel_legs = manager_recs = bad_recs = 0
    for fn in sorted(os.listdir(recdir)):
        path = os.path.join(recdir, fn)
        if not fn.endswith(".json") or not os.path.isfile(path):
            continue
        try:
            with open(path) as fh:
                rec = json.load(fh)
        except (OSError, ValueError) as exc:
            bad_recs += 1
            print(f"assemble-digest: unreadable record {fn}: {exc}",
                  file=sys.stderr)
            continue
        if not isinstance(rec, dict):
            bad_recs += 1
            continue

        kind = rec.get("kind")
        if kind == "kernel-leg":
            root_id = str(rec.get("root_id", "none"))
            label = ROOT_LABELS.get(root_id, root_id)
            name = (
                f"{rec.get('family', 'unknown')} "
                f"({root_id}, {label}, {rec.get('root_commit', 'none')}) / "
                f"{rec.get('tag', '0.0.0-unknown')} ({rec.get('flavor', 'unknown')})"
            )
            jobs.append({"name": name,
                         "conclusion": rec.get("conclusion", "failure")})
            kernel_legs += 1
            art_id = str(rec.get("artifact_id", "")).strip()
            art_name = str(rec.get("artifact_name", "")).strip()
            if art_id and art_id != "None" and art_name:
                artifacts.append({"name": art_name, "id": art_id})
        elif kind == "helper":
            root_id = str(rec.get("root_id", "none"))
            label = ROOT_LABELS.get(root_id, root_id)
            name = (
                f"{rec.get('family', 'unknown')} "
                f"({root_id}, {label}, {rec.get('root_commit', 'none')}) / "
                f"{rec.get('helper', 'helper')}"
            )
            jobs.append({"name": name,
                         "conclusion": rec.get("conclusion", "failure")})
        elif kind == "manager":
            art_id = str(rec.get("artifact_id", "")).strip()
            art_name = str(rec.get("artifact_name", "")).strip()
            if art_id and art_name:
                artifacts.append({"name": art_name, "id": art_id})
                manager_recs += 1
        else:
            bad_recs += 1
            print(f"assemble-digest: unknown record kind in {fn}: {kind!r}",
                  file=sys.stderr)

    print(f"assemble-digest: {kernel_legs} kernel legs, "
          f"{manager_recs} manager records, {bad_recs} bad -> "
          f"{len(jobs)} jobs, {len(artifacts)} artifacts")

    if not jobs:
        # Nothing assembled (e.g. download step found no records because the
        # run predates self-reporting). Signal the caller to use the REST
        # fallback rather than posting an empty "everything failed" digest.
        return 3

    with open(args.jobs_out, "w") as fh:
        json.dump(jobs, fh)
    with open(args.artifacts_out, "w") as fh:
        json.dump(artifacts, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
