---
name: threejs
description: "Export Three.js scenes to OBJ with world transforms and instances preserved; optionally partition named groups into OBJ parts or URDF links."
---

# Three.js export

## Select the route before running anything

- Single OBJ: one traversal into an export container; no part map, merging, or articulation references.
- Per-part OBJ: each mesh belongs to its nearest named Group. Key by Group identity, not name; nested named groups own separate meshes. Skip empty parts and use deterministic unique filenames. Read `link-export-rules.md` only here.
- URDF: named groups are links; nearest named ancestor is parent. Default joints to fixed unless motion is evidenced. Read `joint-type-heuristics.md` and `urdf-minimal.md` only here.

## Known runtime facts: skip rediscovery

Use the task-pinned dependency; observed working version: `three@0.175.0`. Install once if needed, not after a failed exporter probe. Preserve the input bytes. For its bare imports, substitute resolved module URLs in an in-memory source copy and import that copy; do not rewrite the input.

The supplied `export_instanced_obj.mjs` has fixed paths and does not handle `--help` as a CLI option. Its observed output is merged, nonindexed, and unnamed. Do not probe it with flags or run it to discover these facts. Use it through `skill.execute` only when its fixed-path/merged output fits the task. For retained mesh names or reflected geometry, use the OBJExporter baking route below directly instead of running an incompatible resource first. Use `export_link_objs.mjs --input <scene_js> --out-dir <dir>` or `build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>` through `skill.execute` for their respective routes.

## OBJExporter baking route

1. Call `createScene()`, then `root.updateMatrixWorld(true)`; never recenter or rescale.
2. Ordinary mesh: `world = mesh.matrixWorld`. For every instance, `getMatrixAt(i, instance)` then `world = mesh.matrixWorld.clone().multiply(instance)`.
3. Clone geometry, ensure normals exist, and bake `axis.clone().multiply(world)`. Axis is identity unless requested; for the specified -90° X conversion use `new THREE.Matrix4().makeRotationX(-Math.PI / 2)`. For precision-sensitive baking promote cloned position/normal attributes to Float64 first.
4. `geometry.applyMatrix4(transform)` handles inverse-transpose normals. If `transform.determinant() < 0`, ensure an index exists and swap each triangle's second and third indices; do not negate normals. Preserve UVs and indices; no unconditional `toNonIndexed()`.
5. Add each baked geometry to an identity-transform Mesh, retain names (suffix instances), update container world matrices, then serialize with Three.js `OBJExporter`.
6. Validate once: derive expected counts from the scene including all instances; check finite coordinates, face-index ranges, transformed positions, and nondegenerate face/normal orientation. Do not hardcode observed counts or add repeated export/check passes.
