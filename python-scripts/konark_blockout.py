# =============================================================================
#  KONARK SUN TEMPLE - Structural Blockout (Jagamohana + Chariot Base)
#  Kalinga 'Pidha Deula' style | metric units | low-poly primitives only
#
#  References used to derive the numbers:
#   - Wikipedia / UNESCO (whc.unesco.org/en/list/246): 24 wheels ~3 m dia,
#     jagamohana ~30 m walls, roof = three tiers of SIX pidhas each
#   - Sketchfab moniln (skfb.ly/pw7wx): overall massing & stepped pitha
#   - Sketchfab Logeswaran (skfb.ly/oI7oz): wheel = rim + extended axle hub,
#     8 thick primary spokes (45 deg) + 8 thin secondary spokes interleaved
#   - Scribd Konark golden-ratio study: PHI drives tier heights (h/PHI each
#     tier) and width taper (tier k ends at W / PHI^(2k/3), apex = W/PHI^2)
#
#  Collections produced:
#   [Konark_Main_Structure]    pitha + bada + pidha tiers + crown platform
#   [Konark_Wheels_Placements] 24 collection-instance empties (12 pairs)
#   [Konark_References]        > Konark_Wheel_Master (source wheel, excluded)
#
#  All meshes have rotation & scale applied (1,1,1). Safe to re-run.
# =============================================================================
import bpy
import math

PHI = (1 + 5 ** 0.5) / 2  # 1.6180339887

# ---------------------------------------------------------------- collections
def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

coll_main   = get_coll("Konark_Main_Structure")
coll_wheels = get_coll("Konark_Wheels_Placements")
coll_refs   = get_coll("Konark_References")
wheel_coll  = bpy.data.collections.get("Konark_Wheel_Master")
if wheel_coll is None:
    wheel_coll = bpy.data.collections.new("Konark_Wheel_Master")
    coll_refs.children.link(wheel_coll)

# ------------------------------------------------------------------- material
mat = bpy.data.materials.get("Konark_Sandstone")
if mat is None:
    mat = bpy.data.materials.new("Konark_Sandstone")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.42, 0.27, 0.17, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.95

# -------------------------------------------------------------------- helpers
def move_to(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)

def finalize(obj, coll):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    move_to(obj, coll)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def add_box(name, dx, dy, dz, loc, coll, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dx, dy, dz)
    finalize(o, coll)
    return o

# =============================================================================
#  A. MULTI-TIERED PITHA  (stepped square stone platform, 48 m -> 42 m)
# =============================================================================
pitha_steps = [(48.0, 1.2), (45.0, 1.2), (42.0, 1.2)]
z = 0.0
for i, (w, h) in enumerate(pitha_steps):
    add_box(f"Pitha_Step_{i+1}", w, w, h, (0, 0, z + h / 2), coll_main)
    z += h
PITHA_TOP  = z                       # 3.6 m
PITHA_HALF = pitha_steps[0][0] / 2   # 24 m

# East entrance staircase - chariot FRONT (-X), perpendicular to wheel rows
add_box("Pitha_East_Stairs", 6.0, 8.0, 1.8, (-(PITHA_HALF + 3.0), 0, 0.9), coll_main)

# =============================================================================
#  B. JAGAMOHANA  (Pidha Deula: bada + 3 tiers x 6 pidhas, PHI-tapered)
# =============================================================================
BADA_W = 30.0
BADA_H = BADA_W / 2.0                # walls twice as wide as high -> 15 m
add_box("Jagamohana_Bada", BADA_W, BADA_W, BADA_H, (0, 0, z + BADA_H / 2), coll_main)
z += BADA_H

H1       = 7.2
tier_h   = [H1, H1 / PHI, H1 / PHI ** 2]                       # 7.20 / 4.45 / 2.75
tier_end = [BADA_W / PHI ** (2 * (k + 1) / 3) for k in range(3)]  # 21.75 / 15.78 / 11.46
RECESS_H = 1.1
PIDHAS   = 6

start_w = BADA_W
for t in range(3):
    end_w  = tier_end[t]
    step_h = tier_h[t] / PIDHAS
    for i in range(PIDHAS):
        f = i / (PIDHAS - 1)
        w = start_w + (end_w - start_w) * f
        w *= 1.03 if i % 2 else 1.0            # alternating lip (terrace read)
        add_box(f"Pidha_T{t+1}_{i+1}", w, w, step_h, (0, 0, z + step_h / 2), coll_main)
        z += step_h
    if t < 2:                                   # kanthi recess between tiers
        rw = end_w * 0.80
        add_box(f"Kanthi_Recess_{t+1}", rw, rw, RECESS_H, (0, 0, z + RECESS_H / 2), coll_main)
        z += RECESS_H
        start_w = end_w * 0.94

# Flat circular crown platform (ready for Amalaka / Kalasha)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=tier_end[2] / 2 * 0.72,
                                    depth=0.9, location=(0, 0, z + 0.45))
o = bpy.context.active_object
o.name = "Crown_Platform_Base"
finalize(o, coll_main)
z += 0.9
print("Jagamohana apex: %.2f m" % z)           # ~36.1 m

# =============================================================================
#  C. KONARK WHEEL MASTER  (outer dia 2.97 m, axle along Y) + 24 INSTANCES
# =============================================================================
parts = []
def reg(o):
    o.data.materials.clear()
    o.data.materials.append(mat)
    move_to(o, wheel_coll)
    parts.append(o)
    return o

bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=8,
    major_radius=1.35, minor_radius=0.135, rotation=(math.pi / 2, 0, 0))
reg(bpy.context.active_object).name = "Wheel_Rim"

bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.30, depth=0.55,
                                    rotation=(math.pi / 2, 0, 0))
reg(bpy.context.active_object).name = "Wheel_Hub"

bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.14, depth=1.35,
                                    rotation=(math.pi / 2, 0, 0))
reg(bpy.context.active_object).name = "Wheel_Axle"

R_MID = 0.775                                   # spoke centre radius
for k in range(8):
    a = math.radians(45 * k)
    bpy.ops.mesh.primitive_cube_add(size=1,     # thick primary spoke
        location=(R_MID * math.cos(a), 0, R_MID * math.sin(a)), rotation=(0, -a, 0))
    o = bpy.context.active_object
    o.name = f"Wheel_Spoke_Main_{k+1}"
    o.scale = (1.05, 0.20, 0.26)
    reg(o)

    b = a + math.radians(22.5)                  # thin secondary spoke
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=1.0,
        location=(R_MID * math.cos(b), 0, R_MID * math.sin(b)),
        rotation=(0, math.pi / 2 - b, 0))
    o = bpy.context.active_object
    o.name = f"Wheel_Spoke_Thin_{k+1}"
    reg(o)

    bpy.ops.mesh.primitive_cube_add(size=1,     # decorative rim knob
        location=(1.53 * math.cos(b), 0, 1.53 * math.sin(b)), rotation=(0, -b, 0))
    o = bpy.context.active_object
    o.name = f"Wheel_Rim_Knob_{k+1}"
    o.scale = (0.16, 0.12, 0.20)
    reg(o)

bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
wheel = bpy.context.active_object
wheel.name = "Konark_Wheel"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# --- 24 instances (12 pairs) along the +/-Y chariot sides -------------------
R_OUT = 1.485
y_off = PITHA_HALF + 0.35
xs = [-20.0 + i * (40.0 / 11.0) for i in range(12)]
n = 0
for side in (1, -1):
    for x in xs:
        n += 1
        e = bpy.data.objects.new(f"Wheel_Instance_{n:02d}", None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = wheel_coll
        e.location = (x, side * y_off, R_OUT)   # rim touches ground plane
        e.empty_display_size = 0.4
        coll_wheels.objects.link(e)

# exclude master source collection from the view layer (instances stay live)
def find_lc(lc, name):
    if lc.collection.name == name:
        return lc
    for ch in lc.children:
        r = find_lc(ch, name)
        if r:
            return r

lc = find_lc(bpy.context.view_layer.layer_collection, "Konark_Wheel_Master")
if lc:
    lc.exclude = True

# =============================================================================
#  D. CROWN (MASTAKA): Beki -> Amalaka -> Khapuri -> Kalasha
# =============================================================================
def finalize_main(obj):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    move_to(obj, coll_main)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

cz = z  # top of Crown_Platform_Base (~36.1)

bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=3.0, depth=1.4, location=(0, 0, cz + 0.7))
o = bpy.context.active_object; o.name = "Crown_Beki"; finalize_main(o); cz += 1.4

am_r = BADA_W / PHI ** 3 / 2                 # amalaka radius from golden ratio (~3.54)
bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=10,
    major_radius=am_r * 0.72, minor_radius=am_r * 0.33, location=(0, 0, cz + 1.1))
o = bpy.context.active_object; o.name = "Crown_Amalaka"; finalize_main(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=am_r * 0.75, depth=2.2, location=(0, 0, cz + 1.1))
o = bpy.context.active_object; o.name = "Crown_Amalaka_Core"; finalize_main(o); cz += 2.2

bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=2.2, location=(0, 0, cz))
o = bpy.context.active_object; o.name = "Crown_Khapuri"; o.scale = (1, 1, 0.55)
finalize_main(o); cz += 1.2

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.0, location=(0, 0, cz + 0.8))
o = bpy.context.active_object; o.name = "Crown_Kalasha_Body"; o.scale = (1, 1, 1.1); finalize_main(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.35, depth=0.9, location=(0, 0, cz + 2.0))
o = bpy.context.active_object; o.name = "Crown_Kalasha_Neck"; finalize_main(o)
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.5, radius2=0.0, depth=1.1, location=(0, 0, cz + 2.9))
o = bpy.context.active_object; o.name = "Crown_Kalasha_Tip"; finalize_main(o)

# =============================================================================
#  E. SEVEN HORSES (master blockout + instances flanking the east stairs)
# =============================================================================
horse_coll = bpy.data.collections.get("Konark_Horse_Master")
if horse_coll is None:
    horse_coll = bpy.data.collections.new("Konark_Horse_Master")
    coll_refs.children.link(horse_coll)
coll_horses = get_coll("Konark_Horses_Placements")

hparts = []
def hpart(name, scale=None):
    o = bpy.context.active_object
    o.name = name
    if scale:
        o.scale = scale
    o.data.materials.clear()
    o.data.materials.append(mat)
    move_to(o, horse_coll)
    hparts.append(o)
    return o

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3));  hpart("Horse_Pedestal", (2.6, 1.3, 0.6))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.85)); hpart("Horse_Body", (2.3, 0.85, 1.0))
for i, (lx, ly) in enumerate([(0.85, 0.28), (0.85, -0.28), (-0.85, 0.28), (-0.85, -0.28)]):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(lx, ly, 0.98))
    hpart(f"Horse_Leg_{i+1}", (0.22, 0.22, 0.85))
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.0, 0, 2.75), rotation=(0, -0.55, 0))
hpart("Horse_Neck", (0.55, 0.42, 1.5))
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.65, 0, 3.35), rotation=(0, 0.35, 0))
hpart("Horse_Head", (0.85, 0.32, 0.42))
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.35, 0, 2.2), rotation=(0, 0.5, 0))
hpart("Horse_Tail", (0.7, 0.18, 0.3))

bpy.ops.object.select_all(action='DESELECT')
for o in hparts:
    o.select_set(True)
bpy.context.view_layer.objects.active = hparts[0]
bpy.ops.object.join()
horse = bpy.context.active_object
horse.name = "Konark_Horse"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

for i, y in enumerate([-7.5, -12.0, -16.5, -21.0, 7.5, 12.0, 16.5]):
    e = bpy.data.objects.new(f"Horse_Instance_{i+1:02d}", None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = horse_coll
    e.location = (-33.5, y, 0.0)
    e.empty_display_size = 0.4
    coll_horses.objects.link(e)

lc = find_lc(bpy.context.view_layer.layer_collection, "Konark_Horse_Master")
if lc:
    lc.exclude = True

# =============================================================================
#  F. REKHA DEULA (main sanctum tower, originally ~69 m) + PLATFORM EXTENSION
# =============================================================================
def add_box_at(name, dx, dy, dz, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dx, dy, dz)
    finalize_main(o)
    return o

# F1. extend the chariot platform westward (deul shares the base)
zz = 0.0
for i, (wy, h, x0, x1) in enumerate([(48.0, 1.2, 24.0, 60.0),
                                     (45.0, 1.2, 22.5, 58.5),
                                     (42.0, 1.2, 21.0, 57.0)]):
    add_box_at(f"Pitha_West_Ext_{i+1}", x1-x0, wy, h, ((x0+x1)/2, 0, zz + h/2))
    zz += h

# F2. deul: bada + curvilinear gandi + mastaka
DX, DW = 40.0, 24.0
zz = PITHA_TOP
DBH = 12.5
add_box_at("Deul_Bada", DW, DW, DBH, (DX, 0, zz + DBH/2))
add_box_at("Deul_Bada_PagaX", DW + 1.6, DW * 0.42, DBH, (DX, 0, zz + DBH/2))
add_box_at("Deul_Bada_PagaY", DW * 0.42, DW + 1.6, DBH, (DX, 0, zz + DBH/2))
zz += DBH

N, GH = 14, 40.0
lh = GH / N
for i in range(N):
    t = (i + 1) / N
    w = DW * (1 - 0.68 * t ** 2.4)          # rekha curve: slow start, sharp top
    add_box_at(f"Deul_Gandi_{i+1:02d}", w, w, lh, (DX, 0, zz + lh/2))
    if i % 2 == 0:
        add_box_at(f"Deul_Gandi_{i+1:02d}_PagaX", w + 1.2, w * 0.40, lh, (DX, 0, zz + lh/2))
        add_box_at(f"Deul_Gandi_{i+1:02d}_PagaY", w * 0.40, w + 1.2, lh, (DX, 0, zz + lh/2))
    zz += lh

bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=4.0, depth=2.0, location=(DX, 0, zz + 1.0))
o = bpy.context.active_object; o.name = "Deul_Beki"; finalize_main(o); zz += 2.0
dam_r = DW / PHI ** 2 / 2 * 1.55
bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=10,
    major_radius=dam_r * 0.72, minor_radius=dam_r * 0.33, location=(DX, 0, zz + 1.6))
o = bpy.context.active_object; o.name = "Deul_Amalaka"; finalize_main(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=dam_r * 0.75, depth=3.2, location=(DX, 0, zz + 1.6))
o = bpy.context.active_object; o.name = "Deul_Amalaka_Core"; finalize_main(o); zz += 3.2
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=3.2, location=(DX, 0, zz))
o = bpy.context.active_object; o.name = "Deul_Khapuri"; o.scale = (1, 1, 0.55); finalize_main(o); zz += 1.8
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.5, location=(DX, 0, zz + 1.2))
o = bpy.context.active_object; o.name = "Deul_Kalasha_Body"; o.scale = (1, 1, 1.1); finalize_main(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.5, depth=1.3, location=(DX, 0, zz + 3.0))
o = bpy.context.active_object; o.name = "Deul_Kalasha_Neck"; finalize_main(o)
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.7, radius2=0.0, depth=1.6, location=(DX, 0, zz + 4.3))
o = bpy.context.active_object; o.name = "Deul_Kalasha_Tip"; finalize_main(o)

# F3. re-space the 24 wheels along the full (extended) chariot base
xs_full = [-19.0 + i * (74.0 / 11.0) for i in range(12)]
insts = sorted([ob for ob in bpy.data.objects if ob.name.startswith("Wheel_Instance_")],
               key=lambda ob: ob.name)
for i, e in enumerate(insts):
    side = 1 if i < 12 else -1
    e.location.x = xs_full[i % 12]
    e.location.y = side * abs(e.location.y)

# =============================================================================
#  G. NATA MANDIR (dance hall - roof collapsed; walls, piers & pillars remain)
# =============================================================================
NX = -52.0
zz = 0.0
for i, (w, h) in enumerate([(22.0, 1.0), (20.0, 1.0), (18.0, 1.0)]):
    add_box_at(f"NataMandir_Pitha_{i+1}", w, w, h, (NX, 0, zz + h/2)); zz += h
add_box_at("NataMandir_Floor", 16.0, 16.0, 0.4, (NX, 0, zz + 0.2)); zz += 0.4

WT, WH_wall, SEG = 1.2, 5.5, 4.6
for nm, cx, cy, dx, dy in [("N1", -4.7, 7.4, SEG, WT), ("N2", 4.7, 7.4, SEG, WT),
                           ("S1", -4.7, -7.4, SEG, WT), ("S2", 4.7, -7.4, SEG, WT),
                           ("E1", -7.4, -4.7, WT, SEG), ("E2", -7.4, 4.7, WT, SEG),
                           ("W1", 7.4, -4.7, WT, SEG), ("W2", 7.4, 4.7, WT, SEG)]:
    add_box_at(f"NataMandir_Wall_{nm}", dx, dy, WH_wall, (NX + cx, cy, zz + WH_wall/2))
for sx in (-1, 1):
    for sy in (-1, 1):
        add_box_at(f"NataMandir_Pier_{'N' if sy>0 else 'S'}{'W' if sx>0 else 'E'}",
                   2.2, 2.2, WH_wall, (NX + sx*7.0, sy*7.0, zz + WH_wall/2))
for i, (px, py) in enumerate([(-3, -3), (-3, 3), (3, -3), (3, 3)]):
    add_box_at(f"NataMandir_Pillar_{i+1}", 1.3, 1.3, 7.5, (NX + px, py, zz + 3.75))
add_box_at("NataMandir_East_Stairs", 5.0, 7.0, 1.6, (NX - 13.5, 0, 0.8))

# =============================================================================
#  H. COMPOUND WALL, EAST GATEWAY & SUBSIDIARY SHRINES
# =============================================================================
coll_comp = get_coll("Konark_Compound")

def add_box_comp(name, dx, dy, dz, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dx, dy, dz)
    o.data.materials.clear(); o.data.materials.append(mat)
    move_to(o, coll_comp)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o

