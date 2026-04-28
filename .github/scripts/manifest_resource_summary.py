import base64
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import re

REFS_URL = "https://android.googlesource.com/kernel/manifest/+refs"
MANIFEST_URL_TEMPLATE = "https://android.googlesource.com/kernel/manifest/+/refs/heads/{branch}/default.xml?format=TEXT"

print("Fetching all manifest branches from googlesource...")
refs_resp = requests.get(REFS_URL)
refs = refs_resp.text.splitlines()
branches = set()
for line in refs:
    m = re.search(r'refs/heads/(common-[^<"\s]+)', line)
    if m:
        branches.add(m.group(1))
    m2 = re.search(r'refs/heads/deprecated/(common-[^<"\s]+)', line)
    if m2:
        branches.add(f"deprecated/{m2.group(1)}")

manifest_projects = defaultdict(set)  # resource -> set of manifest names
manifest_names = []

for branch in sorted(branches):
    manifest_name = branch
    url = MANIFEST_URL_TEMPLATE.format(branch=branch)
    print(f"Fetching manifest: {manifest_name}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}")
        continue
    xml_content = base64.b64decode(resp.content).decode("utf-8")
    root = ET.fromstring(xml_content)
    for project in root.findall("project"):
        name = project.get("name")
        path = project.get("path", name)
        manifest_projects[(name, path)].add(manifest_name)
    manifest_names.append(manifest_name)

with open("manifest_resource_summary.md", "w") as f:
    f.write("| Resource Name | Path | Appears In Manifests |\n")
    f.write("|--------------|------|----------------------|\n")
    for (name, path), manifests in sorted(manifest_projects.items()):
        f.write(f"| `{name}` | `{path}` | {', '.join(sorted(manifests))} |\n")

print("Summary written to manifest_resource_summary.md")
