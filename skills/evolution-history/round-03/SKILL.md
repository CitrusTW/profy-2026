---
name: threejs
description: "Export Three.js scenes to OBJ with world transforms and instances preserved; optionally partition named groups into OBJ parts or URDF links."
---

# Three.js export

## Route

- Single OBJ: one traversal into one container; retain mesh names. No part map, merging, or articulation references.
- Per-part OBJ: meshes belong to their nearest named Group; key by Group identity, not name. Nested groups own separate meshes. Skip empty parts; use deterministic unique filenames. Read `link-export-rules.md`.
- URDF: named groups are links; nearest named ancestor is parent. Default joints to fixed absent motion evidence. Read `joint-type-heuristics.md` and `urdf-minimal.md`.

## Runtime

Stay in the current project; do not probe other sessions or system dependency paths. If installation is needed, run once: `npm install --no-audit --no-fund three@0.175.0` (use the task-pinned version). Do not run exporters to discover missing dependencies.

Preserve input bytes. Load its bare import using an in-memory copy; no hardcoded node_modules path:

```javascript
// fs = node:fs/promises; loader resides under the project.
const source = (await fs.readFile(input, 'utf8')).replace(
  /(from\s*)(['"])three\2/g,
  (_, prefix) => prefix + JSON.stringify(import.meta.resolve('three')));
const { createScene } = await import(
  'data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
```

Resolve other imports only if present. Use read/write/edit for file operations; batch independent reads.

## Single OBJ

1. Call `createScene()` and `root.updateMatrixWorld(true)`; never recenter or rescale.
2. Ordinary mesh: `world = mesh.matrixWorld`. Every instance: `getMatrixAt(i, instance)` then `world = mesh.matrixWorld.clone().multiply(instance)`.
3. Clone geometry; ensure normals exist. Promote cloned position/normal attributes to Float64 for precision-sensitive baking. Apply `axis.clone().multiply(world)` once. Axis defaults to identity; requested -90° X uses `new THREE.Matrix4().makeRotationX(-Math.PI / 2)`.
4. `applyMatrix4` handles inverse-transpose normals. If the combined determinant is negative, create sequential indices if absent and swap each triangle's second/third indices. Do not negate normals, discard UVs, or unconditionally call `toNonIndexed()`.
5. Add baked geometry on identity-transform Mesh objects; retain names, suffix instances. Update container world matrices; serialize with Three.js `OBJExporter`.
6. Validate once: derive expected counts/positions while traversing the source, including instances; check serialized OBJ counts, finite attributes, index ranges, transformed positions, and nondegenerate face/normal orientation. Do not duplicate these checks on baked geometry, hardcode counts, rerun exports, or build a reusable audit framework.

## Resources

Use `skill.execute` with resource basenames. `export_instanced_obj.mjs` has fixed paths, no `--help`, and merged/nonindexed/unnamed output: skip it for names or reflections; use baking above. Do not probe it. Other routes: `export_link_objs.mjs --input <scene_js> --out-dir <dir>`; `build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>`.