WX, WY, WT2, WH2, GATE = 88.0, 58.0, 1.6, 3.5, 7.0
add_box_comp("Wall_North", 2*WX, WT2, WH2, (0, WY, WH2/2))
add_box_comp("Wall_South", 2*WX, WT2, WH2, (0, -WY, WH2/2))
add_box_comp("Wall_West", WT2, 2*WY + WT2, WH2, (WX, 0, WH2/2))
seg = (2*WY - 2*GATE) / 2
add_box_comp("Wall_East_N", WT2, seg, WH2, (-WX, GATE + seg/2, WH2/2))
add_box_comp("Wall_East_S", WT2, seg, WH2, (-WX, -GATE - seg/2, WH2/2))
for s in (1, -1):
    add_box_comp(f"Gate_Pier_{'N' if s>0 else 'S'}", 2.4, 2.4, 6.5, (-WX, s*GATE, 3.25))
add_box_comp("Gate_Lintel", 2.8, 2*GATE + 2.4, 1.4, (-WX, 0, 7.2))
for sx in (1, -1):
    for sy in (1, -1):
        add_box_comp(f"Wall_Corner_{'E' if sx<0 else 'W'}{'N' if sy>0 else 'S'}",
                     4.0, 4.0, 5.0, (sx*WX, sy*WY, 2.5))

def mini_shrine(tag, cx, cy):
    add_box_comp(f"Shrine_{tag}_Base", 9.0, 9.0, 1.0, (cx, cy, 0.5))
    add_box_comp(f"Shrine_{tag}_Body", 6.5, 6.5, 4.0, (cx, cy, 3.0))
    sz = 5.0
    for i, w in enumerate([6.0, 5.0, 4.0, 3.0]):
        add_box_comp(f"Shrine_{tag}_Pidha_{i+1}", w, w, 0.8, (cx, cy, sz + 0.4)); sz += 0.8
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.1, depth=0.6, location=(cx, cy, sz + 0.3))
    o = bpy.context.active_object; o.name = f"Shrine_{tag}_Beki"
    o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.8, radius2=0.0, depth=1.4, location=(cx, cy, sz + 1.3))
    o = bpy.context.active_object; o.name = f"Shrine_{tag}_Kalasha"
    o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)

mini_shrine("North", 0.0, 36.0)
mini_shrine("South", 0.0, -36.0)

# =============================================================================
#  I. REFINEMENT PASS - central temple (jagamohana), from HD photo references
#     (1822 measured elevation, floor plan, front-view photos in /Images)
#     Replaces the simple roof/crown with: bada moldings + pagas + doorways,
#     riser+lip pidhas, statue terraces, ghanta-dominated mastaka, dhvaja.
# =============================================================================
for ob in list(bpy.data.objects):
    if ob.name.startswith(("Pidha_T", "Kanthi_Recess_", "Crown_")):
        bpy.data.objects.remove(ob, do_unlink=True)

def cylm(name, r, d, loc, v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc)
    o = bpy.context.active_object
    o.name = name
    finalize_main(o)
    return o

# --- I1. bada details -------------------------------------------------------
BW, Z0 = 30.0, PITHA_TOP
mz = Z0
for i, (grow, h) in enumerate([(1.4, 0.6), (1.0, 0.5), (0.6, 0.4)]):
    add_box_at(f"JM_Pabhaga_{i+1}", BW + grow, BW + grow, h, (0, 0, mz + h/2)); mz += h
add_box_at("JM_Bandhana", BW + 0.8, BW + 0.8, 0.7, (0, 0, Z0 + 7.5))
add_box_at("JM_Paga_X",  BW + 1.8, BW * 0.38, 15.0, (0, 0, Z0 + 7.5))
add_box_at("JM_Paga_Y",  BW * 0.38, BW + 1.8, 15.0, (0, 0, Z0 + 7.5))
add_box_at("JM_Paga_X2", BW + 0.9, BW * 0.78, 15.0, (0, 0, Z0 + 7.5))
add_box_at("JM_Paga_Y2", BW * 0.78, BW + 0.9, 15.0, (0, 0, Z0 + 7.5))
for tag, px, py, dx, dy in [("E", -1, 0, 1, 0), ("W", 1, 0, 1, 0),
                            ("N", 0, 1, 0, 1), ("S", 0, -1, 0, 1)]:
    off = BW/2 + 0.9 + 0.55
    add_box_at(f"JM_Door_{tag}", 1.6 if dx else 5.5, 1.6 if dy else 5.5, 9.0,
               (px * off, py * off, Z0 + 4.5))
    for j, (w, h) in enumerate([(4.6, 0.9), (3.4, 0.9), (2.2, 0.9)]):
        add_box_at(f"JM_Door_{tag}_Corbel_{j+1}",
                   1.3 if dx else w, 1.3 if dy else w, h,
                   (px * (off - 0.15*(j+1)), py * (off - 0.15*(j+1)),
                    Z0 + 9.0 + j * 0.9 + h/2))

# --- I2. gandi: riser+lip pidhas, walkable statue terraces -------------------
z = Z0 + 15.0
tier_h_r   = [7.2, 7.2/PHI, 7.2/PHI**2]
tier_end_r = [BW / PHI**(2*(k+1)/3) for k in range(3)]
TERRACE_H, LIP = 1.6, 1.7
start_w = BW
terr = []
for t in range(3):
    end_w  = tier_end_r[t]
    step_h = tier_h_r[t] / 6
    rh, lh = step_h * 0.55, step_h * 0.45
    for i in range(6):
        f = i / 5
        w = start_w + (end_w - start_w) * f
        add_box_at(f"Pidha_T{t+1}_{i+1}_Riser", w - LIP, w - LIP, rh, (0, 0, z + rh/2)); z += rh
        add_box_at(f"Pidha_T{t+1}_{i+1}_Lip",   w, w, lh, (0, 0, z + lh/2)); z += lh
    if t < 2:
        nxt = end_w * 0.86
        add_box_at(f"Kanthi_Wall_{t+1}", nxt, nxt, TERRACE_H, (0, 0, z + TERRACE_H/2))
        terr.append((z, end_w, nxt))
        z += TERRACE_H
        start_w = end_w * 0.94
top_w = tier_end_r[2]

for t, (tz, ew, nw) in enumerate(terr):        # musician statue blocks
    r = (nw/2 + ew/2) / 2
    for side in range(4):
        for i in range(5 - t):
            f = (i + 0.5) / (5 - t) - 0.5
            d = f * (ew - 3.0)
            loc = [(d, r), (d, -r), (r, d), (-r, d)][side]
            add_box_at(f"JM_Statue_T{t+1}_S{side}_{i+1}", 0.8, 0.8, 1.8,
                       (loc[0], loc[1], tz + 0.9))

# --- I3. mastaka: corner beasts, ghanta dome, upper stack, dhvaja ------------
c = top_w/2 - 1.0
for sx in (1, -1):
    for sy in (1, -1):
        add_box_at(f"JM_CornerBeast_{'N' if sy>0 else 'S'}{'W' if sx>0 else 'E'}",
                   1.5, 0.9, 1.6, (sx*c, sy*c, z + 0.8))
add_box_at("Crown_Cap_Square", top_w * 0.92, top_w * 0.92, 0.7, (0, 0, z + 0.35)); z += 0.7
cylm("Crown_Platform_Base", top_w/2 * 0.74, 0.7, (0, 0, z + 0.35)); z += 0.7
cylm("Crown_Beki", 2.7, 1.3, (0, 0, z + 0.65)); z += 1.3

GR = top_w/2 * 0.86
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=GR, location=(0, 0, z))
o = bpy.context.active_object; o.name = "Crown_Ghanta"; o.scale = (1, 1, 0.60); finalize_main(o)
for i, f in enumerate([0.35, 0.62, 0.84]):
    rr = GR * (1 - f*f) ** 0.5 * 1.01
    bpy.ops.mesh.primitive_torus_add(major_segments=28, minor_segments=6,
        major_radius=rr, minor_radius=0.14, location=(0, 0, z + GR*0.60*f))
    o = bpy.context.active_object; o.name = f"Crown_Ghanta_Rib_{i+1}"; finalize_main(o)
z += GR * 0.60

cylm("Crown_Beki2", 1.5, 1.0, (0, 0, z + 0.5)); z += 1.0
bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=8,
    major_radius=1.6, minor_radius=0.75, location=(0, 0, z + 0.75))
o = bpy.context.active_object; o.name = "Crown_Amalaka"; finalize_main(o)
cylm("Crown_Amalaka_Core", 1.5, 1.5, (0, 0, z + 0.75)); z += 1.5
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.35, location=(0, 0, z))
o = bpy.context.active_object; o.name = "Crown_Khapuri"; o.scale = (1, 1, 0.5); finalize_main(o); z += 0.68
bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=7, radius=0.75, location=(0, 0, z + 0.55))
o = bpy.context.active_object; o.name = "Crown_Kalasha_Body"; o.scale = (1, 1, 1.15); finalize_main(o)
cylm("Crown_Kalasha_Neck", 0.28, 0.6, (0, 0, z + 1.45), v=12)
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.38, radius2=0.0, depth=0.8, location=(0, 0, z + 2.1))
o = bpy.context.active_object; o.name = "Crown_Kalasha_Tip"; finalize_main(o)
cylm("Crown_Dhvaja_Rod", 0.09, 3.2, (0, 0, z + 3.5), v=8)
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=0.12,
    location=(0, 0, z + 4.6), rotation=(1.5708, 0, 0))
