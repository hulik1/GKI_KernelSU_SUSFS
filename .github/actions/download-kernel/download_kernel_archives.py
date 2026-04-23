import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen
import hashlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--android-version", required=True)
    parser.add_argument("--kernel-version", required=True)
    parser.add_argument("--os-patch-level", required=True)
    return parser.parse_args()


def write_github_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")


def main() -> int:
    args = parse_args()

    formatted_branch = f"{args.android_version}-{args.kernel_version}-{args.os_patch_level}"
    manifest_branch = f"common-{formatted_branch}"
    manifest_ref = f"refs/heads/{manifest_branch}"
    manifest_base = f"https://android.googlesource.com/kernel/manifest/+/{manifest_ref}/"
    manifest_origin = f"{urllib.parse.urlparse(manifest_base).scheme}://{urllib.parse.urlparse(manifest_base).netloc}"

    target_repo = os.environ.get("GITHUB_REPOSITORY", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")

    toolchain_map = {
        "clang/host/linux-x86": "clang",
        "prebuilts/rust": "rust",
        "prebuilts/clang-tools": "clang-tools",
        "platform/prebuilts/build-tools": "build-tools",
        "kernel/prebuilts/build-tools": "kernel-build-tools",
        "platform/prebuilts/bazel/linux-x86_64": "bazel-linux-x86_64",
        "platform/prebuilts/jdk/jdk11": "jdk11",
        "toolchain/prebuilts/ndk/r23": "ndk-r23",
        "platform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8": "gcc-glibc2.17-4.8",
    }

    release_assets_lock = threading.Lock()
    release_assets_cache: list[dict[str, Any]] | None = None
    release_info_lock = threading.Lock()
    release_info_cache: dict[str, Any] | None = None
    upload_locks_guard = threading.Lock()
    upload_locks: dict[tuple[str, str], threading.Lock] = {}

    def is_deprecated_branch(branch: str) -> bool:
        try:
            out = subprocess.check_output(
                ["git", "ls-remote", "https://android.googlesource.com/kernel/common", branch],
                text=True,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            return "deprecated" in out
        except Exception:
            return False

    deprecated = is_deprecated_branch(formatted_branch)
    write_github_output("deprecated", str(deprecated).lower())
    print(f"Manifest branch: {manifest_branch}")
    print(f"Deprecated: {deprecated}")

    def fetch_gitiles_file_text(file_name: str) -> str:
        url = f"{manifest_base}{file_name}?format=TEXT"
        req = Request(url, headers={"User-Agent": "actions-download-kernel"})
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
        decoded = base64.b64decode(data)
        text = decoded.decode("utf-8", errors="replace")
        if deprecated:
            text = text.replace(f"\"{formatted_branch}\"", f"\"deprecated/{formatted_branch}\"")
        return text

    def load_manifest_with_includes(entry_file: str) -> tuple[ET.Element, list[tuple[str, ET.Element]]]:
        seen_files: set[str] = set()
        to_process = [entry_file]

        combined = ET.Element("manifest")
        combined_default: ET.Element | None = None
        combined_remotes: dict[str, ET.Element] = {}

        projects: list[ET.Element] = []
        link_copy: list[tuple[str, ET.Element]] = []

        while to_process:
            file_name = to_process.pop()
            if file_name in seen_files:
                continue
            seen_files.add(file_name)

            xml_text = fetch_gitiles_file_text(file_name)
            root = ET.fromstring(xml_text)

            for include in root.findall("include"):
                inc_name = include.get("name")
                if inc_name:
                    to_process.append(inc_name)

            for remote in root.findall("remote"):
                remote_name = remote.get("name")
                if remote_name and remote_name not in combined_remotes:
                    combined_remotes[remote_name] = remote

            if combined_default is None:
                d = root.find("default")
                if d is not None:
                    combined_default = d

            for project in root.findall("project"):
                projects.append(project)
                path = project.get("path", project.get("name") or "")
                for child in list(project):
                    if child.tag in ("linkfile", "copyfile"):
                        link_copy.append((path, child))

        for r in combined_remotes.values():
            combined.append(r)
        if combined_default is not None:
            combined.append(combined_default)
        for p in projects:
            combined.append(p)

        return combined, link_copy

    manifest_root, link_copy = load_manifest_with_includes("default.xml")

    def resolve_remote_fetch(fetch: str) -> str:
        fetch = fetch.strip()
        if fetch.startswith("https://") or fetch.startswith("http://"):
            return fetch.rstrip("/")
        base = f"{manifest_origin}/"
        resolved = urllib.parse.urljoin(base, f"{fetch.rstrip('/')}/")
        return resolved.rstrip("/")

    remotes = {
        r.get("name"): resolve_remote_fetch(r.get("fetch") or "")
        for r in manifest_root.findall("remote")
        if r.get("name") and r.get("fetch") is not None
    }
    default = manifest_root.find("default")
    def_remote = default.get("remote") if default is not None else None
    def_rev = default.get("revision") if default is not None else None

    def get_toolchain_label(project_name: str) -> str | None:
        for key, value in toolchain_map.items():
            if key in project_name:
                return value
        return None

    def github_api_get_json(url: str) -> object:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "actions-download-kernel",
        }
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        req = Request(url, headers=headers)
        with urlopen(req, timeout=60) as resp:
            data = resp.read()
        return json.loads(data.decode("utf-8", errors="replace"))

    def github_api_post_json(url: str, payload: dict[str, Any]) -> object:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "actions-download-kernel",
            "Content-Type": "application/json",
        }
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, headers=headers, data=data, method="POST")
        with urlopen(req, timeout=60) as resp:
            body = resp.read()
        return json.loads(body.decode("utf-8", errors="replace"))

    def get_toolchain_release_assets() -> list[dict[str, Any]]:
        nonlocal release_assets_cache
        with release_assets_lock:
            if release_assets_cache is not None:
                return release_assets_cache

        if not target_repo:
            with release_assets_lock:
                release_assets_cache = []
                return release_assets_cache

        assets: list[dict[str, Any]] = []
        url = f"https://api.github.com/repos/{target_repo}/releases?per_page=100"
        try:
            releases = github_api_get_json(url)
            if isinstance(releases, list):
                release = next(
                    (
                        r
                        for r in releases
                        if isinstance(r, dict)
                        and (r.get("name") == "Toolchains Mirror Cache" or r.get("tag_name") == "toolchain-cache")
                    ),
                    None,
                )
                if isinstance(release, dict):
                    raw_assets = release.get("assets", [])
                    assets = raw_assets if isinstance(raw_assets, list) else []
        except Exception:
            assets = []

        if not assets and github_token:
            release = get_or_create_toolchain_release()
            if isinstance(release, dict):
                raw_assets = release.get("assets", [])
                assets = raw_assets if isinstance(raw_assets, list) else []

        with release_assets_lock:
            release_assets_cache = assets
            return release_assets_cache

    def get_or_create_toolchain_release() -> dict[str, Any] | None:
        nonlocal release_info_cache, release_assets_cache
        with release_info_lock:
            if release_info_cache is not None:
                return release_info_cache
            if not target_repo or not github_token:
                release_info_cache = None
                return release_info_cache

            try:
                url = f"https://api.github.com/repos/{target_repo}/releases/tags/toolchain-cache"
                release = github_api_get_json(url)
                if isinstance(release, dict):
                    release_info_cache = release
                    assets = release.get("assets", [])
                    with release_assets_lock:
                        release_assets_cache = assets if isinstance(assets, list) else []
                    return release_info_cache
            except Exception:
                pass

            try:
                create_url = f"https://api.github.com/repos/{target_repo}/releases"
                release = github_api_post_json(
                    create_url,
                    {
                        "tag_name": "toolchain-cache",
                        "name": "Toolchains Mirror Cache",
                        "draft": False,
                        "prerelease": False,
                    },
                )
                if isinstance(release, dict):
                    release_info_cache = release
                    assets = release.get("assets", [])
                    with release_assets_lock:
                        release_assets_cache = assets if isinstance(assets, list) else []
                    return release_info_cache
            except Exception:
                try:
                    url = f"https://api.github.com/repos/{target_repo}/releases/tags/toolchain-cache"
                    release = github_api_get_json(url)
                    if isinstance(release, dict):
                        release_info_cache = release
                        assets = release.get("assets", [])
                        with release_assets_lock:
                            release_assets_cache = assets if isinstance(assets, list) else []
                        return release_info_cache
                except Exception:
                    release_info_cache = None
                    return release_info_cache

            release_info_cache = None
            return release_info_cache

    def download_github_release_asset(api_url: str, out_path: str) -> None:
        headers = {
            "Accept": "application/octet-stream",
            "User-Agent": "actions-download-kernel",
        }
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        req = Request(api_url, headers=headers)
        with urlopen(req, timeout=120) as resp, open(out_path, "wb") as f:
            shutil.copyfileobj(resp, f, length=1024 * 1024)

    def run_curl_download(url: str, out_path: str) -> None:
        subprocess.run(
            ["curl", "-LfsS", "--retry", "5", "--connect-timeout", "30", "-o", out_path, url],
            check=True,
            text=True,
        )

    def extract_tar_gz(archive_path: str, dest_dir: str, strip_components: int) -> None:
        cmd = ["tar", "-xzf", archive_path, "-C", dest_dir]
        if strip_components > 0:
            cmd.extend(["--strip-components", str(strip_components)])
        subprocess.run(cmd, check=True, text=True)

    def upload_release_asset(upload_url_template: str, file_path: str, asset_name: str) -> None:
        upload_url = upload_url_template.split("{", 1)[0]
        url = f"{upload_url}?name={urllib.parse.quote(asset_name, safe='')}"

        tmp_fd, tmp_resp = tempfile.mkstemp(prefix="gh-release-upload-", suffix=".json")
        os.close(tmp_fd)
        cmd = [
            "curl",
            "-LsS",
            "-X",
            "POST",
            "-H",
            "Accept: application/vnd.github.v3+json",
            "-H",
            "Content-Type: application/octet-stream",
            "-H",
            "User-Agent: actions-download-kernel",
            "-o",
            tmp_resp,
            "-w",
            "%{http_code}",
        ]
        if github_token:
            cmd.extend(["-H", f"Authorization: token {github_token}"])
        cmd.extend(["--data-binary", f"@{file_path}", url])

        try:
            res = subprocess.run(cmd, check=True, text=True, capture_output=True)
            code = (res.stdout or "").strip()
            if code in {"200", "201"}:
                return
            if code == "422":
                return
            body = ""
            try:
                with open(tmp_resp, "r", encoding="utf-8", errors="replace") as f:
                    body = f.read()
            except Exception:
                body = ""
            raise RuntimeError(f"Release asset upload failed (HTTP {code}): {body}")
        finally:
            if os.path.exists(tmp_resp):
                os.remove(tmp_resp)

    def build_release_asset_index() -> dict[str, dict[str, Any]]:
        assets = get_toolchain_release_assets()
        index: dict[str, dict[str, Any]] = {}
        for a in assets:
            if isinstance(a, dict) and isinstance(a.get("name"), str):
                index[a["name"]] = a
        return index

    def sha256_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def ensure_toolchain_cached(label: str, rev: str, src_dir: str) -> None:
        nonlocal release_assets_cache
        if not github_token or not target_repo:
            return

        cache_key = (label, rev)
        with upload_locks_guard:
            lock = upload_locks.get(cache_key)
            if lock is None:
                lock = threading.Lock()
                upload_locks[cache_key] = lock

        with lock:
            try:
                base_filename = f"{label}-{rev}.tar.gz"
                meta_name = f"{label}-{rev}.cache.json"
                asset_index = build_release_asset_index()
                if meta_name in asset_index:
                    return

                release = get_or_create_toolchain_release()
                if not release:
                    return
                upload_url_template = release.get("upload_url")
                if not isinstance(upload_url_template, str) or not upload_url_template:
                    return

                tmp_dir = tempfile.mkdtemp(prefix="toolchain-cache-")
                try:
                    archive_path = os.path.join(tmp_dir, base_filename)
                    subprocess.run(
                        ["tar", "-I", "gzip -1", "-cf", archive_path, "-C", src_dir, "."],
                        check=True,
                        text=True,
                    )

                    size = os.path.getsize(archive_path)
                    max_part = 1900 * 1024 * 1024

                    meta: dict[str, Any] = {
                        "format": 1,
                        "label": label,
                        "rev": rev,
                        "archive": base_filename,
                        "parts": [],
                    }

                    if size <= max_part:
                        upload_release_asset(upload_url_template, archive_path, base_filename)
                        meta["parts"].append(
                            {
                                "name": base_filename,
                                "size": size,
                                "sha256": sha256_file(archive_path),
                            }
                        )
                    else:
                        subprocess.run(
                            ["split", "-b", str(max_part), "-d", "-a", "2", archive_path, f"{archive_path}.part"],
                            check=True,
                            text=True,
                        )
                        for name in sorted(os.listdir(tmp_dir)):
                            if name.startswith(f"{base_filename}.part"):
                                part_path = os.path.join(tmp_dir, name)
                                upload_release_asset(upload_url_template, part_path, name)
                                meta["parts"].append(
                                    {
                                        "name": name,
                                        "size": os.path.getsize(part_path),
                                        "sha256": sha256_file(part_path),
                                    }
                                )

                    meta_path = os.path.join(tmp_dir, meta_name)
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump(meta, f, separators=(",", ":"))
                    upload_release_asset(upload_url_template, meta_path, meta_name)

                    with release_assets_lock:
                        release_assets_cache = None
                finally:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                return

    def try_extract_toolchain_cache(project_name: str, rev: str, dest_dir: str, strip_components: int) -> bool:
        label = get_toolchain_label(project_name)
        if not label:
            return False

        asset_index = build_release_asset_index()

        base_filename = f"{label}-{rev}.tar.gz"
        meta_name = f"{label}-{rev}.cache.json"
        matching: list[tuple[str, str]] = []

        if meta_name in asset_index and isinstance(asset_index[meta_name].get("url"), str):
            tmp_fd, tmp_meta = tempfile.mkstemp(prefix="toolchain-cache-", suffix=".json")
            os.close(tmp_fd)
            try:
                download_github_release_asset(asset_index[meta_name]["url"], tmp_meta)
                with open(tmp_meta, "r", encoding="utf-8", errors="replace") as f:
                    meta = json.load(f)
                parts = meta.get("parts", [])
                if not isinstance(parts, list) or not parts:
                    return False
                for p in parts:
                    if not isinstance(p, dict):
                        continue
                    name = p.get("name")
                    if isinstance(name, str) and name in asset_index and isinstance(asset_index[name].get("url"), str):
                        matching.append((name, asset_index[name]["url"]))
                if not matching:
                    return False
            finally:
                if os.path.exists(tmp_meta):
                    os.remove(tmp_meta)
        else:
            for asset_name, a in asset_index.items():
                asset_url = a.get("url")
                if isinstance(asset_url, str) and asset_name.startswith(base_filename):
                    matching.append((asset_name, asset_url))

        if not matching:
            return False

        matching.sort(key=lambda x: x[0])
        part_paths: list[str] = []
        try:
            for asset_name, asset_url in matching:
                part_path = os.path.abspath(asset_name)
                download_github_release_asset(asset_url, part_path)
                part_paths.append(part_path)

            if len(part_paths) == 1 and part_paths[0].endswith(".tar.gz"):
                extract_tar_gz(part_paths[0], dest_dir, strip_components)
            else:
                tmp_fd, tmp_path = tempfile.mkstemp(prefix="toolchain-", suffix=".tar.gz")
                os.close(tmp_fd)
                try:
                    with open(tmp_path, "wb") as out_f:
                        for p in part_paths:
                            with open(p, "rb") as in_f:
                                shutil.copyfileobj(in_f, out_f, length=1024 * 1024)
                    extract_tar_gz(tmp_path, dest_dir, strip_components)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            return True
        except Exception:
            return False
        finally:
            for p in part_paths:
                if os.path.exists(p):
                    os.remove(p)

    def url_quote_rev(rev: str) -> str:
        return urllib.parse.quote(rev, safe="")

    def googlesource_archive_urls(repo_url: str, rev: str) -> list[str]:
        qrev = url_quote_rev(rev)
        if rev.startswith("refs/"):
            return [f"{repo_url}/+archive/{qrev}.tar.gz"]
        return [
            f"{repo_url}/+archive/{url_quote_rev(f'refs/heads/{rev}')}.tar.gz",
            f"{repo_url}/+archive/{url_quote_rev(f'refs/tags/{rev}')}.tar.gz",
            f"{repo_url}/+archive/{qrev}.tar.gz",
        ]

    def github_archive_urls(repo_url: str, rev: str) -> list[str]:
        if rev.startswith("refs/"):
            return [f"{repo_url}/archive/{rev}.tar.gz"]
        return [
            f"{repo_url}/archive/refs/heads/{rev}.tar.gz",
            f"{repo_url}/archive/refs/tags/{rev}.tar.gz",
            f"{repo_url}/archive/{rev}.tar.gz",
        ]

    def gitlab_archive_urls(repo_url: str, rev: str, repo_basename: str) -> list[str]:
        qrev = urllib.parse.quote(rev, safe="")
        return [f"{repo_url}/-/archive/{qrev}/{repo_basename}-{qrev}.tar.gz"]

    def build_project_urls(base_url: str, name: str, rev: str) -> tuple[list[str], int]:
        repo_url = f"{base_url}/{name}"

        if "github.com" in base_url:
            return github_archive_urls(repo_url, rev), 1

        if "googlesource.com" in base_url or "android.googlesource.com" in base_url:
            return googlesource_archive_urls(repo_url, rev), 0

        if "git.codelinaro.org" in base_url or "gitlab" in base_url:
            repo_basename = name.rstrip("/").split("/")[-1]
            return gitlab_archive_urls(repo_url, rev, repo_basename), 1

        return [], 0

    def sync_project(task: tuple[str, str, str, str]) -> dict[str, Any]:
        name, path, rev, base_url = task
        start_time = time.time()
        dest_dir = os.path.abspath(path if path not in ("./", ".") else ".")
        os.makedirs(dest_dir, exist_ok=True)

        try:
            urls, strip_components = build_project_urls(base_url, name, rev)
            if not urls:
                return {
                    "ok": False,
                    "name": name,
                    "path": path,
                    "rev": rev,
                    "base_url": base_url,
                    "error": "no supported remote",
                    "urls": [],
                }

            if try_extract_toolchain_cache(name, rev, dest_dir, strip_components):
                duration = time.time() - start_time
                print(f"Synced {name} -> {path} ({duration:.2f}s)")
                return {"ok": True}

            tmp_fd, tmp_path = tempfile.mkstemp(prefix="kernel-src-", suffix=".tar.gz")
            os.close(tmp_fd)
            try:
                last_err: str | None = None
                for url in urls:
                    try:
                        run_curl_download(url, tmp_path)
                        extract_tar_gz(tmp_path, dest_dir, strip_components)
                        label = get_toolchain_label(name)
                        if label:
                            ensure_toolchain_cached(label, rev, dest_dir)
                        duration = time.time() - start_time
                        print(f"Synced {name} -> {path} ({duration:.2f}s)")
                        return {"ok": True}
                    except subprocess.CalledProcessError as e:
                        last_err = str(e)
                        continue

                return {
                    "ok": False,
                    "name": name,
                    "path": path,
                    "rev": rev,
                    "base_url": base_url,
                    "error": last_err or "download/extract failed",
                    "urls": urls,
                }
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            return {
                "ok": False,
                "name": name,
                "path": path,
                "rev": rev,
                "base_url": base_url,
                "error": f"unexpected exception: {e}",
                "urls": [],
            }

    def ensure_build_tools_python(kernel_root: str) -> None:
        build_tools_dir = os.path.join(kernel_root, "prebuilts", "build-tools")
        expected = os.path.join(build_tools_dir, "path", "linux-x86", "python3")
        if os.path.exists(expected):
            return

        os.makedirs(os.path.dirname(expected), exist_ok=True)

        candidate: str | None = None
        for root_dir, _, files in os.walk(build_tools_dir):
            if "python3" in files:
                candidate = os.path.join(root_dir, "python3")
                break

        if candidate is None:
            candidate = shutil.which("python3") or "/usr/bin/python3"

        try:
            if os.path.lexists(expected):
                os.remove(expected)
            rel_target = os.path.relpath(candidate, os.path.dirname(expected))
            os.symlink(rel_target, expected)
        except Exception:
            return

    sync_tasks: list[tuple[str, str, str, str]] = []
    for project in manifest_root.findall("project"):
        name = project.get("name")
        if not name:
            continue
        path = project.get("path", name)
        remote_name = project.get("remote", def_remote)
        if not remote_name:
            continue
        base_url = remotes.get(remote_name)
        if not base_url:
            continue
        rev = project.get("revision", def_rev)
        if not rev:
            continue
        sync_tasks.append((name, path, rev, base_url))

    max_workers = min(32, (os.cpu_count() or 2) * 2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results: list[dict[str, Any]] = list(executor.map(sync_project, sync_tasks))

    failed = [r for r in results if not r.get("ok")]
    if failed:
        for r in failed[:25]:
            print(
                f"[FAIL] {r.get('name')} -> {r.get('path')} rev={r.get('rev')} remote={r.get('base_url')} err={r.get('error')}"
            )
            for u in (r.get("urls") or [])[:5]:
                print(f"       url={u}")
        return 1

    ensure_build_tools_python(os.getcwd())

    for project_path, child in link_copy:
        src_rel = child.get("src")
        dest_rel = child.get("dest")
        if not src_rel or not dest_rel:
            continue

        src_path = os.path.join(os.getcwd(), project_path, src_rel)
        dest_path = os.path.join(os.getcwd(), dest_rel)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if child.tag == "linkfile":
            if os.path.lexists(dest_path):
                os.remove(dest_path)
            rel_target = os.path.relpath(src_path, os.path.dirname(dest_path))
            os.symlink(rel_target, dest_path)
        elif child.tag == "copyfile":
            shutil.copy2(src_path, dest_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
