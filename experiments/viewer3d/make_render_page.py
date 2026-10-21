"""Make closeup-render.html: closeup.html without UI, driven frame-by-frame from Playwright.
window.renderAt(t, cam) sets sim time t and camera {px,py,pz,tx,ty,tz,fov}, then renders once."""
src = open('closeup.html', encoding='utf-8').read()
src = src.replace('</style>', '  .panel { display: none !important; }\n</style>', 1)
hook = '''
window.renderInfo = () => { const b = busiest(); return { b, W, D, links: data.links.map(l => [...toXZ(l[0], l[1]), ...toXZ(l[2], l[3])]) }; };
window.renderAt = (tt, cam) => {
  t = tt; viewMode = -1; draw();
  camera.fov = cam.fov || 50; camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  camera.position.set(cam.px, cam.py, cam.pz); camera.lookAt(cam.tx, cam.ty, cam.tz);
  renderer.render(scene, camera); return true;
};
window.__ready = true;
'''
tail = "addEventListener('resize', resize); resize(); draw(); requestAnimationFrame(loop);"
assert tail in src
src = src.replace(tail, "addEventListener('resize', resize); resize(); draw();" + hook)
open('closeup-render.html', 'w', encoding='utf-8').write(src)
print('ok')