o = bpy.context.active_object; o.name = "Crown_Dhvaja_Wheel"; finalize_main(o)

# =============================================================================
#  J. REFINEMENT PASS 2 - wheels & Nata Mandir, from HD photo references
#     NOTE: master collections are UNLINKED from the scene (data-only) instead
#     of excluded - excluding a collection removes it from the depsgraph and
#     kills its instances.
# =============================================================================
# unlink masters from the scene tree (instances keep working, masters invisible)
for _nm in ("Konark_Wheel_Master", "Konark_Horse_Master"):
    _c = bpy.data.collections[_nm]
    if _c.name in [ch.name for ch in coll_refs.children]:
        coll_refs.children.unlink(_c)

# --- J1. wheel master rebuild (flat rim band, flared spokes, beads, hub) -----
_old = bpy.data.objects.get("Konark_Wheel")
if _old:
    bpy.data.objects.remove(_old, do_unlink=True)

wparts = []
def wreg(o, name):
    o.name = name
    o.data.materials.clear(); o.data.materials.append(mat)
    move_to(o, wheel_coll)
    wparts.append(o)
    return o

def wapply(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# rim: flat band - create axis-up, squash along local Z, THEN rotate to face Y
bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=8,
    major_radius=1.28, minor_radius=0.24)
o = bpy.context.active_object
o.scale = (1, 1, 0.55)
o.rotation_euler = (math.pi/2, 0, 0)
wreg(o, "W_RimBand"); wapply(o)
for nm2, mr in [("W_RimOuterRing", 1.50), ("W_RimInnerRing", 1.06)]:
    bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=6,
        major_radius=mr, minor_radius=0.07, rotation=(math.pi/2, 0, 0))
    wreg(bpy.context.active_object, nm2)

bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.45, depth=0.55, rotation=(math.pi/2, 0, 0))
o = wreg(bpy.context.active_object, "W_HubMedallion"); wapply(o)
bpy.ops.mesh.primitive_torus_add(major_segments=24, minor_segments=6,
    major_radius=0.52, minor_radius=0.05, rotation=(math.pi/2, 0, 0))
wreg(bpy.context.active_object, "W_HubRing")
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.15, depth=1.4, rotation=(math.pi/2, 0, 0))
o = wreg(bpy.context.active_object, "W_Axle"); wapply(o)
for s in (1, -1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.24, depth=0.10,
        location=(0, s*0.72, 0), rotation=(math.pi/2, 0, 0))
    o = wreg(bpy.context.active_object, f"W_AxleCap_{1 if s>0 else 2}"); wapply(o)

for k in range(8):
    a = math.radians(45 * k)
    ca, sa = math.cos(a), math.sin(a)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.78*ca, 0, 0.78*sa), rotation=(0, -a, 0))
    o = bpy.context.active_object; o.scale = (0.95, 0.16, 0.22)
    wreg(o, f"W_Spoke_{k+1}_Blade"); wapply(o)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(1.13*ca, 0, 1.13*sa), rotation=(0, -a, 0))
    o = bpy.context.active_object; o.scale = (0.34, 0.15, 0.38)
    wreg(o, f"W_Spoke_{k+1}_Flare"); wapply(o)
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.17, depth=0.26,
        location=(0.82*ca, 0, 0.82*sa), rotation=(math.pi/2, 0, 0))
    o = wreg(bpy.context.active_object, f"W_Spoke_{k+1}_Medallion"); wapply(o)

for k in range(8):
    b = math.radians(45 * k + 22.5)
    cb, sb = math.cos(b), math.sin(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.95,
        location=(0.78*cb, 0, 0.78*sb), rotation=(0, math.pi/2 - b, 0))
    o = wreg(bpy.context.active_object, f"W_Thin_{k+1}_Core"); wapply(o)
    for j, r in enumerate([0.45, 0.62, 0.79, 0.96, 1.13]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.07,
            location=(r*cb, 0, r*sb))
        wreg(bpy.context.active_object, f"W_Thin_{k+1}_Bead_{j+1}")

for k in range(8):
    cc = math.radians(45 * k + 22.5)
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(1.58*math.cos(cc), 0, 1.58*math.sin(cc)), rotation=(0, -cc, 0))
    o = bpy.context.active_object; o.scale = (0.18, 0.14, 0.24)
    wreg(o, f"W_RimKnob_{k+1}"); wapply(o)

bpy.ops.object.select_all(action='DESELECT')
for o in wparts:
    o.select_set(True)
bpy.context.view_layer.objects.active = wparts[0]
bpy.ops.object.join()
wheel = bpy.context.active_object
wheel.name = "Konark_Wheel"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# --- J2. Nata Mandir rebuild: open pier grid on molded platform --------------
for ob in list(bpy.data.objects):
    if ob.name.startswith("NataMandir_"):
        bpy.data.objects.remove(ob, do_unlink=True)

NX = -52.0
nz = 0.0
for i, (w, h) in enumerate([(22.0, 0.8), (20.6, 1.4), (22.4, 0.5),
                            (20.2, 0.9), (21.6, 0.5)]):
    add_box_at(f"NataMandir_Pitha_{i+1}", w, w, h, (NX, 0, nz + h/2)); nz += h
add_box_at("NataMandir_Floor", 18.0, 18.0, 0.4, (NX, 0, nz + 0.2)); nz += 0.4

for tag, px, py in [("E", -1, 0), ("W", 1, 0), ("N", 0, 1), ("S", 0, -1)]:
    for s in range(6):
        sh = nz / 6
        off = 11.0 + (6 - s - 1) * 0.9 - 0.45
        if px:
            add_box_at(f"NataMandir_Stair_{tag}_{s+1}", 0.9, 5.0, sh*(s+1),
                       (NX + px*off, 0, sh*(s+1)/2))
        else:
            add_box_at(f"NataMandir_Stair_{tag}_{s+1}", 5.0, 0.9, sh*(s+1),
                       (NX, py*off, sh*(s+1)/2))

for ix, gx in enumerate([-6.45, -2.15, 2.15, 6.45]):
    for iy, gy in enumerate([-6.45, -2.15, 2.15, 6.45]):
        inner = ix in (1, 2) and iy in (1, 2)
        ph = 7.5 if inner else 5.5
        nm2 = f"NataMandir_Pier_{ix}{iy}"
        add_box_at(nm2, 2.0, 2.0, ph, (NX + gx, gy, nz + ph/2))
        add_box_at(nm2 + "_Base", 2.5, 2.5, 0.5, (NX + gx, gy, nz + 0.25))
        add_box_at(nm2 + "_Capital", 2.7, 2.7, 0.45, (NX + gx, gy, nz + ph + 0.225))

# =============================================================================
#  K. MAYADEVI TEMPLE (ruin, walls only) - SW of the main deul
# =============================================================================
MX, MY = 38.0, -36.0

add_box_comp("Mayadevi_Terrace", 30.0, 20.0, 0.35, (MX, MY, 0.175))
add_box_comp("Mayadevi_Plinth", 22.0, 14.0, 1.1, (MX, MY, 0.9))
ptop = 1.45

for s in range(3):
    add_box_comp(f"Mayadevi_PlinthStair_{s+1}", 0.7, 4.0, 1.1 - s*0.35,
                 (MX - 11.35 - s*0.7, MY, 0.35 + (1.1 - s*0.35)/2))
for s in range(2):
    add_box_comp(f"Mayadevi_TerraceStair_{s+1}", 0.6, 5.0, 0.35 - s*0.17,
                 (MX - 15.3 - s*0.6, MY, (0.35 - s*0.17)/2))

WT3, WH_hall, WH_sanc = 1.0, 4.2, 4.8
HX, SX = MX - 4.0, MX + 4.5

add_box_comp("Mayadevi_Hall_WallN", 11.0, WT3, WH_hall, (HX, MY + 5.0, ptop + WH_hall/2))
add_box_comp("Mayadevi_Hall_WallS", 11.0, WT3, WH_hall, (HX, MY - 5.0, ptop + WH_hall/2))
for s in (1, -1):
    add_box_comp(f"Mayadevi_Hall_WallE_{1 if s>0 else 2}", WT3, 3.5, WH_hall,
                 (HX - 5.0, MY + s*3.25, ptop + WH_hall/2))
    add_box_comp(f"Mayadevi_Hall_WallW_{1 if s>0 else 2}", WT3, 3.5, WH_hall,
                 (HX + 5.0, MY + s*3.25, ptop + WH_hall/2))

