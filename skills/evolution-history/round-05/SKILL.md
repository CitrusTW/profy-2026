---
name: threejs
description: "Export Three.js scenes to OBJ preserving world transforms and instances; optionally partition named groups into OBJ parts or URDF links."
---

# Three.js export

## Route

- Single OBJ: use the complete example below; no merging, part map, or articulation references.
- Per-part: nearest named Group owns each mesh; key by Group identity, not name. Nested groups own separate meshes. Skip empty parts; use deterministic unique filenames. Read `references/link-export-rules.md`.
- URDF: named groups are links; nearest named ancestor is parent. Default joints to fixed without motion evidence. Read `references/joint-type-heuristics.md` and `references/urdf-minimal.md`.

## Single OBJ

Use the task-pinned dependency; when needed install once with `npm install --no-audit --no-fund three@0.175.0`, without dependency-discovery probes. Save this as `output/export_object.mjs`; run from the project root with `node output/export_object.mjs`. Change paths/axis only as requested. Input bytes stay unchanged.

```javascript
import fs from 'node:fs/promises';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
const source = (await fs.readFile('data/object.js', 'utf8')).replace(
  /(from\s*)(['"])three\2/g,
  (_, p) => p + JSON.stringify(import.meta.resolve('three')));
const { createScene } = await import(
  'data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const root = createScene();
root.updateMatrixWorld(true);
// Requested -90 degree X rotation; use identity if no conversion is requested.
const axis = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
const out = new THREE.Group();
function bake(mesh, world, name) {
  let geom = mesh.geometry.clone();
  if (!geom.attributes.normal) geom.computeVertexNormals();
  for (const key of ['position', 'normal']) {
    const a = geom.getAttribute(key);
    geom.setAttribute(key, new THREE.BufferAttribute(
      new Float64Array(a.array), a.itemSize));
  }
  const transform = axis.clone().multiply(world);
  geom.applyMatrix4(transform);
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

Keep the nonindexed serialization line. Float64 promotion above assumes standard BufferAttributes. Never recenter/rescale, double-bake transforms, or negate reflection normals: `applyMatrix4` already uses inverse-transpose normals; swap winding instead.

Validate once in the export run: use the loaded scene and baked geometry for expanded counts, finite attributes, transformed positions, and nondegenerate face/normal agreement; check serialized face-index ranges. Keep checks bounded and inline, not a second scene loader, reusable audit file, or another export. Derive expectations from input, never fixed counts. If packaging is requested, hash/package the exact saved bytes afterward; do not reserialize. Keep audits/dependencies outside deliverables.

Attached `bench_skills/` resources use ordinary file/shell tools, not registered IDs. Native resources use `skill.execute`. Other routes: `export_link_objs.mjs --input <scene_js> --out-dir <dir>`; `build_urdf_from_scene.mjs --input <scene_js> --output <file.urdf> --mesh-dir <dir>`. Do not probe unrelated scripts for a single OBJ.
