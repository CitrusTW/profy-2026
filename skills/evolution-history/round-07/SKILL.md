---
name: mesh-analysis
description: "Analyze binary STL meshes, isolate the largest connected component, extract Material IDs from triangle attributes, and calculate volume or density-based mass while excluding scan debris."
---

# Mesh Analysis

Use the supplied `scripts/mesh_tool.py` module. `MeshAnalyzer(path).analyze_largest_component()` returns `main_part_volume`, `main_part_material_id`, and `total_components`; it handles binary parsing, component selection and the 2-byte attribute field. Do not replace it with a second connectivity/volume implementation for routine verification.

## Direct workflow

1. Read the supplied density table and any coordinate-unit instructions. Resolve the actual skill package, input and output paths before execution. For extracted environments, map original absolute paths to their extracted `fs` locations; do not access the original host paths. An attached skill is a directory, not necessarily a registered skill ID. Do not assume `/root/.claude/skills` exists.
2. Run one Python invocation with four arguments: package directory, STL path, density-table path, output JSON path. All paths must be accessible in the current workspace. The example supports Markdown rows with plain or bold numeric IDs.
3. Deliver the requested JSON. If an execution adapter requires an archive/manifest, package the exact saved bytes at the requested logical location; keep scratch analysis and dependencies out of the archive.

```python
# Run this body with the four arguments described above.
import json, re, sys
from pathlib import Path

package, stl, table, output = map(Path, sys.argv[1:])
sys.path.insert(0, str(package.resolve() / 'scripts'))
from mesh_tool import MeshAnalyzer

report = MeshAnalyzer(str(stl)).analyze_largest_component()
volume = float(report['main_part_volume'])
material_id = int(report['main_part_material_id'])
densities = {}
for line in table.read_text().splitlines():
    cells = [c.strip().replace('**', '')
             for c in line.strip().strip('|').split('|')]
    if len(cells) >= 3 and re.fullmatch(r'\d+', cells[0]):
        densities[int(cells[0])] = float(cells[2])
if material_id not in densities:
    raise ValueError(f'Material ID {material_id} missing from density table')
# Convert volume here ONLY when documented units require it.
mass = volume * densities[material_id]
output.write_text(json.dumps({
    'main_part_mass': mass, 'material_id': material_id
}, indent=2) + '\n')
```

Volume is in coordinate units cubed; STL has no standard unit declaration. Check task metadata before multiplying. Convert only for a documented mismatch; if units are unspecified, disclose the assumption instead of inventing a scale. Preserve numeric precision in JSON.

A missing material row is an error, not permission to substitute debris density. Investigate geometry only if the module fails or yields anomalous results; a successful analysis does not require a separate watertightness or NumPy reimplementation. On a path-permission failure, correct the workspace mapping rather than retrying the same original absolute path.