add_box_comp("Mayadevi_Sanc_WallN", 9.0, WT3, WH_sanc, (SX, MY + 4.0, ptop + WH_sanc/2))
add_box_comp("Mayadevi_Sanc_WallS", 9.0, WT3, WH_sanc, (SX, MY - 4.0, ptop + WH_sanc/2))
add_box_comp("Mayadevi_Sanc_WallW", WT3, 8.0, WH_sanc, (SX + 4.0, MY, ptop + WH_sanc/2))

bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.4, depth=0.8,
                                    location=(SX, MY, ptop + 0.4))
o = bpy.context.active_object
o.name = "Mayadevi_Pedestal"
o.data.materials.clear(); o.data.materials.append(mat)
move_to(o, coll_comp)

for i, dx in enumerate([-3.2, 0.0, 3.2]):
    for s, tg in [(1, "N"), (-1, "S")]:
        add_box_comp(f"Mayadevi_Hall_Paga_{tg}{i+1}", 2.2, 0.4, WH_hall - 0.7,
                     (HX + dx, MY + s*5.7, ptop + (WH_hall - 0.7)/2))
for i, dx in enumerate([-2.4, 2.4]):
    for s, tg in [(1, "N"), (-1, "S")]:
        add_box_comp(f"Mayadevi_Sanc_Paga_{tg}{i+1}", 2.0, 0.4, WH_sanc - 0.7,
                     (SX + dx, MY + s*4.7, ptop + (WH_sanc - 0.7)/2))
add_box_comp("Mayadevi_Sanc_Paga_W", 0.4, 2.4, WH_sanc - 0.7,
             (SX + 4.7, MY, ptop + (WH_sanc - 0.7)/2))

for i, (bx, by, bz, ddx, ddy, ddz) in enumerate([
        (HX - 3.5, MY + 5.0, WH_hall, 1.8, 1.1, 0.9), (HX + 1.0, MY + 5.0, WH_hall, 1.4, 1.0, 0.6),
        (HX - 1.0, MY - 5.0, WH_hall, 2.0, 1.1, 0.8), (HX + 3.8, MY - 5.0, WH_hall, 1.2, 1.0, 0.5),
        (HX - 5.0, MY + 3.0, WH_hall, 1.1, 1.6, 0.7), (HX - 5.0, MY - 2.6, WH_hall, 1.1, 1.3, 0.5),
        (SX + 1.5, MY + 4.0, WH_sanc, 1.7, 1.1, 0.8), (SX - 1.8, MY - 4.0, WH_sanc, 1.5, 1.1, 0.6),
        (SX + 4.0, MY + 1.2, WH_sanc, 1.1, 1.8, 0.9), (SX + 4.0, MY - 2.0, WH_sanc, 1.1, 1.4, 0.5)]):
    add_box_comp(f"Mayadevi_Rubble_{i+1:02d}", ddx, ddy, ddz, (bx, by, ptop + bz + ddz/2))

# =============================================================================
#  L. FINAL POLISH - Surya niches, unique wheel spins, materials, sunrise rig
# =============================================================================
# chlorite (dark green stone) for the Surya statues
chl = bpy.data.materials.get("Konark_Chlorite")
if chl is None:
    chl = bpy.data.materials.new("Konark_Chlorite")
    chl.use_nodes = True
    _b = chl.node_tree.nodes.get("Principled BSDF")
    _b.inputs["Base Color"].default_value = (0.045, 0.075, 0.055, 1.0)
    _b.inputs["Roughness"].default_value = 0.55

def add_box_mat(name, dx, dy, dz, loc, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dx, dy, dz)
    o.data.materials.clear(); o.data.materials.append(m)
    move_to(o, coll_main)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o

# L1. Surya statue niches on the deul raha pagas (N, S, W)
paga_off = DW/2 + 0.8
nz2 = PITHA_TOP + 8.5
for tag, px, py in [("W", 1, 0), ("N", 0, 1), ("S", 0, -1)]:
    fx, fy = DX + px*paga_off, py*paga_off
    add_box_mat(f"Deul_SuryaNiche_{tag}_Frame",
                1.0 if px else 3.2, 3.2 if px else 1.0, 4.6, (fx, fy, nz2), mat)
    add_box_mat(f"Deul_SuryaNiche_{tag}_Cap",
                1.2 if px else 2.4, 2.4 if px else 1.2, 0.7, (fx, fy, nz2 + 2.65), mat)
    sx2, sy2 = DX + px*(paga_off + 0.35), py*(paga_off + 0.35)
    add_box_mat(f"Deul_Surya_{tag}_Body", 0.5 if px else 1.1, 1.1 if px else 0.5,
                2.6, (sx2, sy2, nz2 - 0.5), chl)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.28,
                                         location=(sx2, sy2, nz2 + 1.1))
    o = bpy.context.active_object; o.name = f"Deul_Surya_{tag}_Head"
    o.data.materials.clear(); o.data.materials.append(chl); move_to(o, coll_main)

# L2. unique per-wheel rotation about the axle
for i, e in enumerate(sorted([ob for ob in bpy.data.objects
                              if ob.name.startswith("Wheel_Instance_")],
                             key=lambda ob: ob.name)):
    e.rotation_euler = (0, math.radians((i * 17.0) % 45.0), 0)

# L3. procedural khondalite sandstone
nt = mat.node_tree
nodes, links = nt.nodes, nt.links
bsdf = nodes.get("Principled BSDF")
tex = nodes.get("KN_Noise") or nodes.new("ShaderNodeTexNoise"); tex.name = "KN_Noise"
tex.location = (-600, 300)
tex.inputs["Scale"].default_value = 3.5
tex.inputs["Detail"].default_value = 8.0
ramp = nodes.get("KN_Ramp") or nodes.new("ShaderNodeValToRGB"); ramp.name = "KN_Ramp"
ramp.location = (-350, 300)
ramp.color_ramp.elements[0].position = 0.30
ramp.color_ramp.elements[0].color = (0.16, 0.09, 0.055, 1)
ramp.color_ramp.elements[1].position = 0.75
ramp.color_ramp.elements[1].color = (0.48, 0.30, 0.18, 1)
links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
bmp = nodes.get("KN_Bump") or nodes.new("ShaderNodeBump"); bmp.name = "KN_Bump"
bmp.location = (-350, -50)
bmp.inputs["Strength"].default_value = 0.35
bn = nodes.get("KN_BumpNoise") or nodes.new("ShaderNodeTexNoise"); bn.name = "KN_BumpNoise"
bn.location = (-600, -50)
bn.inputs["Scale"].default_value = 55.0
links.new(bn.outputs["Fac"], bmp.inputs["Height"])
links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])

# L4. ground plane
if not bpy.data.objects.get("Konark_Ground"):
    bpy.ops.mesh.primitive_plane_add(size=420, location=(0, 0, -0.05))
    g = bpy.context.active_object; g.name = "Konark_Ground"
    gm = bpy.data.materials.new("Konark_GroundSand")
    gm.use_nodes = True
    gb = gm.node_tree.nodes.get("Principled BSDF")
    gb.inputs["Base Color"].default_value = (0.42, 0.33, 0.22, 1)
    gb.inputs["Roughness"].default_value = 1.0
    g.data.materials.append(gm)
    move_to(g, coll_refs)

# L5. sunrise sun (east = -X) + sky fill
sun = bpy.data.objects.get("Sun")
if sun is None:
    _l = bpy.data.objects.get("Light")
    if _l: bpy.data.objects.remove(_l, do_unlink=True)
    sd = bpy.data.lights.new("Sun", 'SUN')
    sun = bpy.data.objects.new("Sun", sd)
    bpy.context.scene.collection.objects.link(sun)
sun.data.energy = 6.0
sun.data.color = (1.0, 0.72, 0.5)
sun.data.angle = math.radians(1.5)
sun.location = (0, 0, 60)
sun.rotation_euler = (0, math.radians(-80), 0)
world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.35, 0.48, 0.7, 1.0)
bg.inputs["Strength"].default_value = 0.5

# L6. hero camera (SE, sunrise side) - long clip so nothing is cut off
cam = bpy.data.objects.get("Camera")
if cam is None:
    cd = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cd)
    bpy.context.scene.collection.objects.link(cam)
cam.location = (-115.0, -75.0, 30.0)
cam.data.lens = 40
cam.data.clip_end = 3000
target = bpy.data.objects.get("Konark_CamTarget")
if target is None:
    target = bpy.data.objects.new("Konark_CamTarget", None)
    bpy.context.scene.collection.objects.link(target)
target.location = (8.0, 0.0, 20.0)
for c in list(cam.constraints):
    cam.constraints.remove(c)
tc = cam.constraints.new('TRACK_TO')
tc.target = target
tc.track_axis = 'TRACK_NEGATIVE_Z'
tc.up_axis = 'UP_Y'
bpy.context.scene.camera = cam

# To render:  scene.render.filepath = "...png"; bpy.ops.render.render(write_still=True)
# =============================================================================
#  M. ARUNA STAMBHA (chlorite charioteer pillar, east axis) + SUNRISE ANIMATION
# =============================================================================
AX, AY = -72.0, 0.0
az = 0.0
for i, (w, h) in enumerate([(4.2, 0.35), (3.4, 0.35), (2.6, 0.35)]):
    add_box_comp(f"ArunaStambha_Plinth_{i+1}", w, w, h, (AX, AY, az + h/2)); az += h
