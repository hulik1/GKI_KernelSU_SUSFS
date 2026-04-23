#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-all}"
shift || true
RUN_ALL=false

ANDROID_VERSION="${1:-${ANDROID_VERSION:-}}"
KERNEL_VERSION="${2:-${KERNEL_VERSION:-}}"
OS_PATCH_LEVEL="${3:-${OS_PATCH_LEVEL:-}}"

if [[ "$PHASE" == "prepare" || "$PHASE" == "all" ]]; then
  if [[ -z "$ANDROID_VERSION" || -z "$KERNEL_VERSION" || -z "$OS_PATCH_LEVEL" ]]; then
    echo "usage: $0 <prepare|parse|sync|post|all> <android_version> <kernel_version> <os_patch_level>" >&2
    exit 2
  fi
fi

require_env() {
  local key="$1"
  if [[ -z "${!key:-}" ]]; then
    echo "missing env: ${key}" >&2
    exit 2
  fi
}

fetch_gitiles_text() {
  local manifest_base="$1"
  local file_name="$2"
  curl -LfsS -H "User-Agent: actions-download-kernel" "${manifest_base}${file_name}?format=TEXT" | base64 -d
}

prepare_manifest() {
  local formatted_branch="${ANDROID_VERSION}-${KERNEL_VERSION}-${OS_PATCH_LEVEL}"
  local manifest_branch="common-${formatted_branch}"
  local manifest_ref="refs/heads/${manifest_branch}"
  local manifest_base="https://android.googlesource.com/kernel/manifest/+/${manifest_ref}/"

  local deprecated=false
  if git ls-remote https://android.googlesource.com/kernel/common "${formatted_branch}" 2>/dev/null | rg -q deprecated; then
    deprecated=true
  fi

  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    printf 'deprecated=%s\n' "$(echo "$deprecated" | tr '[:upper:]' '[:lower:]')" >> "$GITHUB_OUTPUT"
  fi

  echo "Manifest branch: ${manifest_branch}"
  echo "Deprecated: ${deprecated}"

  TMP_DIR="$(mktemp -d)"
  export TMP_DIR

  if [[ -n "${GITHUB_ENV:-}" ]]; then
    {
      echo "TMP_DIR=${TMP_DIR}"
      echo "ANDROID_VERSION=${ANDROID_VERSION}"
      echo "KERNEL_VERSION=${KERNEL_VERSION}"
      echo "OS_PATCH_LEVEL=${OS_PATCH_LEVEL}"
      echo "FORMATTED_BRANCH=${formatted_branch}"
      echo "MANIFEST_BRANCH=${manifest_branch}"
      echo "MANIFEST_REF=${manifest_ref}"
      echo "MANIFEST_BASE=${manifest_base}"
      echo "DEPRECATED=${deprecated}"
    } >> "$GITHUB_ENV"
  fi

  local manifest_xml
  manifest_xml="$(fetch_gitiles_text "${manifest_base}" default.xml)"
  if [[ "$deprecated" == "true" ]]; then
    manifest_xml="$(printf '%s' "$manifest_xml" | sed "s/\"${formatted_branch//\//\\/}\"/\"deprecated\\/${formatted_branch//\//\\/}\"/g")"
  fi
  printf '%s' "$manifest_xml" > "${TMP_DIR}/manifest.xml"
}

parse_manifest() {
  require_env TMP_DIR
  python3 - <<'PY' > "${TMP_DIR}/parsed.jsonl"
import json
import os
import urllib.parse
import xml.etree.ElementTree as ET

manifest_origin = "https://android.googlesource.com"

with open(os.path.join(os.environ["TMP_DIR"], "manifest.xml"), "r", encoding="utf-8", errors="replace") as f:
    root = ET.fromstring(f.read())

remotes = {}
for r in root.findall("remote"):
    name = r.get("name")
    fetch = (r.get("fetch") or "").strip()
    if not name or not fetch:
        continue
    if fetch.startswith("http://") or fetch.startswith("https://"):
        remotes[name] = fetch.rstrip("/")
    else:
        remotes[name] = urllib.parse.urljoin(manifest_origin + "/", fetch.rstrip("/") + "/").rstrip("/")

default = root.find("default")
def_remote = default.get("remote") if default is not None else None
def_rev = default.get("revision") if default is not None else None

projects = []
link_copy = []

for p in root.findall("project"):
    name = p.get("name")
    if not name:
        continue
    path = p.get("path", name)
    remote_name = p.get("remote", def_remote)
    rev = p.get("revision", def_rev)
    base_url = remotes.get(remote_name) if remote_name else None
    if not base_url or not rev:
        continue
    projects.append({"name": name, "path": path, "rev": rev, "base_url": base_url})
    for child in list(p):
        if child.tag in ("linkfile", "copyfile"):
            link_copy.append({"project_path": path, "tag": child.tag, "src": child.get("src"), "dest": child.get("dest")})

for prj in projects:
    print(json.dumps({"type": "project", **prj}, separators=(",", ":")))

for op in link_copy:
    print(json.dumps({"type": "op", **op}, separators=(",", ":")))
PY

  jq -r 'select(.type=="project") | [.name,.path,.rev,.base_url] | @tsv' "${TMP_DIR}/parsed.jsonl" > "${TMP_DIR}/projects.txt"
  jq -r 'select(.type=="op") | [.tag,.project_path,(.src//""),(.dest//"")] | @tsv' "${TMP_DIR}/parsed.jsonl" > "${TMP_DIR}/ops.txt"
}

