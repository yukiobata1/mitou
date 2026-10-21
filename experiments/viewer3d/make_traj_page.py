"""Make closeup-traj.html: the close-up viewer driven by traj.json (build_microsim.py) instead of
section-entry events. window.renderAt(k, cam) draws 60 Hz frame k from camera cam."""
src = open('closeup.html', encoding='utf-8').read()

def sub(old, new, count=1):
    global src
    assert old in src, old[:60]
    src = src.replace(old, new, count)

sub('</style>', '  .panel { display: none !important; }\n</style>')
sub("scene.fog = new THREE.Fog(0xdfe5ec, 60, 140);", "scene.fog = new THREE.Fog(0xcdb77a, 28, 80);")
# yellow room lighting (lithography bays filter out short wavelengths)
sub("scene.background = new THREE.Color(0xdfe5ec);", "scene.background = new THREE.Color(0xcdb77a);")
sub("scene.add(new THREE.HemisphereLight(0xffffff, 0x8a94a3, 0.55));", "scene.add(new THREE.HemisphereLight(0xffd35a, 0xc9a24a, 1.25));")
sub("const sun = new THREE.DirectionalLight(0xffffff, 1.6);", "const sun = new THREE.DirectionalLight(0xffc940, 1.7);")
sub("const lampMat = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 1.2 });",
    "const lampMat = new THREE.MeshStandardMaterial({ color: 0xffd24a, emissive: 0xffc830, emissiveIntensity: 1.4 });")
sub("scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;",
    "scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;\n"
    "renderer.toneMappingExposure = 1.1;")
# FOUP: dark smoky-brown translucent shell with 25 wafers (300 mm, 10 mm pitch) inside
sub("import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';",
    "import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';\n"
    "import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';")
sub("const foupMat = new THREE.MeshPhysicalMaterial({ color: 0x8fa3bd, roughness: 0.25, metalness: 0.0, clearcoat: 0.6, transparent: true, opacity: 0.92 });",
    "const foupMat = new THREE.MeshPhysicalMaterial({ color: 0x3b2618, roughness: 0.3, metalness: 0.0, clearcoat: 0.7, transparent: true, opacity: 0.62, depthWrite: false });\n"
    "const waferMat = new THREE.MeshPhysicalMaterial({ color: 0xb8bcc8, metalness: 0.95, roughness: 0.12, iridescence: 1.0, iridescenceIOR: 1.8, iridescenceThicknessRange: [250, 700] });\n"
    "const waferGeo = mergeGeometries(Array.from({ length: 25 }, (_, k) => new THREE.CylinderGeometry(0.15, 0.15, 0.003, 40).translate(0, -0.125 + k * 0.0104, 0)));")
sub("const lidMat = new THREE.MeshStandardMaterial({ color: 0x3c4a5c, roughness: 0.5 });",
    "const lidMat = new THREE.MeshStandardMaterial({ color: 0x1f1510, roughness: 0.45 });")
sub("    inst(new THREE.BoxGeometry(0.3, 0.04, 0.05), darkMat, n),                        // FOUP handle\n",
    "    inst(new THREE.BoxGeometry(0.3, 0.04, 0.05), darkMat, n),                        // FOUP handle\n"
    "    inst(waferGeo, waferMat, n),                                                     // 25 wafers inside the FOUP\n")
sub("const data = await (await fetch('scene-closeup.json')).json();",
    "const data = await (await fetch('scene-closeup.json')).json();\n"
    "const TR = await (await fetch('traj.json')).json();\n"
    "const origLinks = data.links;")
# rails: smooth (tessellated) geometry from traj.json
sub("const flangeTop = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.06, 0.34), railMat, data.links.length);",
    "const railLinks = TR.rails;\nconst flangeTop = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.06, 0.34), railMat, railLinks.length);")
sub("const web = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.22, 0.06), railMat, data.links.length * 2);",
    "const web = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.22, 0.06), railMat, railLinks.length * 2);")
sub("const flangeBot = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.06, 0.34), railMat, data.links.length);\ndata.links.forEach((l, i) => {",
    "const flangeBot = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 0.06, 0.34), railMat, railLinks.length);\nrailLinks.forEach((l, i) => {")
sub("const dx = x2 - x1, dz = z2 - z1, len = Math.hypot(dx, dz) || 0.01;",
    "const dx = x2 - x1, dz = z2 - z1, len = (Math.hypot(dx, dz) || 0.01) + 0.02;")
