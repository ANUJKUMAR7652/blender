import bpy
import math


def create_toon_material(name, base_color, shadow_color, ink_edge=True, cast_shadow=True, glossy_shine=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.shadow_method = 'OPAQUE' if cast_shadow else 'NONE'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    s2rgb = nodes.new('ShaderNodeShaderToRGB')

    toon_ramp = nodes.new('ShaderNodeValToRGB')
    toon_ramp.color_ramp.interpolation = 'CONSTANT'
    toon_ramp.color_ramp.elements[0].position = 0.0
    toon_ramp.color_ramp.elements[0].color = shadow_color
    toon_ramp.color_ramp.elements[1].position = 0.34
    toon_ramp.color_ramp.elements[1].color = base_color

    if glossy_shine:
        hi = toon_ramp.color_ramp.elements.new(0.82)
        hi.color = (
            min(1.0, base_color[0] * 1.6 + 0.16),
            min(1.0, base_color[1] * 1.6 + 0.14),
            min(1.0, base_color[2] * 1.6 + 0.12),
            1.0
        )

    links.new(diffuse.outputs['BSDF'], s2rgb.inputs['Shader'])
    links.new(s2rgb.outputs['Color'], toon_ramp.inputs['Fac'])

    if ink_edge:
        lw = nodes.new('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.28
        edge_ramp = nodes.new('ShaderNodeValToRGB')
        edge_ramp.color_ramp.interpolation = 'CONSTANT'
        edge_ramp.color_ramp.elements[0].position = 0.0
        edge_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
        edge_ramp.color_ramp.elements[1].position = 0.82
        edge_ramp.color_ramp.elements[1].color = (0.03, 0.03, 0.04, 1)

        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Fac'].default_value = 1.0
        links.new(lw.outputs['Facing'], edge_ramp.inputs['Fac'])
        links.new(toon_ramp.outputs['Color'], mix.inputs['Color1'])
        links.new(edge_ramp.outputs['Color'], mix.inputs['Color2'])
        links.new(mix.outputs['Color'], out.inputs['Surface'])
    else:
        links.new(toon_ramp.outputs['Color'], out.inputs['Surface'])
    return mat


def create_vfx_emission_material(name, color, strength=6.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.shadow_method = 'NONE'
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emis = nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = color
    emis.inputs['Strength'].default_value = strength
    mat.node_tree.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    return mat


def create_striped_sock_material():
    return create_toon_material("FB_Striped_Sock_Mat", (0.95, 0.95, 0.95, 1), (0.78, 0.78, 0.82, 1))


def create_black_nylon_cage_material():
    """Creates the Diamond Black Nylon / Chain-Link Mesh Material (Like Image 2!)."""
    name = "Octagon_Black_Nylon_Net_Mat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.blend_method = 'HASHED'
    mat.shadow_method = 'NONE'
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    tex = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Rotation'].default_value = (0, 0, math.radians(45))  # 45-deg Diamond Mesh!

    brick = nodes.new('ShaderNodeTexBrick')
    brick.offset = 0.0
    brick.inputs['Color1'].default_value = (0.0, 0.0, 0.0, 1.0)      # Hole
    brick.inputs['Color2'].default_value = (0.0, 0.0, 0.0, 1.0)      # Hole
    brick.inputs['Mortar'].default_value = (1.0, 1.0, 1.0, 1.0)      # Black Nylon Wire
    brick.inputs['Scale'].default_value = 34.0
    brick.inputs['Mortar Size'].default_value = 0.16
    brick.inputs['Brick Width'].default_value = 1.0
    brick.inputs['Row Height'].default_value = 1.0

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.08, 0.09, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45

    # Semi-transparent dark backing + solid black nylon diamond wires
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.32, 0.32, 0.32, 1.0)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

    links.new(tex.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    links.new(brick.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Alpha'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def create_octagon_mat_material():
    """Warm White MMA Octagon Canvas Floor Mat (Receives Soft Shadows!)."""
    name = "Anime_Octagon_Floor_Mat"
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.94, 0.92, 0.90, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.90
    bsdf.inputs['Specular'].default_value = 0.05
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def setup_studio_environment():
    for obj in list(bpy.data.objects):
        if obj.name in ("Cube", "Light", "Camera") or obj.name.startswith(
            ("FA_", "FB_", "REF_", "Arena_", "FightCam", "CamTarget", "KeyLight", "RimLight", "VFX_")
        ):
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.use_soft_shadows = True
    scene.eevee.shadow_cube_size = '1024'
    scene.eevee.shadow_cascade_size = '2048'
    # Crisp Standard Color Management so Whites & Blacks look 100% like Video Image 2!
    try:
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass

    # Dark Charcoal/Black Studio World Background
    if not scene.world:
        scene.world = bpy.data.worlds.new("FightWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.09, 0.10, 0.12, 1.0)
        bg.inputs[1].default_value = 1.0

    # 1. White MMA Octagon Floor Mat + Black Octagon Boundary Line
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=3.8, depth=0.04, location=(0, 0, -0.02))
    floor = bpy.context.active_object
    floor.name = "Arena_Grid_Floor"
    floor.rotation_euler = (0, 0, math.radians(22.5))
    floor.data.materials.append(create_octagon_mat_material())

    black_pad_mat = bpy.data.materials.new("Arena_Black_Pad")
    black_pad_mat.use_nodes = True
    bsdf_p = black_pad_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_p:
        bsdf_p.inputs['Base Color'].default_value = (0.06, 0.06, 0.07, 1.0)
        bsdf_p.inputs['Roughness'].default_value = 0.38
    black_pad_mat.shadow_method = 'NONE'

    net_mat = create_black_nylon_cage_material()

    # 2. Build 8-Sided Octagon MMA Cage (Posts + Top/Bottom Padded Rails + Black Nylon Mesh Panels!)
    oct_r = 3.25
    cage_h = 1.85
    for i in range(8):
        a1 = math.radians(i * 45.0 + 22.5)
        a2 = math.radians((i + 1) * 45.0 + 22.5)
        x1, y1 = oct_r * math.cos(a1), oct_r * math.sin(a1)
        x2, y2 = oct_r * math.cos(a2), oct_r * math.sin(a2)

        # Corner Padded Pillar
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.11, depth=cage_h, location=(x1, y1, cage_h * 0.5))
        post = bpy.context.active_object
        post.name = f"Arena_Post_{i}"
        bpy.ops.object.shade_smooth()
        post.data.materials.append(black_pad_mat)

        # Inner Black Boundary Line on Mat
        mx, my = (x1 + x2) * 0.5, (y1 + y2) * 0.5
        wall_len = math.hypot(x2 - x1, y2 - y1)
        wall_ang = math.atan2(y2 - y1, x2 - x1)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mx * 0.78, my * 0.78, 0.002))
        line = bpy.context.active_object
        line.name = f"Arena_MatLine_{i}"
        line.scale = (wall_len * 0.78, 0.03, 0.002)
        line.rotation_euler = (0, 0, wall_ang)
        line.data.materials.append(black_pad_mat)

        # Top & Bottom Horizontal Padded Cage Rails
        for rz, r_rad in [(cage_h, 0.095), (0.06, 0.075)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r_rad, depth=wall_len, location=(mx, my, rz))
            rail = bpy.context.active_object
            rail.name = f"Arena_Rail_{i}_{rz}"
            bpy.ops.object.shade_smooth()
            rail.rotation_euler = (0, math.radians(90), wall_ang)
            rail.data.materials.append(black_pad_mat)

        # Black Nylon Mesh Fence Panel (Skip front-camera panel i=5,6 so camera view is unobstructed!)
        if i not in (5, 6):
            bpy.ops.mesh.primitive_plane_add(size=1.0, location=(mx, my, cage_h * 0.5))
            panel = bpy.context.active_object
            panel.name = f"Arena_NylonNet_{i}"
            panel.scale = (wall_len, cage_h, 1.0)
            panel.rotation_euler = (math.radians(90), 0, wall_ang)
            panel.data.materials.append(net_mat)

    # Dark Studio Outer Backdrop & Ceiling (So Black Nylon Cage stands out clearly!)
    dark_wall_mat = create_toon_material("Arena_Dark_Backdrop", (0.14, 0.15, 0.17, 1), (0.08, 0.09, 0.10, 1), ink_edge=False, cast_shadow=False)
    for w_name, w_loc, w_rot in [
        ("Arena_BackWall", (0, 7.5, 4), (90, 0, 0)),
        ("Arena_LeftWall", (-7.5, 0, 4), (0, 90, 0)),
        ("Arena_RightWall", (7.5, 0, 4), (0, -90, 0)),
        ("Arena_Ceiling", (0, 0, 5.5), (180, 0, 0)),
    ]:
        bpy.ops.mesh.primitive_plane_add(size=24, location=w_loc, rotation=[math.radians(a) for a in w_rot])
        w = bpy.context.active_object
        w.name = w_name
        w.data.materials.append(dark_wall_mat)

    # Balanced Studio Lighting (No Overexposure!)
    bpy.ops.object.light_add(type='SUN', location=(2.2, -3.2, 6.0))
    sun = bpy.context.active_object
    sun.name = "KeyLight"
    sun.data.energy = 2.15
    sun.data.angle = math.radians(8.0)
    sun.data.use_shadow = True
    sun.data.use_contact_shadow = True
    sun.rotation_euler = (math.radians(35), math.radians(-22), math.radians(18))

    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.05, location=(0, 0, 1.15))
    cam_target = bpy.context.active_object
    cam_target.name = "CamTarget"

    bpy.ops.object.camera_add(location=(0, -2.85, 1.18))
    cam = bpy.context.active_object
    cam.name = "FightCam"
    cam.data.lens = 38
    track = cam.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    scene.camera = cam