if [[ "$PHASE" == "prepare" ]]; then
  prepare_manifest
  exit 0
fi

if [[ "$PHASE" == "parse" ]]; then
  parse_manifest
  exit 0
fi

if [[ "$PHASE" == "all" ]]; then
  prepare_manifest
  parse_manifest
  RUN_ALL=true
  PHASE="sync"
fi

require_env TMP_DIR

TARGET_REPO="${GITHUB_REPOSITORY:-}"
GITHUB_TOKEN_VALUE="${GITHUB_TOKEN:-}"

release_json="${TMP_DIR}/release.json"
assets_json="${TMP_DIR}/assets.json"

get_or_create_release() {
  if [[ -z "$TARGET_REPO" || -z "$GITHUB_TOKEN_VALUE" ]]; then
    return 1
  fi

  if curl -LfsS -H "Authorization: token ${GITHUB_TOKEN_VALUE}" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${TARGET_REPO}/releases/tags/toolchain-cache" > "$release_json"; then
    return 0
  fi

  curl -LfsS -X POST -H "Authorization: token ${GITHUB_TOKEN_VALUE}" -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    -d '{"tag_name":"toolchain-cache","name":"Toolchains Mirror Cache","draft":false,"prerelease":false}' \
    "https://api.github.com/repos/${TARGET_REPO}/releases" > "$release_json" || true

  curl -LfsS -H "Authorization: token ${GITHUB_TOKEN_VALUE}" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${TARGET_REPO}/releases/tags/toolchain-cache" > "$release_json"
}

refresh_assets() {
  if [[ -z "$TARGET_REPO" || -z "$GITHUB_TOKEN_VALUE" ]]; then
    printf '[]' > "$assets_json"
    return 0
  fi
  if ! curl -LfsS -H "Authorization: token ${GITHUB_TOKEN_VALUE}" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${TARGET_REPO}/releases/tags/toolchain-cache" > "$release_json"; then
    get_or_create_release || true
  fi
  jq -c '.assets // []' "$release_json" > "$assets_json" || printf '[]' > "$assets_json"
}

upload_asset() {
  local upload_url_template="$1"
  local file_path="$2"
  local asset_name="$3"
  local upload_url
  upload_url="${upload_url_template%%\{*}"
  local url="${upload_url}?name=$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("${asset_name}", safe=""))
PY
)"
  local http_code
  http_code="$(curl -LsS -X POST \
    -H "Authorization: token ${GITHUB_TOKEN_VALUE}" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/octet-stream" \
    -H "User-Agent: actions-download-kernel" \
    --data-binary "@${file_path}" \
    -o /dev/null -w "%{http_code}" \
    "$url" || true)"
  if [[ "$http_code" == "200" || "$http_code" == "201" || "$http_code" == "422" ]]; then
    return 0
  fi
  return 1
}

download_release_asset() {
  local api_url="$1"
  local out_path="$2"
  curl -LfsS \
    -H "Authorization: token ${GITHUB_TOKEN_VALUE}" \
    -H "Accept: application/octet-stream" \
    -H "User-Agent: actions-download-kernel" \
    "$api_url" -o "$out_path"
}

sha256_file() {
  sha256sum "$1" | awk '{print $1}'
}

