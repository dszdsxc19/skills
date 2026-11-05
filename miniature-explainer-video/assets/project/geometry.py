"""Original reusable primitives for miniature explanatory scenes."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
ACTIVE = None
MESHES = {}
MATERIALS = {}
FONT = None
COLORS = {
    "paper":"#eee8dc", "wall":"#ece6d8", "white":"#faf7ef",
    "navy":"#243d49", "teal":"#397e80", "blue":"#527f9c",
    "pink":"#cc7894", "orange":"#bf7252", "yellow":"#d8b469",
    "green":"#8ca477", "grass":"#b0bd94", "wood":"#93663f",
    "woodlight":"#c29c74", "red":"#aa594c", "road":"#697778",
    "metal":"#8d9b9d", "skin":"#d0ad8b", "hair":"#3b3b36",
    "gray":"#bbbdb6", "rubber":"#354348", "glass":"#9fbcc6",
    "darkgreen":"#456554", "tile":"#dcded2"
}


def rgba(key):
    value = COLORS.get(key, key).lstrip("#")
    rgb = [int(value[i:i+2], 16)/255 for i in (0,2,4)]
    return tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb)+(1,)


def material(key):
    if key in MATERIALS:
        return MATERIALS[key]
    m = bpy.data.materials.new(key)
    m.diffuse_color = rgba(key)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    links = m.node_tree.links
    p = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = rgba(key)
    p.inputs["Roughness"].default_value = .53
    if key in ["metal", "rubber"]:
        p.inputs["Metallic"].default_value = .55 if key == "metal" else .05
        p.inputs["Roughness"].default_value = .30 if key == "metal" else .75
    if key in ["blue", "pink", "glass"]:
        p.inputs["Roughness"].default_value = .28
        if "Coat Weight" in p.inputs:
            p.inputs["Coat Weight"].default_value = .30
    if key in ["wood", "woodlight", "paper", "wall", "tile"]:
        coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (2, 65, 7) if "wood" in key else (1,1,1)
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 2.7 if "wood" in key else 95
        noise.inputs["Detail"].default_value = 3
        links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        ramp = nodes.new("ShaderNodeValToRGB")
        base = rgba(key)
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[0].color = tuple(v*.70 for v in base[:3])+(1,)
        ramp.color_ramp.elements[1].color = tuple(min(1,v*1.15) for v in base[:3])+(1,)
        links.new(noise.outputs["Fac"], ramp.inputs[0])
        links.new(ramp.outputs["Color"], p.inputs["Base Color"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = .12 if "wood" in key else .045
        bump.inputs["Distance"].default_value = .025 if "wood" in key else .009
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], p.inputs["Normal"])
    MATERIALS[key] = m
    return m


def empty(name, loc=(0,0,0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.parent = parent
    return o


def use_set(name, x):
    global ACTIVE
    ACTIVE = empty(name, (x,0,0))
    return ACTIVE


def finish(o, name, loc, mat, parent):
    o.name = name
    o.location = loc
    o.parent = ACTIVE if parent is None else parent
    o.data.materials.append(material(mat))
    return o


def box(name, loc, size, mat="white", bevel=.035, parent=None):
    key = ("box", tuple(size), mat, bevel)
    if key in MESHES:
        o = bpy.data.objects.new(name, MESHES[key])
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        o.parent = ACTIVE if parent is None else parent
        return o
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Crafted soft edge", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    finish(o, name, loc, mat, parent)
    MESHES[key] = o.data
    return o


def ball(name, loc, radius, mat="skin", scale=(1,1,1), parent=None):
    key = ("ball", radius, mat)
    if key in MESHES:
        o = bpy.data.objects.new(name, MESHES[key])
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        o.parent = ACTIVE if parent is None else parent
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius)
        o = bpy.context.object
        finish(o, name, loc, mat, parent)
        for p in o.data.polygons:
            p.use_smooth = True
        MESHES[key] = o.data
    o.scale = scale
    return o


def cyl(name, loc, radius, depth, mat="metal", parent=None, rot=(0,0,0)):
    key = ("cyl", radius, depth, mat)
    if key in MESHES:
        o = bpy.data.objects.new(name, MESHES[key])
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        o.parent = ACTIVE if parent is None else parent
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth)
        o = bpy.context.object
        finish(o, name, loc, mat, parent)
        mod = o.modifiers.new("Rim bevel", "BEVEL")
        mod.width = .012
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        MESHES[key] = o.data
    o.rotation_euler = rot
    return o


def ring(name, loc, mat="blue", parent=None):
    key = ("ring", mat)
    if key in MESHES:
        o = bpy.data.objects.new(name, MESHES[key])
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        o.parent = ACTIVE if parent is None else parent
    else:
        bpy.ops.mesh.primitive_torus_add(major_radius=.115, minor_radius=.024, major_segments=24, minor_segments=8)
        o = bpy.context.object
        finish(o, name, loc, mat, parent)
        for p in o.data.polygons:
            p.use_smooth = True
        MESHES[key] = o.data
    return o


def text(body, loc, size=.25, mat="navy", parent=None, align="CENTER"):
    global FONT
    if FONT is None:
        FONT = bpy.data.fonts.load(str(ROOT/"assets/fonts/NotoSansSC-Medium.ttf"))
    c = bpy.data.curves.new(body, "FONT")
    c.body = body
    c.font = FONT
    c.align_x = align
    c.align_y = "CENTER"
    c.size = size
    c.extrude = .001
    o = bpy.data.objects.new(body, c)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.pi/2,0,0)
    o.parent = ACTIVE if parent is None else parent
    c.materials.append(material(mat))
    return o


def floor(name, size=(7,5), mat="tile"):
    box(name+" wood edge", (0,0,.10), (*size,.28), "woodlight", .10)
    box(name+" floor", (0,0,.29), (size[0]-.08,size[1]-.08,.12), mat, .06)
    if mat == "tile":
        for x in range(-int(size[0]), int(size[0])+1):
            box("Grout line", (x*.5,0,.354), (.009,size[1]-.12,.003), "gray", .0)
        for y in range(-int(size[1]), int(size[1])+1):
            box("Grout line", (0,y*.5,.354), (size[0]-.12,.009,.003), "gray", .0)


def person(name, loc, clothing="blue", scale=.65, elder=False):
    p = empty(name, loc, ACTIVE)
    box(name+" coat", (0,0,.48), (.30,.23,.43), clothing, .07, p)
    box(name+" collar", (0,-.125,.64), (.13,.018,.10), "white", .01, p)
    box(name+" badge", (.075,-.13,.52), (.065,.02,.085), "white", .008, p)
    ball(name+" head", (0,-.015,.84), .147, "skin", (.95,.93,1.08), p)
    ball(name+" hair", (0,.005,.91), .151, "gray" if elder else "hair", (1,.95,.63), p)
    legs, arms = [], []
    for side in [-1,1]:
        hip = empty(name+" hip", (side*.078,0,.29), p)
        box(name+" trouser", (0,0,-.115), (.11,.14,.25), "navy", .025, hip)
        box(name+" shoe", (0,-.045,-.255), (.14,.23,.075), "rubber", .025, hip)
        shoulder = empty(name+" shoulder", (side*.19,0,.61), p)
        box(name+" sleeve", (0,0,-.115), (.09,.14,.29), clothing, .035, shoulder)
        ball(name+" hand", (0,-.015,-.29), .058, "skin", parent=shoulder)
        legs.append(hip)
        arms.append(shoulder)
    if elder:
        cyl(name+" cane", (.26,-.06,.28), .018,.53,"wood",p)
    p.scale = (scale,)*3
    return {"root":p, "legs":legs, "arms":arms, "base":Vector(loc), "scale":scale}


def vehicle(name, mat="yellow", bus=True):
    p = empty(name, parent=ACTIVE)
    length = 1.7 if bus else .95
    box(name+" body", (0,0,.35), (length,.55,.42), mat,.085,p)
    box(name+" cabin", (-.05,0,.65), (length*.88,.52,.35),mat,.065,p)
    for y in [-.268,.268]:
        for x in ([-.57,-.23,.11,.45] if bus else [-.22,.12]):
            box("Bus window", (x,y,.68), (.25,.016,.22),"glass",.017,p)
        for x in [-length*.34,length*.34]:
            cyl("Tyre", (x,y*1.07,.19), .14,.085,"rubber",p,(math.pi/2,0,0))
            cyl("Wheel hub", (x,y*1.23,.19), .065,.01,"metal",p,(math.pi/2,0,0))
    for y in [-.16,.16]:
        box("Headlamp", (length/2+.01,y,.38), (.025,.10,.09),"white",.015,p)
    door = empty(name+" hinged door", (.42,-.28,.44), p)
    box("Door glass", (0,0,.08), (.25,.024,.52),"glass",.015,door)
    return p,door


def path(name, points, mat="orange", radius=.035):
    c = bpy.data.curves.new(name,"CURVE")
    c.dimensions = "3D"
    c.bevel_depth = radius
    c.bevel_resolution = 3
    spline = c.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):
        p.co = (*co,1)
    o = bpy.data.objects.new(name,c)
    bpy.context.scene.collection.objects.link(o)
    o.parent = ACTIVE
    c.materials.append(material(mat))
    return o


def tree(x,y,s=.7):
    cyl("Tree trunk",(x,y,.8*s),.08*s,1.2*s,"wood")
    ball("Leaves",(x,y,1.5*s),.55*s,"green",(.85,.85,1.2))
    ball("Leaves crown",(x+.13*s,y,1.8*s),.34*s,"grass")
