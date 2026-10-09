"""Original Taipei 101 / Xinyi maquette. Run inside Blender 5.2+.
Metres: X east, Y north, Z up. Published tip height: 508 m.
Widths, neighbouring heights, landscaping and facade details are approximate.
"""
import argparse
import json
import math
import random
import sys
import traceback
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--render', action='store_true')
parser.add_argument('--output', type=Path, default=ROOT / 'dist')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT = args.output.resolve()
ASSETS = OUT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
STATUS = OUT / 'job-status.json'


def status(state, **data):
    STATUS.write_text(json.dumps({'state': state, **data}, ensure_ascii=False, indent=2), encoding='utf-8')


status('running')
random.seed(101)
scene = bpy.data.scenes.new('TAIPEI 101 · Xinyi District')
if bpy.context.window:
    bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collections = {}
for name in ['Architecture','Surroundings','Streets','Landscape','Details','Foundation','Lighting']:
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    collections[name] = col
geometry = defaultdict(lambda: [[], []])
materials = {}


def material(name, color, roughness=.7, metallic=0, glow=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (*color,1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    if glow:
        shader.inputs['Emission Color'].default_value = (1,.63,.27,1)
        shader.inputs['Emission Strength'].default_value = .12
    materials[name] = mat
    return name


glass = material('Jade curtain wall',(.105,.34,.34),.25,.4)
dark = material('Deep jade glazing',(.075,.22,.24),.3,.35)
silver = material('Pale aluminium',(.58,.68,.65),.42,.5)
trim = material('Dark structural ribs',(.14,.25,.25),.45,.35)
stone = material('Warm limestone',(.73,.71,.63))
ivory = material('Ivory concrete',(.82,.8,.72))
rose = material('TWTC rose stone',(.52,.31,.29))
roof = material('Patinated green roof',(.24,.47,.4))
hall_roof = material('TWTC dark vaulted roof',(.105,.135,.155),.6,.15)
hall_skylight = material('TWTC roof lights',(.32,.49,.5),.35,.2)
cityglass = material('Neighbour glass',(.25,.37,.38),.3,.25)
asphalt = material('Road asphalt',(.24,.29,.3),.95)
paving = material('Pale stone paving',(.65,.67,.62))
line = material('Traffic markings',(.82,.82,.69))
grass = material('Muted lawn',(.37,.46,.32))
leaves = [material('Tree canopy '+str(i),c) for i,c in enumerate([(.22,.35,.27),(.29,.4,.29),(.36,.45,.31)])]
bark = material('Tree bark',(.29,.25,.2))
base = material('Maquette foundation',(.61,.65,.61))
light = material('Warm window lights',(.88,.69,.42),.42,glow=True)
night_warm = material('Night warm windows',(.12,.15,.13),.5,glow=True)
night_cool = material('Night cool windows',(.1,.16,.16),.5,glow=True)
night_edge = material('Night facade edges',(.16,.2,.2),.5,glow=True)
for name,color in [(night_cool,(.48,.83,1,1)),(night_edge,(.63,.88,.83,1))]:
    shader = next(n for n in materials[name].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Emission Color'].default_value = color


def mesh(vertices, faces, mat, layer='Architecture', landmark='taipei101'):
    vs,fs = geometry[layer,landmark,mat]
    offset = len(vs)
    vs.extend(vertices)
    fs.extend(tuple(i+offset for i in face) for face in faces)


def box(cx,cy,z,w,d,h,mat,layer='Architecture',landmark='taipei101',angle=0):
    c,s=math.cos(angle),math.sin(angle)
    vertices=[(cx+c*x-s*y,cy+s*x+c*y,zz) for zz in [z,z+h]
              for x,y in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
    mesh(vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,layer,landmark)


def chamfer(w,d,cut=.12):
    x,y=w/2,d/2
    cx,cy=w*cut,d*cut
    return [(-x+cx,-y),(x-cx,-y),(x,-y+cy),(x,y-cy),(x-cx,y),(-x+cx,y),(-x,y-cy),(-x,-y+cy)]


def frustum(cx,cy,z0,z1,w0,w1,d0,d1,mat,landmark='taipei101',layer='Architecture'):
    vertices=[(cx+x,cy+y,z) for z,w,d in [(z0,w0,d0),(z1,w1,d1)] for x,y in chamfer(w,d)]
    faces=[tuple(reversed(range(8))),tuple(range(8,16))]
    faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    mesh(vertices,faces,mat,layer,landmark)


def cylinder(cx,cy,z,r,h,mat,layer='Details',landmark='context',count=16):
    vertices=[(cx+r*math.cos(i*math.tau/count),cy+r*math.sin(i*math.tau/count),zz)
              for zz in [z,z+h] for i in range(count)]
    faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh(vertices,faces,mat,layer,landmark)


def beam(a,b,r,mat,landmark='taipei101',layer='Architecture'):
    a,b=Vector(a),Vector(b)
    direction=(b-a).normalized()
    u=direction.cross(Vector((0,0,1)))
    if u.length<.01:
        u=direction.cross(Vector((0,1,0)))
    u.normalize()
    v=direction.cross(u).normalized()
    vertices=[tuple(p+r*(math.cos(i*math.tau/6)*u+math.sin(i*math.tau/6)*v)) for p in [a,b] for i in range(6)]
    faces=[tuple(reversed(range(6))),tuple(range(6,12))]
    faces += [(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    mesh(vertices,faces,mat,layer,landmark)


def lit_window(cx,cy,z0,z1,w0,w1,d0,d1,u,half_width,side,mat,landmark):
    sign = -1 if side in [0,2] else 1
    vertices = []
    for zz,w,d,du in [(z0,w0,d0,-half_width),(z0,w0,d0,half_width),
                       (z1,w1,d1,half_width),(z1,w1,d1,-half_width)]:
        if side<2:
            vertices.append((cx+u*w+du,cy+sign*(d/2+.23),zz))
        else:
            vertices.append((cx+sign*(w/2+.23),cy+u*d+du,zz))
    face=(0,1,2,3) if side in [0,3] else (3,2,1,0)
    mesh(vertices,[face],mat,'Lighting',landmark)


def lit_ring(z,w,d,landmark='taipei101'):
    points = chamfer(w,d)
    for i,(x,y) in enumerate(points):
        xx,yy = points[(i+1)%len(points)]
        beam((x,y,z),(xx,yy,z),.27,night_edge,landmark,'Lighting')


def cladding(z0,z1,w0,w1,d0,d1,landmark='taipei101',cx=0,cy=0,layer='Architecture',floors=8):
    for i in range(1,floors):
        t=i/floors
        w,d=w0+(w1-w0)*t,d0+(d1-d0)*t
        z=z0+(z1-z0)*t
        frustum(cx,cy,z-.14,z+.14,w+.3,w+.3,d+.3,d+.3,silver,landmark,layer)
    for side in range(4):
        for i in range(17):
            u=(i/16-.5)*.75
            sign=-1 if side in [0,2] else 1
            if side<2:
                a,b=(cx+w0*u,cy+sign*(d0/2+.18),z0),(cx+w1*u,cy+sign*(d1/2+.18),z1)
            else:
                a,b=(cx+sign*(w0/2+.18),cy+d0*u,z0),(cx+sign*(w1/2+.18),cy+d1*u,z1)
            beam(a,b,.15,silver,landmark,layer)


road_count = 0


def road(a,b,width):
    global road_count
    # Crossed ribbons have distinct elevations to avoid coplanar triangles.
    height = .12 + road_count * .03
    road_count += 1
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    angle=math.atan2(dy,dx)
    box((a[0]+b[0])/2,(a[1]+b[1])/2,height,length,width,.13,asphalt,'Streets','roads',angle)
    for shift in [-.6,.6]:
        box((a[0]+b[0])/2-shift*math.sin(angle),(a[1]+b[1])/2+shift*math.cos(angle),.65+road_count*.004,length,.18,.025,line,'Streets','roads',angle)
    for t in range(10,int(length)-10,22):
        for offset in [-width*.25,width*.25]:
            x=a[0]+dx*t/length-offset*math.sin(angle)
            y=a[1]+dy*t/length+offset*math.cos(angle)
            box(x,y,.65+road_count*.004,7,.23,.025,line,'Streets','roads',angle)


def crossing(cx,cy,width=25,angle=0):
    for i in range(-5,6):
        box(cx+i*2.1*math.cos(angle),cy+i*2.1*math.sin(angle),.8,.9,width,.035,line,'Streets','roads',angle)


def tree(x,y,size=1):
    cylinder(x,y,.45,.48*size,6.7*size,bark,'Landscape','trees',8)
    for z,r in [(5.4,4.5),(8.2,4.1),(10.6,2.8)]:
        frustum(x,y,z*size,(z+2.9)*size,r*2*size,r*1.35*size,r*2*size,r*1.35*size,
                leaves[int(abs(x+y))%3],'trees','Landscape')


def neighbour(cx,cy,w,d,h,name,wall=ivory,glazing=cityglass):
    box(cx,cy,2.5,w,d,h,wall,'Surroundings',name)
    box(cx,cy,h+2.5,w+1.2,d+1.2,1.8,wall,'Surroundings',name)
    for z in range(7,int(h),5):
        for sy in [-1,1]:
            box(cx,cy+sy*(d/2+.08),z,w*.91,.12,2.1,glazing,'Surroundings',name)
        for sx in [-1,1]:
            box(cx+sx*(w/2+.08),cy,z,.12,d*.91,2.1,glazing,'Surroundings',name)
    box(cx+w*.22,cy,h+4,w*.3,d*.4,3,wall,'Surroundings',name)
    columns = max(3,min(14,int(min(w,d)/6)))
    seed = sum(ord(c) for c in name)
    for floor,z in enumerate(range(7,int(h),5)):
        for side in range(4):
            for col in range(columns):
                if (floor*11+col*7+side*5+seed)%13 not in [0,1,3,8]:
                    continue
                u = -.4+.8*(col+.5)/columns
                lit_window(cx,cy,z+.1,z+1.9,w,w,d,d,u,1.15,side,
                           night_cool if (floor+col)%4==0 else night_warm,name)


def twtc_hall():
    """Hall 1's covered atrium, terraced trading floors and south entrance.
    Shape checked against Earth plan and south/west/north/east obliques.
    Seven storeys are documented by TWTC; dimensions remain visual estimates.
    """
    cx,cy=-275,10
    widths=[216,204,191,177,164,151,151]
    souths=[-99,-94,-87,-79,-71,-63,-63]
    levels=[.7,8.7,13.7,18.7,23.7,28.7,33.7,38.7]
    for floor,(w,south,z0,z1) in enumerate(zip(widths,souths,levels,levels[1:])):
        # The central entrance is recessed; the covered interior stays solid.
        x=w/2; north=106; cut=8
        points=[(-x+cut,south),(-16,south),(-16,south+9),
                (16,south+9),(16,south),(x-cut,south),(x,south+cut),
                (x,north-cut),(x-cut,north),(-x+cut,north),
                (-x,north-cut),(-x,south+cut)]
        vertices=[(cx+xx,cy+yy,z) for z in [z0,z1] for xx,yy in points]
        count=len(points)
        faces=[tuple(reversed(range(count)))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        mesh(vertices,faces,rose,'Surroundings','twtc')
        mesh([(cx+xx,cy+yy,z1+.05) for xx,yy in points],
             [tuple(range(count))],roof,'Surroundings','twtc')
        # Continuous dark window bands broken by rose piers, on real step edges.
        for a,b in zip(points,points[1:]+points[:1]):
            ax,ay=a; bx,by=b
            length=math.hypot(bx-ax,by-ay)
            if length<18:
                continue
            nx,ny=(by-ay)/length,-(bx-ax)/length
            row=[(cx+ax+nx*.12,cy+ay+ny*.12,z0+1.35),
                 (cx+bx+nx*.12,cy+by+ny*.12,z0+1.35),
                 (cx+bx+nx*.12,cy+by+ny*.12,z1-1.15),
                 (cx+ax+nx*.12,cy+ay+ny*.12,z1-1.15)]
            mesh(row,[(0,1,2,3)],dark,'Surroundings','twtc')
            columns=max(1,int(length/12))
            for col in range(columns):
                t=(col+.5)/columns
                px,py=cx+ax+(bx-ax)*t,cy+ay+(by-ay)*t
                box(px,py,z0,1.8,1.8,z1-z0,rose,'Surroundings','twtc')
                if (floor*3+col)%4==0:
                    tangent=Vector((bx-ax,by-ay,0)).normalized()
                    centre=Vector((px+nx*.16,py+ny*.16,z0+2.5))
                    quad=[tuple(centre+tangent*dx+Vector((0,0,dz)))
                          for dx,dz in [(-2,-.7),(2,-.7),(2,.7),(-2,.7)]]
                    mesh(quad,[(0,1,2,3)],night_warm,'Lighting','twtc')
        # Repeated projecting piers have their own small green caps.
        piers=[(xx,south) for xx in [-82,-52,-27,27,52,82] if abs(xx)<x-8]
        piers += [(sx*(x-1.8),yy) for sx in [-1,1] for yy in [-51,-6,39,84]]
        for xx,yy in piers:
            box(cx+xx,cy+yy,z0,6.2,6.2,z1-z0+1.6,rose,'Surroundings','twtc')
            box(cx+xx,cy+yy,z1+1.61,5.3,5.3,.18,roof,'Surroundings','twtc')
        box(cx,cy+south+9.12,z0+.5,30,.18,z1-z0-.8,dark,'Surroundings','twtc')

    # A shallow barrel vault covers the central exhibition space, not a lawn.
    half_width=42; y0=cy-55; y1=cy+71; spring=39.1; rise=7.5
    segments=24
    def vault_point(i,y,lift=0):
        t=i*math.pi/segments
        return (cx-half_width*math.cos(t),y,spring+rise*math.sin(t)+lift)
    for i in range(segments):
        mesh([vault_point(i,y0),vault_point(i+1,y0),
              vault_point(i+1,y1),vault_point(i,y1)],[(0,1,2,3)],
             hall_roof,'Surroundings','twtc')
    for yy,reverse in [(y0,True),(y1,False)]:
        end=[vault_point(i,yy) for i in range(segments+1)]
        mesh(end,[tuple(reversed(range(len(end)))) if reverse else tuple(range(len(end)))],
             hall_roof,'Surroundings','twtc')
    for i in range(0,segments+1,3):
        beam(vault_point(i,y0,.08),vault_point(i,y1,.08),.08,trim,'twtc','Surroundings')
    for j in range(1,14):
        yy=y0+j*(y1-y0)/14
        for i in range(segments):
            beam(vault_point(i,yy,.08),vault_point(i+1,yy,.08),.06,trim,'twtc','Surroundings')
            if 2<i<21 and (i*7+j*11)%17 in [0,1]:
                mesh([vault_point(i+.12,yy+.3,.12),vault_point(i+.87,yy+.3,.12),
                      vault_point(i+.87,yy+3.8,.12),vault_point(i+.12,yy+3.8,.12)],
                     [(0,1,2,3)],hall_skylight,'Surroundings','twtc')
    # Roof plant belongs to the upper western terrace, not the centre.
    for yy in [-30,-9,12,33,54,75]:
        box(cx-61,cy+yy,39.0,8.5,9,2.5,ivory,'Surroundings','twtc')
        cylinder(cx-61,cy+yy,41.5,2.8,.45,trim,'Surroundings','twtc',12)
    # Dark central south entrance and its sloped canopy span the setbacks.
    canopy=[(cx-23,cy-106,6.5),(cx+23,cy-106,6.5),
            (cx+14,cy-54,38.9),(cx-14,cy-54,38.9)]
    mesh(canopy,[(0,1,2,3)],hall_roof,'Surroundings','twtc')
    for j in range(1,13):
        t=j/13; xx=23-9*t; yy=cy-106+52*t; zz=6.5+32.4*t
        beam((cx-xx,yy,zz+.1),(cx+xx,yy,zz+.1),.12,silver,'twtc','Surroundings')
    for j in range(7):
        box(cx,cy-107+j*.9,.7,44-j*.8,1.05,.15+j*.18,stone,'Surroundings','twtc')
    # Enclosed bridge across Shifu Road to the 101 shopping podium.
    box(-150,-25,14.2,60,8,1.0,stone,'Surroundings','twtc')
    box(-150,-25,18.2,60,8.4,.5,stone,'Surroundings','twtc')
    for yy in [-29,-21]:
        box(-150,yy,15.2,60,.18,3,dark,'Surroundings','twtc')


try:
    box(-90,85,-8,1170,1050,8,base,'Foundation','foundation')
    box(-90,85,0,1170,1050,.1,paving,'Foundation','foundation')
    for y in [-132,165,385]:
        road((-668,y),(490,y),34 if y==-132 else 27)
    for x in [-151,128,340]:
        road((x,-430),(x,603),30 if x==-151 else 26)
    road((-635,-430),(-125,603),34)
    road((-668,-330),(490,-330),18)
    for x in [-151,128,340]:
        for y in [-132,165,385]:
            crossing(x-22,y,24)
            crossing(x,y+24,24,math.pi/2)

    # Connected podium / west-north shopping mall.
    box(-35,15,.5,205,220,1.2,stone)
    box(-67,34,1.7,118,146,25,dark)
    box(-67,34,26.7,125,151,3.1,silver)
    for y in [-41,110]:
        for x in range(-125,-5,10):
            box(x,y,2.7,1.3,1.8,23,stone)
    for z in [8,15,22]:
        box(-67,-40.2,z,118,1,.45,silver)
    for x in [-111,-86,-61,-36]:
        frustum(x,44,30,35,24,16,127,114,roof)
    box(-58,-48,3,35,14,7,glass)

    # Lower shaft, coin transition, eight outward-flared bamboo sections.
    frustum(0,0,1.7,30,88,86,88,86,glass)
    frustum(0,0,30,119,86,59,86,59,glass)
    cladding(30,119,86,59,86,59,floors=21)
    for floor in range(21):
        z0=30+(floor+.22)*89/21
        z1=z0+2.05
        w0=86-(z0-30)*27/89
        w1=86-(z1-30)*27/89
        for side in range(4):
            for col in range(12):
                if (floor*7+col*3+side)%11 in [0,1,4]:
                    lit_window(0,0,z0,z1,w0,w1,w0,w1,(col-5.5)*.75/12,1.45,side,night_warm,'taipei101')
    frustum(0,0,119,127,60,74,60,74,trim)
    frustum(0,0,127,133,75,75,75,75,silver)
    frustum(0,0,133,136,74,56,74,56,dark)
    for tier in range(8):
        z=136+tier*36
        w0,w1=56-tier*.65,71-tier*.65
        frustum(0,0,z,z+31,w0,w1,w0,w1,glass)
        cladding(z,z+31,w0,w1,w0,w1)
        frustum(0,0,z+31,z+33,w1+2,w1+2,w1+2,w1+2,silver)
        frustum(0,0,z+33,z+36,w1,w0-.65,w1,w0-.65,dark)
        lit_ring(z+32.3,w1+2.6,w1+2.6)
        for floor in range(8):
            z0=z+(floor+.23)*31/8
            z1=z0+2.12
            ww0=w0+(w1-w0)*(z0-z)/31
            ww1=w0+(w1-w0)*(z1-z)/31
            for side in range(4):
                for col in range(14):
                    if (tier*11+floor*7+col*3+side*5)%13 in [0,1,4,7]:
                        lit_window(0,0,z0,z1,ww0,ww1,ww0,ww1,(col-6.5)*.75/14,.95,side,
                                   night_cool if (tier+floor+col)%5==0 else night_warm,'taipei101')
        for sx in [-1,1]:
            for sy in [-1,1]:
                beam((sx*w1*.37,sy*w1*.5,z+28),(sx*(w1*.37+2.5),sy*(w1*.5+3),z+34),1.15,silver)
                box(sx*w1*.34,sy*(w1/2+.33),z+30,3,.25,.7,light)
    for side in range(4):
        vertices=[]
        for depth in [0,1.7]:
            for i in range(48):
                a=i*math.tau/48
                x,y,z=12*math.cos(a),-39-depth,135+12*math.sin(a)
                theta=side*math.pi/2
                vertices.append((x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta),z))
        faces=[tuple(reversed(range(48))),tuple(range(48,96))]
        faces += [(i,(i+1)%48,(i+1)%48+48,i+48) for i in range(48)]
        mesh(vertices,faces,silver)
    frustum(0,0,424,435,51,43,51,43,dark)
    cladding(424,435,51,43,51,43,floors=3)
    frustum(0,0,435,449,42,32,42,32,glass)
    frustum(0,0,449,461,32,22,32,22,dark)
    frustum(0,0,461,470,22,13,22,13,silver)
    frustum(0,0,470,480,12,7,12,7,dark)
    frustum(0,0,480,508,5.5,.5,5.5,.5,silver)
    for z,w in [(435,43.5),(449,33),(461,23),(470,14)]:
        lit_ring(z,w,w)

    twtc_hall()
    neighbour(-465,-59,112,89,32,'ticc',rose,dark)
    for i in range(3):
        box(-465,-59,36+i*4,112-i*18,89-i*13,3.3,rose,'Surroundings','ticc')
    neighbour(-441,64,45,45,138,'trade',rose,cityglass)
    box(-441,64,142,46,46,4,roof,'Surroundings','trade')
    # Hyatt's stepped wings; north of Hall 1.
    neighbour(-267,261,167,91,53,'hyatt',stone,cityglass)
    neighbour(-267,266,69,65,74,'hyatt',stone,cityglass)
    for sx in [-1,1]:
        neighbour(-267+sx*66,266,34,74,63,'hyatt',stone,cityglass)
        frustum(-267+sx*66,266,69,76,34,15,62,25,ivory,'hyatt','Surroundings')
    frustum(-267,266,80,88,55,27,51,25,ivory,'hyatt','Surroundings')
    cylinder(-267,200,.45,27,.2,stone,'Surroundings','hyatt',48)
    for x,y,w,d in [(-184,493,174,34),(-250,451,40,70),(-118,451,40,70),(-184,532,96,32)]:
        neighbour(x,y,w,d,43,'cityhall',stone,cityglass)
    box(-184,441,.5,71,65,.15,paving,'Surroundings','cityhall')
    for x,y,w,d,h in [(230,253,107,103,32),(230,471,111,105,77),(416,242,95,96,104),(412,473,101,112,66)]:
        neighbour(x,y,w,d,h,'eastblock')
    neighbour(236,25,76,97,218,'easttower',cityglass,dark)
    vertices=[(198,-23.5,220.5),(274,-23.5,220.5),(274,73.5,220.5),(198,73.5,220.5),
              (198,-23.5,262),(274,-23.5,245),(274,73.5,245),(198,73.5,262)]
    mesh(vertices,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],cityglass,'Surroundings','easttower')
    for i,(x,y,w,d,h) in enumerate([(-480,-239,78,72,38),(-351,-239,92,73,45),(-235,-240,73,72,31),
                                    (-72,-238,100,70,39),(42,-239,55,74,55),(232,-240,79,71,86),
                                    (417,-240,93,86,44),(-435,-382,77,50,34),(-274,-382,118,53,18),
                                    (229,-382,81,53,31),(409,-382,105,59,47)]):
        neighbour(x,y,w,d,h,'southblock'+str(i),stone if i%3 else ivory)
    box(-15,-381,.35,179,76,.2,grass,'Landscape','park')
    box(-74,236,.4,138,126,.2,grass,'Landscape','plaza')
    for r in [21,31,46]:
        for i in range(64):
            a,b=i*math.tau/64,(i+1)*math.tau/64
            beam((73+r*math.cos(a),24+r*math.sin(a),.6),(73+r*math.cos(b),24+r*math.sin(b),.6),.38,ivory,'plaza','Details')
    for x in range(-620,450,28):
        for y in [-157,187,405]:
            if abs(x-(-635+(y+430)*510/1033))>24:
                tree(x,y,random.uniform(.75,1.15))
    for y in range(-400,590,30):
        for x in [-172,149,362]:
            if all(abs(y-r)>22 for r in [-132,165,385]) and not (x==-172 and -95<y<119):
                tree(x,y,random.uniform(.8,1.15))
    for x in range(-87,71,26):
        for y in [-399,-357,197,280]:
            tree(x,y,.92)
    for i in range(28):
        x,y=-596+i*36,-140 if i%2 else 174
        box(x,y,.4,4.6,2,1.2,ivory if i%3 else cityglass,'Details','traffic')
        box(x+.2,y,1.6,2.5,1.8,.75,dark,'Details','traffic')
    for x in range(-550,470,70):
        for y in [-159,189]:
            cylinder(x,y,.4,.25,8,trim,'Details','streetlights',8)
            box(x,y,8.4,3.2,.75,.3,light,'Details','streetlights')
            box(x,y,8.72,3.35,.83,.2,night_warm,'Lighting','streetlights')
    for r in [21,31]:
        for i in range(24):
            a,b=i*math.tau/24,(i+1)*math.tau/24
            beam((73+r*math.cos(a),24+r*math.sin(a),.9),
                 (73+r*math.cos(b),24+r*math.sin(b),.9),.45,night_edge,'plaza','Lighting')

    for (layer,landmark,mat),(vertices,faces) in geometry.items():
        data=bpy.data.meshes.new(landmark+'__'+mat)
        data.from_pydata(vertices,[],faces)
        data.update()
        obj=bpy.data.objects.new(landmark+'__'+mat,data)
        collections[layer].objects.link(obj)
        data.materials.append(materials[mat])
        obj['layer']=layer
        obj['landmark']=landmark
        obj['approximate']=True
        if layer=='Lighting':
            obj['night_only']=True
            obj.hide_render=True
    world=bpy.data.worlds.new('Taipei warm sky')
    scene.world=world
    world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs[0].default_value=(.88,.86,.79,1)
    bg.inputs[1].default_value=.75
    ld=bpy.data.lights.new('Late afternoon sun','SUN')
    ld.energy=2.5
    ld.angle=.11
    sun=bpy.data.objects.new('Late afternoon sun',ld)
    scene.collection.objects.link(sun)
    sun.rotation_euler=(math.radians(31),math.radians(-28),math.radians(-35))
    cd=bpy.data.cameras.new('Demo overview')
    camera=bpy.data.objects.new('Demo overview',cd)
    scene.collection.objects.link(camera)
    camera.location=(1180,-1410,1090)
    target=Vector((-125,80,185))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    cd.type='ORTHO'
    cd.ortho_scale=1430
    cd.clip_end=6000
    scene.camera=camera
    scene.render.engine='CYCLES'
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1800
    scene.render.resolution_y=1200
    scene.view_settings.view_transform='AgX'
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        bpy.ops.object.select_all(action='DESELECT')
        for col in collections.values():
            for obj in col.objects:
                obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(ASSETS/'taipei101.glb'),export_format='GLB',
                                  use_selection=True,use_active_scene=True,export_extras=True,
                                  export_cameras=False,export_lights=False)
    scene.render.filepath=str(ASSETS/'taipei101-preview.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Taipei101.blend'))
    summary={'scene':scene.name,'units':'metres','axes':{'X':'east','Y':'north','Z':'up'},
             'tower_tip_m':508,'tier_count':8,'approximate':True,'reference_date':'2026-10-10',
             'meshes':len(geometry),'vertices':sum(len(v[0]) for v in geometry.values()),
             'glb_bytes':(ASSETS/'taipei101.glb').stat().st_size,
             'landmarks':['taipei101','twtc','ticc','trade','hyatt','cityhall'],
             'hall1_revision':'Covered barrel vault; seven-storey terraced trading floors; recessed south entrance',
             'limits':'Exterior maquette; widths, facade details and surroundings approximate. No interiors.'}
    (ASSETS/'model-info.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.render:
        with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
            bpy.ops.render.render(write_still=True)
    status('complete',**summary)
    print('TAIPEI101_MODEL_READY',json.dumps(summary))
except Exception:
    status('failed',error=traceback.format_exc())
    raise
