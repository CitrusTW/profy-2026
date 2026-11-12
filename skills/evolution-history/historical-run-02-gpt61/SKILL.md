---
name: threejs
description: "Export Three.js scenes to OBJ or articulated URDF: preserve world transforms, expand InstancedMesh, handle mirrored geometry, and optionally partition named groups into links."
---

# Three.js scene export

## Choose only the requested output

- One OBJ: traverse all meshes once into one export container; retain mesh names. Skip part maps, merging, URDF, and articulation references.
- Per-part OBJ: assign each mesh to its nearest named Group; nested named groups own their meshes separately. Key parts by Group identity, not name; use deterministic unique filenames and skip empty parts. Read `references/link-export-rules.md` only for this route.
- URDF: named groups become links, with the nearest named ancestor as parent. Default joints to fixed absent evidence of motion; sort names deterministically. Read `references/joint-type-heuristics.md` and `references/urdf-minimal.md` only here.

## Bake geometry once

1. Load the supplied module, call `createScene()`, then `root.updateMatrixWorld(true)`. Preserve the source file and original transforms; do not recenter or rescale.
2. Ordinary mesh: use `mesh.matrixWorld`. InstancedMesh: expand each instance using the order below; OBJExporter does not expand instances for you.
3. Clone geometry, ensure normals exist, apply the combined matrix, and correct reflected winding. Put each baked geometry on an identity-transform Mesh in the export container. Update its world matrices, then serialize with Three.js OBJExporter.

```javascript
const axis = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
// Apply this axis only when requested; otherwise use an identity matrix.
const world = mesh.matrixWorld.clone();
// For instance i, instead:
// mesh.getMatrixAt(i, instance);
// world.copy(mesh.matrixWorld).multiply(instance);
const transform = axis.clone().multiply(world);
const geometry = mesh.geometry.clone();
if (!geometry.attributes.normal) geometry.computeVertexNormals();
geometry.applyMatrix4(transform);
if (transform.determinant() < 0) {
  if (!geometry.index) {
    geometry.setIndex(Array.from(
      {length: geometry.attributes.position.count}, (_, i) => i));
  }
  const index = geometry.index;
  for (let i = 0; i < index.count; i += 3) {
    const b = index.getX(i + 1);
    index.setX(i + 1, index.getX(i + 2));
    index.setX(i + 2, b);
  }
}
```

`applyMatrix4` transforms normals with the inverse transpose: do not rotate normals as positions under nonuniform scale. Reflection needs the index swap above, not negated normals. Keep indices/UVs; do not unconditionally call `toNonIndexed()` or merge unlike attribute layouts. For precision-sensitive baking, promote cloned position/normal attributes to Float64 before transformation.

## Runtime and checks

Use the task-pinned Three.js version (observed: `three@0.175.0`). If bare imports fail, resolve the installed module URL in an in-memory source copy; never rewrite input just to load it. Check finite coordinates, face-index ranges, and face/normal orientation in one pass; derive counts from the scene rather than hardcoding them. Export all instances even when the source has only one InstancedMesh node.

## Existing resources

Use attached scripts through `skill.execute` rather than rebuilding their pipelines:
- `scripts/export_instanced_obj.mjs`: instance-aware OBJ export.
- `scripts/export_link_objs.mjs --input <scene_js> --out-dir <dir>`: per-link OBJ.
- `scripts/build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>`: URDF.

Select only the applicable resource; adapt task paths as its interface permits.
