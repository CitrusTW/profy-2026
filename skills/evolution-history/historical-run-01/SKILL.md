---
name: threejs
description: "Three.js scene-graph parsing and export workflows: mesh baking, InstancedMesh expansion, part partitioning, per-link OBJ export, and URDF articulation."
---

# Three.js Scene Graph Export — Efficient SOP

## Workflow (OBJ/URDF export)

1. **Load** the scene module and call `createScene()`. 
2. **Update transforms**: `root.updateMatrixWorld(true)`.
3. **Partition parts**: treat every named `THREE.Group` as a part/link. Each mesh belongs to its nearest named ancestor group. Do NOT merge meshes from nested named groups into parents.
4. **Bake transforms**: For each mesh, clone geometry and apply `mesh.matrixWorld`. Always compute normals if missing. For InstancedMesh, expand each instance with its world matrix.
5. **Axis conversion**: Apply a -90° X rotation (`new THREE.Matrix4().makeRotationX(-Math.PI/2)`) to all baked geometries for Blender Z-up compatibility.
6. **Export**: Merge baked geometries per part. Do NOT traverse into child named groups when exporting a part. Write OBJ per part (or full scene as needed).
7. **URDF**: Use named groups as links; parent is nearest named ancestor. Default joint type is `fixed` unless otherwise indicated. Sort link/joint names for determinism.

## Known Failures & Recovery
- If OBJ is empty or contains NaN/Infinity, check for missing geometry or invalid transforms.
- SkinnedMesh is not supported—requires pose baking before export.

## Antipatterns (Do NOT)
- Do NOT merge meshes from nested named groups into parents.
- Do NOT traverse into child named groups when exporting per-part OBJ.
- Do NOT skip axis conversion if Blender import is required.

## Reference Commands
- Per-link OBJ: `node scripts/export_link_objs.mjs --input <scene_js> --out-dir <dir>`
- InstancedMesh OBJ: `node scripts/export_instanced_obj.mjs`
- URDF: `node scripts/build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <mesh_dir>`

## Empirical Grounding
- All steps and commands are validated by measured runs (see run_stats: 8 tool calls, 152k tokens, success). Axis conversion and mesh baking are required for Blender-ready OBJ.

## References
- `link-export-rules.md`, `joint-type-heuristics.md`, `urdf-minimal.md`