toolchain_label_for() {
  local name="$1"
  if [[ "$name" == *"clang/host/linux-x86"* ]]; then echo "clang"; return 0; fi
  if [[ "$name" == *"prebuilts/rust"* ]]; then echo "rust"; return 0; fi
  if [[ "$name" == *"prebuilts/clang-tools"* ]]; then echo "clang-tools"; return 0; fi
  if [[ "$name" == *"platform/prebuilts/build-tools"* ]]; then echo "build-tools"; return 0; fi
  if [[ "$name" == *"kernel/prebuilts/build-tools"* ]]; then echo "kernel-build-tools"; return 0; fi
  if [[ "$name" == *"platform/prebuilts/bazel/linux-x86_64"* ]]; then echo "bazel-linux-x86_64"; return 0; fi
  if [[ "$name" == *"platform/prebuilts/jdk/jdk11"* ]]; then echo "jdk11"; return 0; fi
  if [[ "$name" == *"toolchain/prebuilts/ndk/r23"* ]]; then echo "ndk-r23"; return 0; fi
  if [[ "$name" == *"platform/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.17-4.8"* ]]; then echo "gcc-glibc2.17-4.8"; return 0; fi
  return 1
}

googlesource_urls() {
  local repo_url="$1"
  local rev="$2"
  if [[ "$rev" == refs/* ]]; then
    printf '%s/+archive/%s.tar.gz\n' "$repo_url" "$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("${rev}", safe="/"))
PY
)"
    return 0
  fi
  printf '%s/+archive/%s.tar.gz\n' "$repo_url" "$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("refs/heads/${rev}", safe="/"))
PY
)"
  printf '%s/+archive/%s.tar.gz\n' "$repo_url" "$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("refs/tags/${rev}", safe="/"))
PY
)"
  printf '%s/+archive/%s.tar.gz\n' "$repo_url" "$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("${rev}", safe="/"))
PY
)"
}

github_urls() {
  local repo_url="$1"
  local rev="$2"
  if [[ "$rev" == refs/* ]]; then
    printf '%s/archive/%s.tar.gz\n' "$repo_url" "$rev"
    return 0
  fi
  printf '%s/archive/refs/heads/%s.tar.gz\n' "$repo_url" "$rev"
  printf '%s/archive/refs/tags/%s.tar.gz\n' "$repo_url" "$rev"
  printf '%s/archive/%s.tar.gz\n' "$repo_url" "$rev"
}

gitlab_urls() {
  local repo_url="$1"
  local rev="$2"
  local base
  base="$(basename "$repo_url")"
  local qrev
  qrev="$(python3 - <<PY
import urllib.parse
print(urllib.parse.quote("${rev}", safe=""))
PY
)"
  printf '%s/-/archive/%s/%s-%s.tar.gz\n' "$repo_url" "$qrev" "$base" "$qrev"
}

extract_archive() {
  local archive_path="$1"
  local dest_dir="$2"
  local strip="$3"
  mkdir -p "$dest_dir"
  if [[ "$strip" == "1" ]]; then
    tar -xzf "$archive_path" -C "$dest_dir" --strip-components 1
  else
    tar -xzf "$archive_path" -C "$dest_dir"
  fi
}

try_extract_from_cache() {
  local label="$1"
  local rev="$2"
  local dest_dir="$3"
  local strip="$4"

  if [[ -z "$TARGET_REPO" || -z "$GITHUB_TOKEN_VALUE" ]]; then
    return 1
  fi

  refresh_assets
  local meta_name="${label}-${rev}.cache.json"
  local meta_url
  meta_url="$(jq -r --arg n "$meta_name" '.[] | select(.name==$n) | .url' "$assets_json" | head -n 1)"
  local parts=()
  if [[ -n "$meta_url" && "$meta_url" != "null" ]]; then
    local meta_path="${TMP_DIR}/${meta_name}"
    download_release_asset "$meta_url" "$meta_path" || return 1
    mapfile -t parts < <(jq -r '.parts[]?.name' "$meta_path" 2>/dev/null || true)
    if [[ "${#parts[@]}" -eq 0 ]]; then
      return 1
    fi
  else
    mapfile -t parts < <(jq -r --arg p "${label}-${rev}.tar.gz" '.[] | select(.name|startswith($p)) | .name' "$assets_json" | sort)
    if [[ "${#parts[@]}" -eq 0 ]]; then
      return 1
    fi
  fi

  local downloaded_parts=()
  for part in "${parts[@]}"; do
    local url
    url="$(jq -r --arg n "$part" '.[] | select(.name==$n) | .url' "$assets_json" | head -n 1)"
    if [[ -z "$url" || "$url" == "null" ]]; then
      return 1
    fi
    local out="${TMP_DIR}/${part}"
    download_release_asset "$url" "$out" || return 1
    downloaded_parts+=("$out")
  done

  if [[ "${#downloaded_parts[@]}" -eq 1 && "${downloaded_parts[0]}" == *.tar.gz ]]; then
    extract_archive "${downloaded_parts[0]}" "$dest_dir" "$strip"
    return 0
  fi

  local merged="${TMP_DIR}/${label}-${rev}.tar.gz"
  cat "${downloaded_parts[@]}" > "$merged"
  extract_archive "$merged" "$dest_dir" "$strip"
  return 0
}

ensure_cached() {
  local label="$1"
  local rev="$2"
  local src_dir="$3"

  if [[ -z "$TARGET_REPO" || -z "$GITHUB_TOKEN_VALUE" ]]; then
    return 0
  fi

  get_or_create_release || return 0
  local upload_url_template
  upload_url_template="$(jq -r '.upload_url // empty' "$release_json")"
  if [[ -z "$upload_url_template" ]]; then
    return 0
  fi

  refresh_assets
  local meta_name="${label}-${rev}.cache.json"
  if jq -e --arg n "$meta_name" '.[] | select(.name==$n)' "$assets_json" >/dev/null 2>&1; then
    return 0
  fi

  local work_dir="${TMP_DIR}/cache-${label}-${rev}"
  mkdir -p "$work_dir"
  local base_filename="${label}-${rev}.tar.gz"
  local archive_path="${work_dir}/${base_filename}"
  tar -I "gzip -1" -cf "$archive_path" -C "$src_dir" .

  local max_part=$((1900*1024*1024))
  local meta_path="${work_dir}/${meta_name}"
  if [[ "$(stat -c '%s' "$archive_path")" -le "$max_part" ]]; then
    upload_asset "$upload_url_template" "$archive_path" "$base_filename" || true
    python3 - <<PY > "$meta_path"
import json, os, hashlib
p="${archive_path}"
h=hashlib.sha256()
with open(p,"rb") as f:
  for c in iter(lambda:f.read(1024*1024), b""):
    h.update(c)
meta={"format":1,"label":"${label}","rev":"${rev}","archive":"${base_filename}","parts":[{"name":"${base_filename}","size":os.path.getsize(p),"sha256":h.hexdigest()}]}
print(json.dumps(meta,separators=(',',':')))
PY
    upload_asset "$upload_url_template" "$meta_path" "$meta_name" || true
    return 0
  fi

  split -b "$max_part" -d -a 2 "$archive_path" "${archive_path}.part"
  python3 - <<PY > "$meta_path"
import json, os, glob, hashlib
parts=[]
for p in sorted(glob.glob("${archive_path}.part"*)):
  name=os.path.basename(p)
  h=hashlib.sha256()
  with open(p,"rb") as f:
    for c in iter(lambda:f.read(1024*1024), b""):
      h.update(c)
  parts.append({"name":name,"size":os.path.getsize(p),"sha256":h.hexdigest()})
meta={"format":1,"label":"${label}","rev":"${rev}","archive":"${base_filename}","parts":parts}
print(json.dumps(meta,separators=(',',':')))
PY
  for part_path in "${archive_path}.part"*; do
    upload_asset "$upload_url_template" "$part_path" "$(basename "$part_path")" || true
  done
  upload_asset "$upload_url_template" "$meta_path" "$meta_name" || true
}

sync_one_project() {
  local name="$1"
  local path="$2"
  local rev="$3"
  local base_url="$4"
  local dest_dir
  if [[ "$path" == "." || "$path" == "./" ]]; then
    dest_dir="$(pwd)"
  else
    dest_dir="$(pwd)/$path"
  fi
  mkdir -p "$dest_dir"

  local label=""
  if label="$(toolchain_label_for "$name" 2>/dev/null)"; then
    if try_extract_from_cache "$label" "$rev" "$dest_dir" "0"; then
      echo "Synced ${name} -> ${path}"
      return 0
    fi
  fi

  local repo_url="${base_url}/${name}"
  local urls=()
  local strip="0"
  if [[ "$base_url" == *github.com* ]]; then
    mapfile -t urls < <(github_urls "$repo_url" "$rev")
    strip="1"
  elif [[ "$base_url" == *googlesource.com* || "$base_url" == *android.googlesource.com* ]]; then
    mapfile -t urls < <(googlesource_urls "$repo_url" "$rev")
    strip="0"
  elif [[ "$base_url" == *git.codelinaro.org* || "$base_url" == *gitlab* ]]; then
    mapfile -t urls < <(gitlab_urls "$repo_url" "$rev")
    strip="1"
  else
    echo "[FAIL] ${name} -> ${path} rev=${rev} remote=${base_url} err=no supported remote" >&2
    return 1
  fi

  local tmp_archive="${TMP_DIR}/dl-$(echo -n "${name}-${rev}" | sha256sum | awk '{print $1}').tar.gz"
  local ok=false
  local last_err=""
  for u in "${urls[@]}"; do
    if curl -LfsS --retry 5 --connect-timeout 30 -o "$tmp_archive" "$u" >/dev/null 2>&1; then
      extract_archive "$tmp_archive" "$dest_dir" "$strip"
      ok=true
      break
    else
      last_err="curl failed: $u"
      continue
    fi
  done
  if [[ "$ok" != "true" ]]; then
    echo "[FAIL] ${name} -> ${path} rev=${rev} remote=${base_url} err=${last_err}" >&2
    for u in "${urls[@]}"; do
      echo "       url=${u}" >&2
    done
    return 1
  fi

  if [[ "$path" == "prebuilts/build-tools" ]]; then
    if [[ ! -f "${dest_dir}/BUILD.bazel" ]]; then
      echo "[FAIL] ${name} -> ${path} rev=${rev} remote=${base_url} err=BUILD.bazel missing after extract" >&2
      return 1
    fi
    if ! rg -q "py_toolchain" "${dest_dir}/BUILD.bazel"; then
      echo "[FAIL] ${name} -> ${path} rev=${rev} remote=${base_url} err=BUILD.bazel missing py_toolchain" >&2
      return 1
    fi
  fi

  if [[ -n "$label" ]]; then
    ensure_cached "$label" "$rev" "$dest_dir" || true
  fi

  echo "Synced ${name} -> ${path}"
}

projects_jsonl="${TMP_DIR}/parsed.jsonl"
project_lines="${TMP_DIR}/projects.txt"
op_lines="${TMP_DIR}/ops.txt"

if [[ ! -f "$project_lines" || ! -f "$op_lines" ]]; then
  jq -r 'select(.type=="project") | [.name,.path,.rev,.base_url] | @tsv' "$projects_jsonl" > "$project_lines"
  jq -r 'select(.type=="op") | [.tag,.project_path,(.src//""),(.dest//"")] | @tsv' "$projects_jsonl" > "$op_lines"
fi

if [[ "$PHASE" != "post" ]]; then
  fail_count=0
  while IFS=$'\t' read -r name path rev base_url; do
    if ! sync_one_project "$name" "$path" "$rev" "$base_url"; then
      fail_count=$((fail_count+1))
    fi
  done < "$project_lines"

  if [[ "$fail_count" -ne 0 ]]; then
    exit 1
  fi
fi

if [[ "$PHASE" == "sync" && "$RUN_ALL" != "true" ]]; then
  exit 0
fi

if [[ "$PHASE" != "post" && "$RUN_ALL" != "true" ]]; then
  exit 0
fi

build_tools_dir="$(pwd)/prebuilts/build-tools"
expected="${build_tools_dir}/path/linux-x86/python3"
if [[ ! -e "$expected" ]]; then
  mkdir -p "$(dirname "$expected")"
  candidate="$(find "$build_tools_dir" -type f -name python3 -print -quit 2>/dev/null || true)"
  if [[ -z "$candidate" ]]; then
    candidate="$(command -v python3 || true)"
  fi
  if [[ -n "$candidate" ]]; then
    rm -f "$expected" 2>/dev/null || true
    ln -s "$(python3 - <<PY
import os
print(os.path.relpath("${candidate}", os.path.dirname("${expected}")))
PY
)" "$expected" || true
  fi
fi

while IFS=$'\t' read -r tag project_path src dest; do
  if [[ -z "$src" || -z "$dest" ]]; then
    continue
  fi
  src_path="$(pwd)/${project_path}/${src}"
  dest_path="$(pwd)/${dest}"
  mkdir -p "$(dirname "$dest_path")"
  if [[ "$tag" == "linkfile" ]]; then
    rm -f "$dest_path" 2>/dev/null || true
    ln -s "$(python3 - <<PY
import os
print(os.path.relpath("${src_path}", os.path.dirname("${dest_path}")))
PY
)" "$dest_path"
  else
    cp -p "$src_path" "$dest_path"
  fi
done < "$op_lines"

exit 0
