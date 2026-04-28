import os
import base64
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

MANIFEST_URLS = [
    url.strip()
    for url in os.environ.get("MANIFEST_URLS", "").splitlines()
    if url.strip()
]

manifest_projects = defaultdict(set)  # resource -> set of manifest names
manifest_names = []

for url in MANIFEST_URLS:
    # Extract manifest name from URL (branch or last path segment)
    if "/+/refs/heads/" in url:
        manifest_name = url.split("/+/refs/heads/")[-1].split("/")[0]
    else:
        manifest_name = url.split("/")[-2]
    manifest_names.append(manifest_name)
    print(f"Fetching manifest: {manifest_name}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}")
        continue
    # Googlesource returns base64-encoded XML
    xml_content = base64.b64decode(resp.content).decode("utf-8")
    root = ET.fromstring(xml_content)
    for project in root.findall("project"):
        name = project.get("name")
        path = project.get("path", name)
        manifest_projects[(name, path)].add(manifest_name)

# Write summary as markdown
with open("manifest_resource_summary.md", "w") as f:
    f.write("| Resource Name | Path | Appears In Manifests |\n")
    f.write("|--------------|------|----------------------|\n")
    for (name, path), manifests in sorted(manifest_projects.items()):
        f.write(f"| `{name}` | `{path}` | {', '.join(sorted(manifests))} |\n")

print("Summary written to manifest_resource_summary.md")