add_box_comp("ArunaStambha_Pedestal", 1.7, 1.7, 0.5, (AX, AY, az + 0.25)); az += 0.5
add_box_comp("ArunaStambha_Pedestal2", 1.4, 1.4, 0.7, (AX, AY, az + 0.35)); az += 0.7

def _chl_obj(o):
    o.data.materials.clear(); o.data.materials.append(chl)
    move_to(o, coll_comp)
    return o

bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.45, radius2=0.36,
                                depth=9.0, location=(AX, AY, az + 4.5))
o = bpy.context.active_object; o.name = "ArunaStambha_Shaft"; _chl_obj(o); az += 9.0
bpy.ops.mesh.primitive_torus_add(major_segments=20, minor_segments=8,
    major_radius=0.42, minor_radius=0.14, location=(AX, AY, az + 0.1))
o = bpy.context.active_object; o.name = "ArunaStambha_Lotus"; _chl_obj(o)
bpy.ops.mesh.primitive_cube_add(size=1, location=(AX, AY, az + 0.525))
o = bpy.context.active_object; o.name = "ArunaStambha_Abacus"
o.scale = (1.15, 1.15, 0.35); _chl_obj(o)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
az += 0.7
bpy.ops.mesh.primitive_cube_add(size=1, location=(AX, AY, az + 0.36))
o = bpy.context.active_object; o.name = "Aruna_Body"; o.scale = (0.55, 0.42, 0.72); _chl_obj(o)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.mesh.primitive_cube_add(size=1, location=(AX - 0.25, AY, az + 0.55))
o = bpy.context.active_object; o.name = "Aruna_Arms"; o.scale = (0.3, 0.5, 0.3); _chl_obj(o)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.17,
                                     location=(AX, AY, az + 0.92))
o = bpy.context.active_object; o.name = "Aruna_Head"; _chl_obj(o)

# --- sunrise animation: sun climbs out of the east over 250 frames ----------
scn = bpy.context.scene
scn.frame_start, scn.frame_end = 1, 250
sun.animation_data_clear()
sun.data.animation_data_clear()

def _sunkey(frame, rot_y_deg, energy, color):
    scn.frame_set(frame)
    sun.rotation_euler = (0, math.radians(rot_y_deg), 0)
    sun.keyframe_insert("rotation_euler", frame=frame)
    sun.data.energy = energy
    sun.data.color = color
    sun.data.keyframe_insert("energy", frame=frame)
    sun.data.keyframe_insert("color", frame=frame)

_sunkey(1,   -89.0, 1.0,  (1.0, 0.45, 0.25))   # first light on the east gate
_sunkey(90,  -78.0, 5.0,  (1.0, 0.62, 0.40))   # golden hour
_sunkey(180, -65.0, 8.0,  (1.0, 0.80, 0.62))
_sunkey(250, -50.0, 10.0, (1.0, 0.92, 0.82))   # morning
scn.frame_set(90)

# =============================================================================
#  N. CARVED FRIEZES - displacement-based relief panels over the carved zones
#     (chariot platform faces, jagamohana jangha, Nata Mandir platform band)
# =============================================================================
fz = bpy.data.collections.get("Konark_Friezes")
if fz is None:
    fz = bpy.data.collections.new("Konark_Friezes")
    bpy.context.scene.collection.children.link(fz)

t_coarse = bpy.data.textures.get("Frieze_Coarse")
if t_coarse is None:
    t_coarse = bpy.data.textures.new("Frieze_Coarse", 'STUCCI')
    t_coarse.noise_scale = 0.9
    t_coarse.turbulence = 6.0
t_fine = bpy.data.textures.get("Frieze_Fine")
if t_fine is None:
    t_fine = bpy.data.textures.new("Frieze_Fine", 'CLOUDS')
    t_fine.noise_scale = 0.35
    t_fine.noise_depth = 4

def frieze_panel(name, length, height, loc, axis, sign):
    xs = max(24, min(400, int(length / 0.22)))
    ys = max(4,  min(60,  int(height / 0.11)))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=xs, y_subdivisions=ys, size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (length, height, 1)
    if axis == 'Y':
        o.rotation_euler = (math.pi/2 * (-sign), 0, 0)
    else:
        o.rotation_euler = (math.pi/2 * (-sign), 0, math.pi/2)
    o.data.materials.clear(); o.data.materials.append(mat)
    move_to(o, fz)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    m1 = o.modifiers.new("Relief_Coarse", 'DISPLACE')
    m1.texture = t_coarse; m1.strength = 0.20; m1.mid_level = 0.5; m1.texture_coords = 'GLOBAL'
    m2 = o.modifiers.new("Relief_Fine", 'DISPLACE')
    m2.texture = t_fine; m2.strength = 0.07; m2.mid_level = 0.5; m2.texture_coords = 'GLOBAL'
    return o

