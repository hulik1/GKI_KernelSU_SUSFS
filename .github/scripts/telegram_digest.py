#!/usr/bin/env python3
"""Build per-family Telegram digest messages from a workflow run's jobs.

Input : the run's jobs JSON (actions API, all pages merged) on stdin.
Output: one line per kernel family, TAB-separated:  <topic_id>\t<html>
        The caller posts each line to that topic via sendMessage.

Routing (topic IDs in the Wild Kernels Testing forum, editable in place):
  build-android12-5-10 -> 3   (5.10.x-android12)
  build-android13-5-10 -> 5   (5.10.x-android13)
  build-android13-5-15 -> 7   (5.15.x-android13; shares the 5.15 topic)
  build-android14-5-15 -> 7   (5.15.x-android14)
  build-android14-6-1  -> 9   (6.1.x-android14)
  build-android15-6-6  -> 13  (6.6.x-android15)
  build-android16-6-12 -> 15  (6.12.x-android16, incl. the lts sublevel)
  build-android17-6-18 -> 17  (6.18.x-android17, placeholder family)
Unmapped families fall back to topic 3 so nothing is silently dropped.

Job names for callable-workflow runs look like:
  build-android15-6-6 (next, KernelSU-Next, 956ea0f5...) / build (...) / 6.6.82-android15-2025-04 (KernelSU-Next)
The first segment identifies the family job; the last carries the
sublevel/os tag and the root flavor.

Usage: telegram_digest.py --run-id ID --branch BR --event EV
                          --run-url URL --nightly-url URL < jobs.json
"""
import argparse
import html
import json
import sys

TOPICS = {
    "build-android12-5-10": "3",
    "build-android13-5-10": "5",
    "build-android13-5-15": "7",
    "build-android14-5-15": "7",
    "build-android14-6-1": "9",
    "build-android15-6-6": "13",
    "build-android16-6-12": "15",
    "build-android17-6-18": "17",
}
FALLBACK_TOPIC = "3"

# Excluded helper jobs that share the build- prefix
EXCLUDED = {"build-nomount-module"}

FAMILY_NAMES = {
    "build-android12-5-10": "5.10.x-android12",
    "build-android13-5-10": "5.10.x-android13",
    "build-android13-5-15": "5.15.x-android13",
    "build-android14-5-15": "5.15.x-android14",
    "build-android14-6-1": "6.1.x-android14",
    "build-android15-6-6": "6.6.x-android15",
    "build-android16-6-12": "6.12.x-android16",
    "build-android17-6-18": "6.18.x-android17",
}

MARKS = {"success": "✅", "failure": "❌", "cancelled": "⛔",
         "skipped": "⏭️", "startup_failure": "❌"}

MAX_LEN = 4000  # Telegram cap is 4096; leave headroom for entities

# Flavor -> manager APK artifact patterns (fnmatch against the run's
# uploaded artifact names; first non-excluded match wins per entry).
# ReSukiSU's manager is the BakaSU rebrand. KernelSU-Next ships a spoofed
# variant: the stock manager links the flavor name, the spoofed one gets
# a suffix link.
FLAVOR_MANAGERS = {
    "KernelSU": [("KernelSU_v*", None)],
    "KernelSU-Next": [("KernelSU_Next_v*", "spoofed"),
                      ("KernelSU_Next_v*spoofed*", None)],
    "ReSukiSU": [("BakaSU_v*", None), ("ReSukiSU_v*", None)],
}


def load_json_any(stream) -> list:
    """Accept a single JSON object/array OR gh api --paginate's
    concatenated pages; merge every list found under common keys
    ('jobs', 'artifacts') or a bare top-level array."""
    text = stream.read()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for key in ("jobs", "artifacts"):
                if isinstance(data.get(key), list):
                    return data[key]
            return []
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        pass
    dec = json.JSONDecoder()
    items, idx, n = [], 0, len(text)
    while idx < n:
        while idx < n and text[idx] in " \t\r\n":
            idx += 1
        if idx >= n:
            break
        obj, end = dec.raw_decode(text, idx)
        idx = end
        if isinstance(obj, dict):
            for key in ("jobs", "artifacts"):
                if isinstance(obj.get(key), list):
                    items.extend(obj[key])
        elif isinstance(obj, list):
            items.extend(obj)
    return items


