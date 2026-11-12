---
name: threejs
description: "Export Three.js scenes to OBJ with world transforms and instances preserved; optionally partition named groups into OBJ parts or URDF links."
---

# Three.js export

## Route first

- Single OBJ: traverse once into one container; retain mesh names. No part map, merging, or articulation references.
- Per-part OBJ: assign meshes to their nearest named Group; key by Group identity, not name. Nested groups own separate meshes. Skip empty parts; use deterministic unique filenames. Read `link-export-rules.md`.
- URDF: named groups are links; nearest named ancestor is parent. Default joints to fixed absent motion evidence. Read `joint-type-heuristics.md` and `urdf-minimal.md`.

## Runtime: use known answers

Use the task-pinned version (observed working: `three@0.175.0`). When installation is needed, install once: `npm install --no-audit --no-fund three@0.175.0`; do not first run an exporter to discover missing dependencies.

Preserve input bytes. In a loader located under the project, resolve its bare import in memory, not by rewriting input or constructing a hardcoded node_modules path:

```javascript
const source = (await fs.readFile(input, 'utf8')).replace(
  /(from\s*)(['"])three\2/g,
  (_, prefix) => prefix + JSON.stringify(import.meta.resolve('three')));
const { createScene } = await import(
  'data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
```

`fs` above is `node:fs/promises`. Resolve other imports only if present.

## Single-OBJ baking

1. Call `createScene()`, then `root.updateMatrixWorld(true)`; never recenter or rescale.
2. Ordinary mesh: `world = mesh.matrixWorld`. For each instance: `getMatrixAt(i, instance)` then `world = mesh.matrixWorld.clone().multiply(instance)`.
3. Clone geometry; ensure normals exist. For precision-sensitive baking promote cloned position/normal attributes to Float64. Apply `axis.clone().multiply(world)` once. Axis is identity unless requested; -90° X is `new THREE.Matrix4().makeRotationX(-Math.PI / 2)`.
4. `geometry.applyMatrix4(transform)` handles inverse-transpose normals. When `transform.determinant() < 0`, create sequential indices if absent, then swap each triangle's second/third indices. Do not negate normals, discard UVs, or unconditionally call `toNonIndexed()`.
5. Put baked geometry on identity-transform Mesh objects; retain names and suffix instances. Update container world matrices; serialize with Three.js `OBJExporter`.
6. Validate once with concise checks: scene-derived counts including instances, finite attributes, face-index ranges, transformed positions, and nondegenerate face/normal orientation. No hardcoded counts, repeated exports, or expanded reusable audit framework.

## Resources

Use `skill.execute` with resource basenames. `export_instanced_obj.mjs` has fixed paths, no `--help`, and merged/nonindexed/unnamed output: skip it for names or reflections; use baking above. Do not probe it. Other routes: `export_link_objs.mjs --input <scene_js> --out-dir <dir>`; `build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>`.