def fz_strip(name, dx, dy, dz, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (dx, dy, dz)
    o.data.materials.clear(); o.data.materials.append(mat)
    move_to(o, fz)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o

# N1. chariot platform: 3 steps x 4 sides + molding courses
for si, (hw, zc, x0, x1) in enumerate([(24.0, 0.6, -24.0, 60.0),
                                       (22.5, 1.8, -22.5, 58.5),
                                       (21.0, 3.0, -21.0, 57.0)]):
    L, cx = x1 - x0, (x0 + x1) / 2
    for sign, tg in [(1, "N"), (-1, "S")]:
        frieze_panel(f"Frieze_Pitha{si+1}_{tg}", L, 1.12, (cx, sign*(hw + 0.04), zc), 'Y', sign)
    frieze_panel(f"Frieze_Pitha{si+1}_E", 2*hw, 1.12, (x0 - 0.04, 0, zc), 'X', -1)
    frieze_panel(f"Frieze_Pitha{si+1}_W", 2*hw, 1.12, (x1 + 0.04, 0, zc), 'X', 1)
    fz_strip(f"Frieze_Course_{si+1}_N", L, 0.18, 0.14, (cx,  hw - 0.02, zc + 0.62))
    fz_strip(f"Frieze_Course_{si+1}_S", L, 0.18, 0.14, (cx, -hw + 0.02, zc + 0.62))

# N2. jagamohana bada: lower + upper jangha relief + register lines
face = BW/2 + 0.02
for zc, ph, t2 in [(6.05, 2.6, "LJ"), (11.3, 3.4, "UJ")]:
    for sign, tg in [(1, "N"), (-1, "S")]:
        frieze_panel(f"Frieze_Bada_{t2}_{tg}", BW, ph, (0, sign*face, zc), 'Y', sign)
    frieze_panel(f"Frieze_Bada_{t2}_E", BW, ph, (-face, 0, zc), 'X', -1)
    frieze_panel(f"Frieze_Bada_{t2}_W", BW, ph, ( face, 0, zc), 'X', 1)
for zc in (5.3, 9.7):
    for sign in (1, -1):
        fz_strip(f"Frieze_BadaCourse_{'N' if sign>0 else 'S'}_{int(zc*10)}",
                 BW + 0.15, 0.16, 0.12, (0, sign*(BW/2), 3.6 + zc))

# N3. Nata Mandir carved platform band
for sign, tg in [(1, "N"), (-1, "S")]:
    frieze_panel(f"Frieze_NM_{tg}", 20.6, 1.3, (NX, sign*10.34, 1.5), 'Y', sign)
frieze_panel("Frieze_NM_E", 20.6, 1.3, (NX - 10.34, 0, 1.5), 'X', -1)
frieze_panel("Frieze_NM_W", 20.6, 1.3, (NX + 10.34, 0, 1.5), 'X', 1)

# N4. material tuning for close-range reads
nt.nodes["KN_Noise"].inputs["Scale"].default_value = 7.0
_r = nt.nodes["KN_Ramp"].color_ramp
_r.elements[0].color = (0.24, 0.145, 0.09, 1)
_r.elements[0].position = 0.22
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.75

# =============================================================================
#  O. CYCLES MICRO-DISPLACEMENT - render-quality carved stone (Blender 5.x)
#     Frieze panels switch from Displace modifiers to adaptive subdivision +
#     true shader displacement computed at render time.
# =============================================================================
scn2 = bpy.context.scene
scn2.render.engine = 'CYCLES'
scn2.cycles.dicing_rate = 1.0
scn2.cycles.max_subdivisions = 8
scn2.cycles.samples = 128
scn2.cycles.use_denoising = True
try:      # enable GPU if present
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dev_type in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if [d for d in prefs.devices if d.type != 'CPU']:
                for d in prefs.devices: d.use = True
                scn2.cycles.device = 'GPU'
                break
        except Exception:
            continue
except Exception:
    pass

carved = bpy.data.materials.get("Konark_Sandstone_Carved")
if carved is None:
    carved = mat.copy(); carved.name = "Konark_Sandstone_Carved"
carved.displacement_method = 'DISPLACEMENT'

cnt = carved.node_tree
cn, cl = cnt.nodes, cnt.links
cout = next(n for n in cn if n.type == 'OUTPUT_MATERIAL')
for n in [n for n in cn if n.name.startswith("CV_")]:
    cn.remove(n)

def _cv(kind, name, loc):
    n = cn.new(kind); n.name = name; n.location = loc; return n

cgeo = _cv("ShaderNodeNewGeometry", "CV_Geo", (-1100, -400))
c1 = _cv("ShaderNodeTexNoise", "CV_Coarse", (-900, -300))
c1.inputs["Scale"].default_value = 1.7
c1.inputs["Detail"].default_value = 7.0
c1.inputs["Roughness"].default_value = 0.62
cl.new(cgeo.outputs["Position"], c1.inputs["Vector"])
c2 = _cv("ShaderNodeTexNoise", "CV_Fine", (-900, -550))
c2.inputs["Scale"].default_value = 14.0
c2.inputs["Detail"].default_value = 8.0
cl.new(cgeo.outputs["Position"], c2.inputs["Vector"])
csep = _cv("ShaderNodeSeparateXYZ", "CV_Sep", (-900, -750))
cl.new(cgeo.outputs["Position"], csep.inputs["Vector"])
cmz = _cv("ShaderNodeMath", "CV_MulZ", (-720, -750)); cmz.operation = 'MULTIPLY'
cmz.inputs[1].default_value = 11.2
cl.new(csep.outputs["Z"], cmz.inputs[0])
csn = _cv("ShaderNodeMath", "CV_Sin", (-560, -750)); csn.operation = 'SINE'
cl.new(cmz.outputs[0], csn.inputs[0])
cab = _cv("ShaderNodeMath", "CV_Abs", (-400, -750)); cab.operation = 'ABSOLUTE'
cl.new(csn.outputs[0], cab.inputs[0])
cband = _cv("ShaderNodeMapRange", "CV_Band", (-240, -750))
cband.inputs["To Min"].default_value = 0.55
cl.new(cab.outputs[0], cband.inputs["Value"])
cm1 = _cv("ShaderNodeMath", "CV_MAdd", (-560, -420)); cm1.operation = 'MULTIPLY_ADD'
cm1.inputs[1].default_value = 0.75
cl.new(c1.outputs["Fac"], cm1.inputs[0])
cm2 = _cv("ShaderNodeMath", "CV_MulF", (-720, -560)); cm2.operation = 'MULTIPLY'
cm2.inputs[1].default_value = 0.25
cl.new(c2.outputs["Fac"], cm2.inputs[0])
cl.new(cm2.outputs[0], cm1.inputs[2])
cmb = _cv("ShaderNodeMath", "CV_MulB", (-400, -480)); cmb.operation = 'MULTIPLY'
cl.new(cm1.outputs[0], cmb.inputs[0])
cl.new(cband.outputs["Result"], cmb.inputs[1])
cdisp = _cv("ShaderNodeDisplacement", "CV_Disp", (-180, -480))
cdisp.inputs["Midlevel"].default_value = 0.5
cdisp.inputs["Scale"].default_value = 0.22
cl.new(cmb.outputs[0], cdisp.inputs["Height"])
cl.new(cdisp.outputs["Displacement"], cout.inputs["Displacement"])

# swap frieze panels: Displace mods -> adaptive subsurf + carved material
for o in fz.objects:
    if not o.name.startswith("Frieze_") or "Course" in o.name:
        continue
    if o.type != 'MESH' or len(o.data.polygons) < 50:
        continue
    for mmod in list(o.modifiers):
        if mmod.type == 'DISPLACE':
            o.modifiers.remove(mmod)
    if not any(mmod.type == 'SUBSURF' for mmod in o.modifiers):
        sub = o.modifiers.new("AdaptiveSub", 'SUBSURF')
        sub.subdivision_type = 'SIMPLE'
        sub.levels = 0
        sub.use_adaptive_subdivision = True
    o.data.materials.clear()
    o.data.materials.append(carved)

# =============================================================================
#  P. DETAIL PASS - torana gate, gajasimhas, door jambs, pilasters, niches,
#     and extended micro-displacement carving on structural elements
# =============================================================================
# P1. corbelled torana gate (replaces the simple gate)
for _nm in ("Gate_Pier_N", "Gate_Pier_S", "Gate_Lintel"):
    _o = bpy.data.objects.get(_nm)
    if _o: bpy.data.objects.remove(_o, do_unlink=True)

GXX, GYY = -88.0, 7.0
for s, tg in [(1, "N"), (-1, "S")]:
    y = s * GYY
    add_box_comp(f"Gate_PierBase_{tg}_1", 3.2, 3.2, 0.7, (GXX, y, 0.35))
    add_box_comp(f"Gate_PierBase_{tg}_2", 2.7, 2.7, 0.6, (GXX, y, 1.0))
    add_box_comp(f"Gate_Pier_{tg}", 2.1, 2.1, 5.4, (GXX, y, 4.0))
    for bi, bz in enumerate([2.6, 4.2, 5.8]):
        add_box_comp(f"Gate_PierBand_{tg}_{bi+1}", 2.45, 2.45, 0.3, (GXX, y, bz))
    add_box_comp(f"Gate_PierCapital_{tg}", 2.9, 2.9, 0.5, (GXX, y, 6.95))
add_box_comp("Gate_Lintel_1", 2.5, 2*GYY + 3.0, 0.65, (GXX, 0, 7.275))
add_box_comp("Gate_Lintel_2", 2.9, 2*GYY + 4.4, 0.6,  (GXX, 0, 7.9))
add_box_comp("Gate_Lintel_3", 3.3, 2*GYY + 5.8, 0.6,  (GXX, 0, 8.5))
gz = 8.8
for i, w in enumerate([4.2, 3.3, 2.4, 1.5]):
    add_box_comp(f"Gate_Crown_Pidha_{i+1}", w, w, 0.5, (GXX, 0, gz + 0.25)); gz += 0.5
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.6, radius2=0.0, depth=1.0,
                                location=(GXX, 0, gz + 0.5))
o = bpy.context.active_object; o.name = "Gate_Crown_Kalasha"
o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)

# P2. gajasimha guardians flanking the approach
for s, tg in [(1, "N"), (-1, "S")]:
    y, bx = s * 5.5, -80.0
    add_box_comp(f"Gajasimha_{tg}_Pedestal", 2.6, 1.8, 0.9, (bx, y, 0.45))
    add_box_comp(f"Gajasimha_{tg}_Eleph_Body", 1.7, 1.3, 0.9, (bx + 0.15, y, 1.35))
    add_box_comp(f"Gajasimha_{tg}_Eleph_Head", 0.8, 0.9, 0.7, (bx - 0.85, y, 1.25))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx - 1.3, y, 0.85),
                                    rotation=(0, math.radians(18), 0))
    o = bpy.context.active_object; o.name = f"Gajasimha_{tg}_Eleph_Trunk"
    o.scale = (0.25, 0.28, 0.9)
    o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for nm2, dims, loc2, rot2 in [
            ("Lion_Body",  (2.0, 0.9, 0.8),  (bx + 0.1, y, 2.35),  (0, math.radians(-32), 0)),
            ("Lion_Chest", (0.8, 1.0, 1.0),  (bx - 0.65, y, 2.85), (0, math.radians(-15), 0)),
            ("Lion_Leg1",  (0.22, 0.22, 1.1), (bx - 1.05, y + 0.3, 2.35), (0, math.radians(-20), 0)),
            ("Lion_Leg2",  (0.22, 0.22, 1.1), (bx - 1.05, y - 0.3, 2.35), (0, math.radians(-20), 0)),
            ("Lion_Haunch", (0.9, 1.0, 0.75), (bx + 0.85, y, 1.85), (0, 0, 0))]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc2, rotation=rot2)
        o = bpy.context.active_object; o.name = f"Gajasimha_{tg}_{nm2}"
        o.scale = dims
        o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.42,
                                         location=(bx - 0.8, y, 3.55))
    o = bpy.context.active_object; o.name = f"Gajasimha_{tg}_Lion_Head"
    o.data.materials.clear(); o.data.materials.append(mat); move_to(o, coll_comp)

# P3. jagamohana: nested door jambs + navagraha lintels, pilasters, niches
doors = [("E", -1, 0), ("W", 1, 0), ("N", 0, 1), ("S", 0, -1)]
for tg, px, py in doors:
    base_off = BW/2 + 0.9
    for j, (w, h, proud) in enumerate([(6.8, 9.9, 0.38), (8.0, 10.7, 0.18)]):
        off = base_off + proud/2
        add_box_at(f"JM_DoorJamb_{tg}_{j+1}", proud if px else w, proud if py else w, h,
                   (px * off, py * off, PITHA_TOP + h/2))
    off = base_off + 0.275
    add_box_at(f"JM_Navagraha_{tg}", 0.55 if px else 7.4, 0.55 if py else 7.4, 1.0,
               (px * off, py * off, PITHA_TOP + 10.4))
    for pi, d in enumerate([-13.6, -8.7, 8.7, 13.6]):
        off = BW/2 + 0.15
        if px:
            add_box_at(f"JM_Pilaster_{tg}_{pi+1}", 0.3, 0.9, 11.0, (px * off, d, PITHA_TOP + 10.0))
        else:
            add_box_at(f"JM_Pilaster_{tg}_{pi+1}", 0.9, 0.3, 11.0, (d, py * off, PITHA_TOP + 10.0))
    for ni, d in enumerate([-13.2, -10.2, -7.4, 7.4, 10.2, 13.2]):
        off = BW/2 + 0.2
        zn = PITHA_TOP + 3.2
        if px:
            add_box_at(f"JM_Niche_{tg}_{ni+1}", 0.4, 0.95, 1.5, (px * off, d, zn))
            add_box_at(f"JM_NicheCap_{tg}_{ni+1}", 0.45, 1.2, 0.3, (px * off, d, zn + 0.95))
        else:
            add_box_at(f"JM_Niche_{tg}_{ni+1}", 0.95, 0.4, 1.5, (d, py * off, zn))
            add_box_at(f"JM_NicheCap_{tg}_{ni+1}", 1.2, 0.45, 0.3, (d, py * off, zn + 0.95))