def family_of(job_name: str) -> str:
    return job_name.split(" / ")[0].split(" (")[0].strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--event", required=True)
    ap.add_argument("--run-url", required=True)
    ap.add_argument("--nightly-url", required=True)
    ap.add_argument("--artifacts-file", default="",
                    help="JSON (single object or concatenated pages) of the "
                         "run's artifacts; enables per-flavor manager links")
    ap.add_argument("--test-chat", default="",
                    help="second chat (testing release group) that gets one "
                         "combined 'new testing release' card")
    ap.add_argument("--test-topic", default="",
                    help="forum topic inside --test-chat for that card")
    ap.add_argument("--chat-id", required=True,
                    help="main announcements chat (per-family digests)")
    args = ap.parse_args()

    artifacts = []
    if args.artifacts_file:
        try:
            with open(args.artifacts_file) as fh:
                artifacts = load_json_any(fh)
        except (OSError, ValueError) as exc:
            print(f"telegram-digest: artifacts parse failed ({exc}); "
                  f"flavor links disabled", file=sys.stderr)
            artifacts = []

    def manager_links(flavor: str) -> list:
        """nightly.link deep links to this flavor's manager APK artifacts.

        Links go by artifact ID (/{repo}/actions/artifacts/{id}.zip) - the
        by-name route can't match names containing dots (every .apk artifact
        404s there), and manager artifacts keep their versioned names.
        """
        import fnmatch
        by_name = {}
        for a in artifacts:
            if "name" in a and "id" in a:
                by_name.setdefault(a["name"], a["id"])
        names = sorted(by_name)
        urls = []
        for pat, excl in FLAVOR_MANAGERS.get(flavor, []):
            for n in names:
                if fnmatch.fnmatch(n, pat) and (not excl or excl not in n):
                    urls.append(
                        f"{args.nightly_url.rsplit('/actions/runs/', 1)[0]}"
                        f"/actions/artifacts/{by_name[n]}.zip")
                    break
        return urls

    data = load_json_any(sys.stdin)
    jobs = data if isinstance(data, list) else []
    if not jobs:
        print("telegram-digest: no jobs in input", file=sys.stderr)
        return 1

    fams = {}
    for j in jobs:
        name = j.get("name") or ""
        fam = family_of(name)
        if not fam.startswith("build-android") or fam in EXCLUDED:
            continue  # resolve-sources, nomount, rej, release, ...
        e = fams.setdefault(fam, {"sublevels": [], "flavors": [],
                                  "counts": {}, "sub_jobs": {}})
        last = name.split(" / ")[-1]
        if " / " in name and "(" in last:
            tag = last.rsplit(" (", 1)[0]
            flavor = last.rsplit(" (", 1)[1].rstrip(")")
            if tag and tag not in e["sublevels"]:
                e["sublevels"].append(tag)
            if flavor and flavor not in e["flavors"]:
                e["flavors"].append(flavor)
            sj = e["sub_jobs"].setdefault(tag, {})
            c = j.get("conclusion") or j.get("status") or "unknown"
            sj[c] = sj.get(c, 0) + 1
        c = j.get("conclusion") or j.get("status") or "unknown"
        e["counts"][c] = e["counts"].get(c, 0) + 1

    # A family whose every job was skipped (single-family dispatch gates
    # the rest off) carries no information - drop it instead of posting
    # an empty card into its topic.
    fams = {f: e for f, e in fams.items()
            if any(k != "skipped" for k in e["counts"])}

    icon = "🌙" if args.event == "schedule" else "🔨"
    for fam, e in sorted(fams.items()):
        topic = TOPICS.get(fam, FALLBACK_TOPIC)
        fname = FAMILY_NAMES.get(fam, fam)
        esc = html.escape

        counts = "  ".join(f"{MARKS.get(k, '•')} {v}"
                           for k, v in sorted(e["counts"].items()))

        # Numeric sort: sublevel then os date ("6.6.102-...-2025-10" AFTER
        # "6.6.118-...-2026-01"? No - 118 > 102, and 2026 > 2025). Lexicographic
        # puts 6.6.102 before 6.6.30 - wrong. X (lts) sorts last.
        def sub_key(tag: str):
            parts = tag.split("-")
            sub = parts[2] if len(parts) >= 3 else "0"
            sub_num = 10 ** 9 if sub.upper() == "X" else \
                int("".join(ch for ch in sub if ch.isdigit()) or 0)
            date_num = 0
            for p in parts[3:]:
                digits = "".join(ch for ch in p if ch.isdigit())
                date_num = date_num * 10000 + (int(digits) if digits else 0)
            return (sub_num, date_num, tag)

        subs = sorted(e["sublevels"], key=sub_key)

        # Per-sublevel lines: passing sublevels link their AnyKernel3
        # artifact (KernelSU-Next preferred, then KernelSU, then ReSukiSU);
        # sublevels with any failed/cancelled job get a ❌ mark and no link.
        art_base = args.nightly_url.rsplit("/actions/runs/", 1)[0]
        sub_lines = []
        for s in subs:
            sj = e["sub_jobs"].get(s, {})
            bad = sj.get("failure", 0) + sj.get("cancelled", 0) + \
                sj.get("startup_failure", 0)
            if bad:
                sub_lines.append(f"- ❌ {esc(s)}")
                continue
            link_id = None
            for fl in ("KernelSU-Next", "KernelSU", "ReSukiSU"):
                art_name = f"{s}-{fl}-AnyKernel3"
                for a in artifacts:
                    if a.get("name") == art_name and "id" in a:
                        link_id = a["id"]
                        break
                if link_id:
                    break
            if link_id:
                url = f"{art_base}/actions/artifacts/{link_id}.zip"
                sub_lines.append(f"- <a href=\"{html.escape(url, quote=True)}\">"
                                 f"{esc(s)}</a>")
            else:
                sub_lines.append(f"- {esc(s)}")
        sub_text = "\n".join(sub_lines) if sub_lines else "—"

        # Flavors, each linking its manager APK when the run uploaded one.
        # The flavor name links the stock manager; KernelSU-Next gets a
        # trailing "spoofed" link for its second variant.
        flines = []
        for f in sorted(e["flavors"]):
            links = manager_links(f)
            if not links:
                flines.append(esc(f))
                continue
            line = f"<a href=\"{html.escape(links[0], quote=True)}\">" \
                   f"{esc(f)}</a>"
            if len(links) > 1:
                line += "  ·  " + "  ·  ".join(
                    f"<a href=\"{html.escape(u, quote=True)}\">spoofed</a>"
                    for u in links[1:])
            flines.append(line)
        flavors = "\n".join(flines) if flines else "—"

        msg = (
            f"<b>{icon} Wild Kernels</b>\n"
            f"\n"
            f"<b>{esc(fname)}</b>\n"
            f"\n"
            f"<b>Branch</b>: <code>{esc(args.branch)}</code>\n"
            f"<b>Trigger</b>: {esc(args.event)}\n"
            f"<b>Run</b>: <a href=\"{esc(args.run_url)}\">#{args.run_id}</a>\n"
            f"\n"
            f"<b>Sublevels</b>:\n"
            f"{sub_lines}\n"
            f"\n"
            f"<b>Flavors</b>:\n"
            f"{flavors}\n"
            f"\n"
            f"<b>Jobs</b>: {counts}\n"
            f"\n"
            f"<b>Download</b>:\n"
            f"<a href=\"{esc(args.nightly_url)}\">nightly.link — all artifacts</a>"
        )
        if len(msg) > MAX_LEN:
            msg = msg[:MAX_LEN - 1] + "…"
        # Records: CHAT \t TOPIC \t HTML, separated by ASCII RS (\x1e): the
        # HTML itself is multi-line, so the caller splits on RS and reads
        # the three fields in order.
        print(f"{args.chat_id}\t{topic}\t{msg}", end="\x1e")

    # Combined "new testing release" card for the testing group: one
    # message listing every family built in this run with its manager
    # links and the shared download link.
    if args.test_chat and args.test_topic and fams:
        esc = html.escape
        sections = []
        for fam, e in sorted(fams.items()):
            fname = FAMILY_NAMES.get(fam, fam)
            counts = "  ".join(f"{MARKS.get(k, '•')} {v}"
                               for k, v in sorted(e["counts"].items()))
            ml = []
            for f in sorted(e["flavors"]):
                links = manager_links(f)
                if links:
                    ml.append(f"<a href=\"{html.escape(links[0], quote=True)}\">"
                              f"{esc(f)}</a>")
                    for u in links[1:]:
                        ml.append(f"<a href=\"{html.escape(u, quote=True)}\">"
                                  f"spoofed</a>")
                else:
                    ml.append(esc(f))
            sections.append(
                f"<b>{esc(fname)}</b>  —  {counts}\n"
                + "  ·  ".join(ml))
        combined = (
            f"👋 <b>Hello, new testing release here:</b>\n"
            f"<b>{icon} Wild Kernels</b> — <code>{esc(args.branch)}</code>\n"
            f"<b>Run</b>: <a href=\"{esc(args.run_url)}\">#{args.run_id}</a>\n"
            f"\n"
            + "\n\n".join(sections) +
            f"\n\n"
            f"<b>Download everything</b>:\n"
            f"<a href=\"{esc(args.nightly_url)}\">nightly.link — all artifacts</a>"
        )
        if len(combined) > MAX_LEN:
            combined = combined[:MAX_LEN - 1] + "…"
        print(f"{args.test_chat}\t{args.test_topic}\t{combined}", end="\x1e")

    return 0


if __name__ == "__main__":
    sys.exit(main())
