---
name: threejs
description: "Export Three.js scenes to OBJ preserving world transforms and instances; optionally partition named groups into OBJ parts or URDF links."
---

# Three.js export

## Choose the output

- Single OBJ: use the example below; no part map, merging, or articulation references.
- Per-part OBJ: assign each mesh to its nearest named Group, keyed by Group identity rather than name. Nested named groups own separate meshes. Skip empty parts; choose deterministic unique filenames. Read `references/link-export-rules.md`.
- URDF: named groups are links; nearest named ancestor is parent. Default joints to fixed absent motion evidence. Read `references/joint-type-heuristics.md` and `references/urdf-minimal.md`.

## Single OBJ: complete example

Install the task-pinned dependency once when needed: `npm install --no-audit --no-fund three@0.175.0`. Save as `output/export_object.mjs`; run `node output/export_object.mjs` from the project root. Preserve input bytes; resolve the bare import in memory.

```javascript
import fs from 'node:fs/promises';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';

const source = (await fs.readFile('data/object.js', 'utf8')).replace(
  /(from\s*)(['"])three\2/g,
  (_, prefix) => prefix + JSON.stringify(import.meta.resolve('three')));
const { createScene } = await import(
  'data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const root = createScene();
root.updateMatrixWorld(true);
// Use identity unless conversion is requested. Here: requested -90 degree X.
const axis = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
const out = new THREE.Group();
function bake(mesh, world, name) {
  let geom = mesh.geometry.clone();
  if (!geom.attributes.normal) geom.computeVertexNormals();
  // Standard BufferAttributes: avoid Float32 rounding during world baking.
  for (const key of ['position', 'normal']) {
    const a = geom.getAttribute(key);
    geom.setAttribute(key, new THREE.BufferAttribute(
      new Float64Array(a.array), a.itemSize));
  }
  const transform = axis.clone().multiply(world);
  geom.applyMatrix4(transform); // includes inverse-transpose normals
  if (transform.determinant() < 0) {
    if (!geom.index) geom.setIndex(Array.from(
      { length: geom.attributes.position.count }, (_, i) => i));
    const ix = geom.index;
    for (let i = 0; i < ix.count; i += 3) {
      const b = ix.getX(i + 1);
      ix.setX(i + 1, ix.getX(i + 2));
      ix.setX(i + 2, b);
    }
  }
  if (geom.index) geom = geom.toNonIndexed();
  const baked = new THREE.Mesh(geom, mesh.material);
  baked.name = name;
  out.add(baked);
}
root.traverse(mesh => {
  if (!mesh.isMesh) return;
  if (mesh.isInstancedMesh) {
    for (let i = 0; i < mesh.count; i++) {
      const instance = new THREE.Matrix4();
      mesh.getMatrixAt(i, instance);
      bake(mesh, mesh.matrixWorld.clone().multiply(instance),
        `${mesh.name}_instance_${i}`);
    }
  } else bake(mesh, mesh.matrixWorld, mesh.name);
});
out.updateMatrixWorld(true);
await fs.mkdir('output', { recursive: true });
await fs.writeFile('output/object.obj', new OBJExporter().parse(out));
```

Never recenter/rescale, double-apply transforms, or negate reflection normals. The original nonindexed serialization is intentional: preserve it. Validate once using scene-derived counts after expansion, finite attributes, face-index ranges, transformed positions, and nondegenerate face/normal orientation. Do not hardcode counts or build an expanded audit framework.

## Other resources

Attached `bench_skills/` files use ordinary read/shell tools, not registered skill IDs. Native registered resources use `skill.execute`. Per-part script: `export_link_objs.mjs --input <scene_js> --out-dir <dir>`; URDF: `build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>`. Do not probe unrelated scripts for a single OBJ.