# P4. carved-lite micro-displacement on structural elements
lite = bpy.data.materials.get("Konark_Sandstone_CarvedLite")
if lite is None:
    lite = carved.copy()
    lite.name = "Konark_Sandstone_CarvedLite"
    lite.node_tree.nodes["CV_Disp"].inputs["Scale"].default_value = 0.09
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith((
            "NataMandir_Pier_", "Gate_Pier", "Gate_Lintel", "Gate_Crown",
            "Mayadevi_Hall_Wall", "Mayadevi_Sanc_Wall", "Mayadevi_Hall_Paga",
            "Mayadevi_Sanc_Paga", "Shrine_North_Body", "Shrine_South_Body",
            "Gajasimha_", "ArunaStambha_Pedestal", "JM_Door", "JM_Navagraha")):
        o.data.materials.clear()
        o.data.materials.append(lite)
        if not any(md.type == 'SUBSURF' for md in o.modifiers):
            sub = o.modifiers.new("AdaptiveSub", 'SUBSURF')
            sub.subdivision_type = 'SIMPLE'
            sub.levels = 0
            sub.use_adaptive_subdivision = True

# =============================================================================
#  Q. REALISTIC COLOR PASS - weathered khondalite, lawns, Nishita dawn sky
#     NOTE: the AI-generated statue meshes (Gajasimha_*_Sculpt, Deul_Surya_*_
#     Sculpt, Horse_Sculpt_*) were created via Hyper3D Rodin and live in the
#     saved konark.blend - they are not reproducible from this script.
# =============================================================================
def upgrade_stone(matname, dark_c, warm_c, patch_c):
    m = bpy.data.materials.get(matname)
    if m is None: return
    nt2 = m.node_tree
    nds, lks = nt2.nodes, nt2.links
    b = nds.get("Principled BSDF")
    rmp = nds.get("KN_Ramp")
    if rmp:
        rmp.color_ramp.elements[0].color = dark_c
        rmp.color_ramp.elements[0].position = 0.18
        rmp.color_ramp.elements[1].color = warm_c
        rmp.color_ramp.elements[1].position = 0.72
    for n in [n for n in nds if n.name.startswith("KL_")]:
        nds.remove(n)
    def q(kind, name, loc):
        n = nds.new(kind); n.name = name; n.location = loc; return n
    big = q("ShaderNodeTexNoise", "KL_Big", (-620, 560))
    big.inputs["Scale"].default_value = 0.55
    big.inputs["Detail"].default_value = 4.0
    mixp = q("ShaderNodeMix", "KL_MixPatch", (-300, 480))
    mixp.data_type = 'RGBA'
    mixp.inputs["B"].default_value = patch_c
    fac = q("ShaderNodeMapRange", "KL_PatchFac", (-460, 560))
    fac.inputs["From Min"].default_value = 0.55
    fac.inputs["From Max"].default_value = 0.75
    fac.inputs["To Max"].default_value = 0.55
    lks.new(big.outputs["Fac"], fac.inputs["Value"])
    lks.new(fac.outputs["Result"], mixp.inputs["Factor"])
    if rmp: lks.new(rmp.outputs["Color"], mixp.inputs["A"])
    g = q("ShaderNodeNewGeometry", "KL_Geo", (-620, 260))
    pr = q("ShaderNodeMapRange", "KL_PointRange", (-460, 260))
    pr.inputs["From Min"].default_value = 0.35
    pr.inputs["From Max"].default_value = 0.65
    pr.inputs["To Min"].default_value = 0.45
    pr.inputs["To Max"].default_value = 1.15
    lks.new(g.outputs["Pointiness"], pr.inputs["Value"])
    oi = q("ShaderNodeObjectInfo", "KL_ObjInfo", (-620, 100))
    orr = q("ShaderNodeMapRange", "KL_ObjRange", (-460, 100))
    orr.inputs["To Min"].default_value = 0.88
    orr.inputs["To Max"].default_value = 1.10
    lks.new(oi.outputs["Random"], orr.inputs["Value"])
    both = q("ShaderNodeMath", "KL_MulBoth", (-300, 180)); both.operation = 'MULTIPLY'
    lks.new(pr.outputs["Result"], both.inputs[0])
    lks.new(orr.outputs["Result"], both.inputs[1])
    comb = q("ShaderNodeCombineColor", "KL_Comb", (-300, 60))
    for ch in ("Red", "Green", "Blue"):
        lks.new(both.outputs[0], comb.inputs[ch])
    fin = q("ShaderNodeMix", "KL_Final", (-120, 380))
    fin.data_type = 'RGBA'; fin.blend_type = 'MULTIPLY'
    fin.inputs["Factor"].default_value = 1.0
    lks.new(mixp.outputs["Result"], fin.inputs["A"])
    lks.new(comb.outputs["Color"], fin.inputs["B"])
    lks.new(fin.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.92

DARK_C  = (0.045, 0.036, 0.032, 1)
WARM_C  = (0.40, 0.245, 0.145, 1)
PATCH_C = (0.55, 0.33, 0.21, 1)
for mn in ("Konark_Sandstone", "Konark_Sandstone_Carved", "Konark_Sandstone_CarvedLite"):
    upgrade_stone(mn, DARK_C, WARM_C, PATCH_C)

cb = chl.node_tree.nodes.get("Principled BSDF")
cb.inputs["Base Color"].default_value = (0.030, 0.048, 0.038, 1)
cb.inputs["Roughness"].default_value = 0.38
gmm = bpy.data.materials.get("Konark_GroundSand")
if gmm:
    gmm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.38, 0.26, 0.16, 1)

# lawns (modern site gardens)
lawn = bpy.data.materials.get("Konark_Lawn")
if lawn is None:
    lawn = bpy.data.materials.new("Konark_Lawn")
    lawn.use_nodes = True
    lb = lawn.node_tree.nodes.get("Principled BSDF")
    lb.inputs["Roughness"].default_value = 1.0
    lnz = lawn.node_tree.nodes.new("ShaderNodeTexNoise"); lnz.location = (-500, 300)
    lnz.inputs["Scale"].default_value = 18.0
    lrp = lawn.node_tree.nodes.new("ShaderNodeValToRGB"); lrp.location = (-300, 300)
    lrp.color_ramp.elements[0].color = (0.055, 0.12, 0.03, 1)
    lrp.color_ramp.elements[1].color = (0.13, 0.24, 0.06, 1)
    lawn.node_tree.links.new(lnz.outputs["Fac"], lrp.inputs["Fac"])
    lawn.node_tree.links.new(lrp.outputs["Color"], lb.inputs["Base Color"])
for tag3, cx, cy, lx, ly in [("NE", -50, 33, 68, 42), ("SE", -50, -33, 68, 42),
                             ("NW", 46, 33, 78, 42), ("SW", 46, -33, 78, 42)]:
    if bpy.data.objects.get(f"Lawn_{tag3}"): continue
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, -0.02))
    o = bpy.context.active_object; o.name = f"Lawn_{tag3}"
    o.scale = (lx, ly, 1)
    o.data.materials.append(lawn)
    move_to(o, coll_refs)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Nishita dawn sky (sun disc off - the keyed Sun lamp is the light source)
wnt = world.node_tree
skyn = wnt.nodes.get("Konark_Sky")
if skyn is None:
    skyn = wnt.nodes.new("ShaderNodeTexSky"); skyn.name = "Konark_Sky"
    skyn.location = (-300, 300)
try:
    skyn.sky_type = 'NISHITA'
except Exception:
    pass
skyn.sun_elevation = math.radians(9.0)
skyn.sun_rotation = math.radians(90.0)
if hasattr(skyn, "sun_intensity"): skyn.sun_intensity = 0.0
if hasattr(skyn, "sun_disc"): skyn.sun_disc = False
wnt.links.new(skyn.outputs["Color"], wnt.nodes["Background"].inputs["Color"])
wnt.nodes["Background"].inputs["Strength"].default_value = 0.12

print("Konark Sun Temple COMPLETE: full complex, carved detail, khondalite "
      "colors, lawns, dawn sky. Statue sculpts live in konark.blend.")
