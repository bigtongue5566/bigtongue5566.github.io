"""Reopen the delivered Blender file and render Hall 1 from reference directions.
Run: blender --background dist/Taipei101.blend --python scripts/review_model.py
Review images contain only our generated geometry, no Google imagery.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes.get('TAIPEI 101 · Xinyi District')
assert scene is not None, 'Missing demo scene'
bpy.context.window.scene = scene
meshes = [o for o in scene.objects if o.type == 'MESH']
hall = [o for o in meshes if o.get('landmark') == 'twtc' and o.get('layer') == 'Surroundings']
night = [o for o in meshes if o.get('night_only')]
assert hall and night, 'Hall and night lighting must survive reopening'
for obj in meshes:
    assert all(math.isfinite(c) for v in obj.data.vertices for c in (obj.matrix_world @ v.co))
tip = max((obj.matrix_world @ v.co).z for obj in meshes if obj.get('landmark') == 'taipei101' for v in obj.data.vertices)
assert abs(tip-508)<.02
review = ROOT/'dist'/'review'
review.mkdir(exist_ok=True)
camera=scene.camera
camera.data.type='ORTHO'
camera.data.ortho_scale=320
scene.cycles.samples=16
scene.render.resolution_x=1280
scene.render.resolution_y=960
target=Vector((-275,10,24))
views={
    'hall1-south':(-275,-450,360),
    'hall1-west':(-700,10,420),
    'hall1-plan':(-275,9.99,750),
}
for name,position in views.items():
    camera.location=position
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(review/(name+'.png'))
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        bpy.ops.render.render(write_still=True)
report={'reopened':True,'scene':scene.name,'scenes_in_file':len(bpy.data.scenes),
        'mesh_count':len(meshes),'hall1_mesh_count':len(hall),'night_mesh_count':len(night),
        'tower_tip_m':tip,'all_vertices_finite':True,'reference_view_renders':list(views)}
(ROOT/'dist'/'blend-reopen-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BLEND_REOPEN_AND_HALL_REVIEW_OK',json.dumps(report))