sub("data.links.forEach(l => { const [x1, z1] = toXZ(l[0], l[1]), [x2, z2] = toXZ(l[2], l[3]);\n  const n = Math.max(1, Math.round(Math.hypot(x2 - x1, z2 - z1) / 4));",
    "origLinks.forEach(l => { const [x1, z1] = toXZ(l[0], l[1]), [x2, z2] = toXZ(l[2], l[3]);\n  const n = Math.max(1, Math.round(Math.hypot(x2 - x1, z2 - z1) / 4));")
sub("data.links.forEach(l => {\n  const [x1, z1] = toXZ(l[0], l[1]), [x2, z2] = toXZ(l[2], l[3]);\n  if (Math.abs(z2 - z1)",
    "origLinks.forEach(l => {\n  const [x1, z1] = toXZ(l[0], l[1]), [x2, z2] = toXZ(l[2], l[3]);\n  if (Math.abs(z2 - z1)")
# load port: a pedestal directly under the rail (top at 1.01 m), where the hoist sets the FOUP down
sub("const port = new THREE.InstancedMesh(new THREE.BoxGeometry(0.55, 0.12, 0.55), portMat, toolPos.length);",
    "const port = new THREE.InstancedMesh(new THREE.BoxGeometry(0.5, 0.90, 0.5), portMat, toolPos.length);")
sub("m4.makeTranslation(p[0] - 1.5, 0.95, p[1]); port.setMatrixAt(i, m4);",
    "m4.makeTranslation(p[0] - 2.1, 0.45, p[1]); port.setMatrixAt(i, m4);")
# vehicle count from traj
sub("const n = run.ohts.length;", "const n = TR.nveh;")
sub('  parts = [\n    inst(new THREE.BoxGeometry(1.1, 0.22, 0.26), darkMat, n),                       // bogie on rail\n    inst(new RoundedBoxGeometry(1.75, 0.62, 0.95, 3, 0.08), bodyMat, n),             // body shell\n    inst(new THREE.BoxGeometry(1.78, 0.08, 0.98), blueMat, n),                       // blue belt line\n    inst(new THREE.BoxGeometry(0.28, 0.05, 0.12), lampOn, n),                        // status lamp (tinted)\n    inst(new THREE.CylinderGeometry(0.012, 0.012, 0.3, 6), beltMat, n),              // hoist belt L (retracted while travelling)\n    inst(new THREE.CylinderGeometry(0.012, 0.012, 0.3, 6), beltMat, n),              // hoist belt R\n    inst(new THREE.BoxGeometry(0.62, 0.08, 0.4), darkMat, n),                        // gripper plate\n    inst(new RoundedBoxGeometry(0.44, 0.42, 0.44, 3, 0.04), foupMat, n),             // FOUP body\n    inst(new THREE.BoxGeometry(0.46, 0.05, 0.46), lidMat, n),                        // FOUP top plate\n    inst(new THREE.BoxGeometry(0.3, 0.04, 0.05), darkMat, n),                        // FOUP handle\n', '  parts = [\n    inst(new THREE.BoxGeometry(0.8, 0.2, 0.24), darkMat, n),                         // travel unit inside the rail\n    inst(new RoundedBoxGeometry(1.05, 0.34, 0.56, 3, 0.05), bodyMat, n),             // upper housing (drive + hoist)\n    inst(new THREE.BoxGeometry(1.06, 0.045, 0.57), blueMat, n),                      // blue line\n    inst(new THREE.BoxGeometry(0.16, 0.04, 0.08), lampOn, n),                        // status lamp (tinted)\n    inst(new THREE.CylinderGeometry(0.008, 0.008, 0.3, 6), beltMat, n),              // hoist belt L\n    inst(new THREE.CylinderGeometry(0.008, 0.008, 0.3, 6), beltMat, n),              // hoist belt R\n    inst(new THREE.BoxGeometry(0.34, 0.05, 0.28), darkMat, n),                       // gripper\n    inst(new RoundedBoxGeometry(0.42, 0.33, 0.39, 3, 0.03), foupMat, n),             // FOUP shell (~420 x 390 x 335 mm)\n    inst(new THREE.BoxGeometry(0.2, 0.025, 0.2), lidMat, n),                         // FOUP top robotic flange\n    inst(new THREE.BoxGeometry(0.03, 0.29, 0.35), lidMat, n),                        // FOUP door (front face)\n    inst(new THREE.BoxGeometry(0.035, 0.8, 0.55), bodyMat, n),                       // front cover\n    inst(new THREE.BoxGeometry(0.035, 0.8, 0.55), bodyMat, n),                       // rear cover\n')
hook = r'''
const pf = TR.port_foups;
const portFoup = new THREE.InstancedMesh(new RoundedBoxGeometry(0.42, 0.33, 0.39, 3, 0.03), foupMat, pf.length);
const portLid = new THREE.InstancedMesh(new THREE.BoxGeometry(0.2, 0.025, 0.2), lidMat, pf.length);
const portWafer = new THREE.InstancedMesh(waferGeo, waferMat, pf.length);
portFoup.castShadow = true; scene.add(portFoup); scene.add(portLid); scene.add(portWafer);
const lampCol = [new THREE.Color(0x35c46b), new THREE.Color(0xf0a92b), new THREE.Color(0x3d8bff)];
function drawFrame(k) {
  const n = TR.nveh;
  for (let i = 0; i < n; i++) parts.forEach(p => p.setMatrixAt(i, hidden));
  for (const r of TR.frames[k]) {
    const [i, x, z, a, h, foup, st] = r;
    const cx = Math.cos(a), cz = -Math.sin(a);
    setPart(0, i, x, RAIL_H, z, a);
    setPart(1, i, x, RAIL_H - 0.32, z, a);
    setPart(2, i, x, RAIL_H - 0.40, z, a);
    setPart(3, i, x + Math.sin(a) * 0.29, RAIL_H - 0.27, z + Math.cos(a) * 0.29, a);
    setPart(10, i, x + cx * 0.51, RAIL_H - 0.55, z + cz * 0.51, a);
    setPart(11, i, x - cx * 0.51, RAIL_H - 0.55, z - cz * 0.51, a);
    const bx = cx * 0.13, bz = cz * 0.13, bl = 0.02 + h;
    setPart(4, i, x + bx, RAIL_H - 0.49 - bl / 2, z + bz, a, bl / 0.3);
    setPart(5, i, x - bx, RAIL_H - 0.49 - bl / 2, z - bz, a, bl / 0.3);
    setPart(6, i, x, RAIL_H - 0.535 - h, z, a);
    if (foup) { const fy = RAIL_H - 0.735 - h;
      setPart(7, i, x, fy, z, a); setPart(8, i, x, fy + 0.18, z, a);
      setPart(9, i, x + cx * 0.215, fy, z + cz * 0.215, a); setPart(12, i, x, fy, z, a); }
    tint.setXYZ(i, lampCol[st].r, lampCol[st].g, lampCol[st].b);
  }
  pf.forEach((q, j) => {
    const on = k >= q[1] && k < q[2], P = TR.ports[q[0]];
    if (on) { m4.makeTranslation(P[0], 1.065, P[1]); portFoup.setMatrixAt(j, m4); portWafer.setMatrixAt(j, m4); m4.makeTranslation(P[0], 1.245, P[1]); portLid.setMatrixAt(j, m4); }
    else { portFoup.setMatrixAt(j, hidden); portLid.setMatrixAt(j, hidden); portWafer.setMatrixAt(j, hidden); }
  });
  portFoup.instanceMatrix.needsUpdate = true; portLid.instanceMatrix.needsUpdate = true; portWafer.instanceMatrix.needsUpdate = true;
  parts.forEach(p => { p.instanceMatrix.needsUpdate = true; }); tint.needsUpdate = true;
}
scene.traverse(o => { const ms = Array.isArray(o.material) ? o.material : (o.material ? [o.material] : []);
  for (const m of ms) if ('envMapIntensity' in m && m !== waferMat) m.envMapIntensity = (m.metalness > 0.5 ? 0.7 : 0.25); });
window.nFrames = TR.frames.length;
window.renderAt = (k, cam) => {
  drawFrame(Math.min(k, TR.frames.length - 1));
  camera.fov = cam.fov || 50; camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  camera.position.set(cam.px, cam.py, cam.pz); camera.lookAt(cam.tx, cam.ty, cam.tz);
  renderer.render(scene, camera); return true;
};
window.__ready = true;
'''
tail = "addEventListener('resize', resize); resize(); draw(); requestAnimationFrame(loop);"
sub(tail, "addEventListener('resize', resize); resize();" + hook)
sub("setView(2); playing = true;", "playing = false; if (0) setView(2);")
open('closeup-traj.html', 'w', encoding='utf-8').write(src)
print('ok')
