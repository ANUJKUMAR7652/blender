import bpy
import bmesh
import math
from mathutils import Vector

try:
    from .materials_arena import create_toon_material, create_striped_sock_material
except ImportError:
    from materials_arena import create_toon_material, create_striped_sock_material


def create_joint(name, parent, local_loc=(0, 0, 0)):
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.01)
    j = bpy.context.active_object
    j.name = name
    if parent:
        j.parent = parent
    j.location = local_loc
    return j


def create_anatomical_torso_mesh(name, parent, skin_mat, top_mat, accent_mat, is_claudia=True):
    """
    Seamless Female Torso with Full Rounded Bust Profile (`bust_size = 0.074` for Claudia),
    Scoop-Neck Shoulder Straps, Racerback Cut, White Side Trim on Black Top, Abs, Navel & Spine!
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(skin_mat)    # 0: Skin
    obj.data.materials.append(top_mat)     # 1: Main Crop Top
    obj.data.materials.append(accent_mat)  # 2: White Side/Back Stripe on Fighter B's Black Top!

    segs = 36
    rings = [
        (-0.03, 0.078, 0.106, 0.002),
        (0.00, 0.084, 0.112, 0.004),
        (0.03, 0.076, 0.100, 0.006),
        (0.055, 0.072, 0.092, 0.008),
        (0.085, 0.070, 0.089, 0.009),
        (0.125, 0.077, 0.098, 0.010),
        (0.165, 0.084, 0.108, 0.011),
        (0.190, 0.088, 0.114, 0.013),
        (0.220, 0.096, 0.122, 0.018),
        (0.250, 0.102, 0.126, 0.022), # Full Bust Peak (Matches Image 2!)
        (0.280, 0.095, 0.122, 0.015),
        (0.315, 0.086, 0.120, 0.008),
        (0.350, 0.080, 0.126, 0.004),
        (0.385, 0.068, 0.142, 0.000),
        (0.415, 0.046, 0.062, 0.000),
        (0.440, 0.038, 0.038, 0.000),
    ]

    bust_size = 0.074 if is_claudia else 0.048
    bm = bmesh.new()
    ring_verts = []

    for (z, rx, ry, ox) in rings:
        v_loop = []
        for s in range(segs):
            ang = (2.0 * math.pi * s) / segs
            ca, sa = math.cos(ang), math.sin(ang)
            x, y = ox + rx * ca, ry * sa

            if 0.18 <= z <= 0.315 and ca > 0.05:
                z_norm = (z - 0.18) / 0.135
                z_curve = math.sin(math.pi * z_norm) ** 0.80
                lobe = (abs(sa) ** 1.25) * ((1.0 - abs(sa)) ** 0.50) * 2.95 * (ca ** 0.55)
                x += bust_size * z_curve * lobe
                y *= (1.0 + 0.12 * z_curve * abs(sa))

                ang_deg = abs(math.degrees(ang))
                if 0.235 <= z <= 0.268 and 26.0 <= ang_deg <= 42.0:
                    apex_fac = math.cos(math.pi * (ang_deg - 34.0) / 16.0) * math.sin(math.pi * (z - 0.235) / 0.033)
                    x += 0.0075 * max(0.0, apex_fac)

            if 0.02 <= z <= 0.16 and ca > 0.75:
                ab_groove = math.exp(-((sa * 12.0) ** 2)) * 0.0035
                x -= ab_groove
                if 0.045 <= z <= 0.065 and abs(sa) < 0.12:
                    x -= 0.0055

            if 0.02 <= z <= 0.36 and ca < -0.75:
                spine_groove = math.exp(-((sa * 10.0) ** 2)) * 0.005
                x += spine_groove

            v_loop.append(bm.verts.new((x, y, z)))
        ring_verts.append(v_loop)

    for r in range(len(ring_verts) - 1):
        r1, r2 = ring_verts[r], ring_verts[r + 1]
        z_mid = 0.5 * (rings[r][0] + rings[r + 1][0])
        for s in range(segs):
            sn = (s + 1) % segs
            f = bm.faces.new((r1[s], r1[sn], r2[sn], r2[s]))
            f.smooth = True

            ang_mid = (2.0 * math.pi * (s + 0.5)) / segs
            ca_m, sa_m = math.cos(ang_mid), abs(math.sin(ang_mid))

            mat_i = 0
            if 0.165 <= z_mid <= 0.285:
                mat_i = 1
                # White vertical side/back stripe on Fighter B's Black Crop Top (Image 2!)
                if not is_claudia and -0.45 <= ca_m <= -0.15 and sa_m > 0.80:
                    mat_i = 2
            elif 0.285 < z_mid <= 0.388:
                if (ca_m >= 0.0 and 0.36 <= sa_m <= 0.68) or (ca_m < 0.0 and 0.22 <= sa_m <= 0.62):
                    mat_i = 1
            f.material_index = mat_i

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    obj.parent = parent
    return obj


def create_sculpted_anime_head(name, parent, skin_mat):
    """
    True Anime Head Contour WITHOUT pushing forehead backward (so Eyes & Bangs sit 100% FLUSH!).
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(skin_mat)

    segs = 32
    rings = [
        (-0.010, 0.038, 0.038, -0.006),
        (0.058, 0.037, 0.037, -0.002),
        (0.068, 0.054, 0.042, 0.028),
        (0.096, 0.084, 0.072, 0.014),
        (0.128, 0.094, 0.086, 0.010),
        (0.158, 0.094, 0.089, 0.008),  # Eye surface at x = 0.008 + 0.094*ca
        (0.192, 0.094, 0.089, 0.005),
        (0.232, 0.085, 0.081, -0.004),
        (0.258, 0.048, 0.046, -0.010),
        (0.268, 0.003, 0.003, -0.012),
    ]

    bm = bmesh.new()
    ring_verts = []
    for (z, rx, ry, ox) in rings:
        v_loop = []
        for s in range(segs):
            ang = (2.0 * math.pi * s) / segs
            ca, sa = math.cos(ang), math.sin(ang)
            x, y = ox + rx * ca, ry * sa
            if 0.065 <= z <= 0.120 and ca > 0.2:
                cf = max(0.0, 1.0 - (z - 0.065) / 0.055)
                x += 0.014 * cf * (ca ** 2.0)
                y *= (1.0 - 0.22 * cf * (ca ** 1.5))
            v_loop.append(bm.verts.new((x, y, z)))
        ring_verts.append(v_loop)

    for r in range(len(ring_verts) - 1):
        r1, r2 = ring_verts[r], ring_verts[r + 1]
        for s in range(segs):
            sn = (s + 1) % segs
            f = bm.faces.new((r1[s], r1[sn], r2[sn], r2[s]))
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    obj.parent = parent
    return obj


def create_flush_anime_eye(prefix, s_tag, side_y, head, white_mat, iris_mat, black_mat, skin_mat, hair_mat):
    """
    Sits 100% FLUSH on the head surface (`x = 0.0935, y = +-0.036`) — ZERO floating gap from side view!
    """
    y_sign = 1.0 if side_y > 0 else -1.0
    face_rot = (0, 0, -20 * y_sign)
    eye_j = create_joint(f"{prefix}_Eye_{s_tag}", head, (0.093, side_y, 0.156))

    def make_flat_disc(name, par, mat, rx_thick, ry_w, rz_h, loc=(0, 0, 0), rot=(0, 0, 0)):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0)
        o = bpy.context.active_object
        o.name = name
        bpy.ops.object.shade_smooth()
        o.data.materials.append(mat)
        o.parent = par
        o.location = loc
        o.rotation_euler = [math.radians(a) for a in rot]
        o.scale = (rx_thick, ry_w, rz_h)
        return o

    make_flat_disc(f"{prefix}_Sclera_{s_tag}", eye_j, white_mat, 0.0020, 0.018, 0.0125, rot=face_rot)

    iris_j = create_joint(f"{prefix}_Iris_{s_tag}", eye_j, (0.0016, -0.001 * y_sign, 0.0))
    make_flat_disc(f"{prefix}_IrisDisc_{s_tag}", iris_j, iris_mat, 0.0012, 0.0098, 0.0110, rot=face_rot)
    make_flat_disc(f"{prefix}_PupilDisc_{s_tag}", iris_j, black_mat, 0.0015, 0.0058, 0.0065, loc=(0.0004, 0, 0), rot=face_rot)
    make_flat_disc(f"{prefix}_Hi1_{s_tag}", iris_j, white_mat, 0.0018, 0.0026, 0.0026, loc=(0.0008, 0.003, 0.003), rot=face_rot)

    make_flat_disc(f"{prefix}_UpperLash_{s_tag}", eye_j, black_mat, 0.0022, 0.020, 0.0030,
                   loc=(0.0012, 0.001 * y_sign, 0.0110), rot=(-6 * y_sign, 0, -20 * y_sign))

    lid_j = create_joint(f"{prefix}_Lid_{s_tag}", head, (0.094, side_y, 0.167))
    make_flat_disc(f"{prefix}_LidPlane_{s_tag}", lid_j, skin_mat, 0.0022, 0.020, 0.0032,
                   loc=(0, 0, -0.004), rot=face_rot)

    make_flat_disc(f"{prefix}_Brow_{s_tag}", head, hair_mat, 0.0022, 0.020, 0.0022,
                   loc=(0.095, side_y, 0.179), rot=(12 * y_sign, 0, -20 * y_sign))


def create_detailed_ear(name, head, skin_mat, shadow_mat, side_y):
    y_sign = 1.0 if side_y > 0 else -1.0
    ear_j = create_joint(name, head, (-0.004, side_y, 0.146))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=1.0)
    outer = bpy.context.active_object
    outer.name = f"{name}_Helix"
    bpy.ops.object.shade_smooth()
    outer.data.materials.append(skin_mat)
    outer.parent = ear_j
    outer.rotation_euler = (math.radians(-10 * y_sign), math.radians(-12), math.radians(-22 * y_sign))
    outer.scale = (0.011, 0.008, 0.022)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1.0)
    inner = bpy.context.active_object
    inner.name = f"{name}_InnerHollow"
    bpy.ops.object.shade_smooth()
    inner.data.materials.append(shadow_mat)
    inner.parent = ear_j
    inner.location = (0.002, 0.002 * y_sign, 0.0)
    inner.rotation_euler = outer.rotation_euler
    inner.scale = (0.007, 0.005, 0.013)


def create_detailed_mouth(prefix, head, mouth_mat, white_mat, tongue_mat):
    mouth_j = create_joint(f"{prefix}_Mouth", head, (0.096, 0, 0.098))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.010)
    cav = bpy.context.active_object
    cav.name = f"{prefix}_MouthCavity"
    bpy.ops.object.shade_smooth()
    cav.data.materials.append(mouth_mat)
    cav.parent = mouth_j
    cav.scale = (0.20, 1.08, 0.22)

    bpy.ops.mesh.primitive_cube_add(size=0.007)
    teeth = bpy.context.active_object
    teeth.name = f"{prefix}_Teeth"
    teeth.data.materials.append(white_mat)
    teeth.parent = mouth_j
    teeth.location = (0.0010, 0, 0.0040)
    teeth.scale = (0.20, 1.80, 0.35)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.006)
    tng = bpy.context.active_object
    tng.name = f"{prefix}_Tongue"
    bpy.ops.object.shade_smooth()
    tng.data.materials.append(tongue_mat)
    tng.parent = mouth_j
    tng.location = (0.0008, 0, -0.0030)
    tng.scale = (0.22, 1.10, 0.42)


def create_bezier_hair_strand(name, parent, hair_mat, p0, p1, p2, p3, width=0.018, thick=0.007, steps=10):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(hair_mat)

    v0, v1, v2, v3 = Vector(p0), Vector(p1), Vector(p2), Vector(p3)
    bm = bmesh.new()
    ring_verts = []

    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        pos = (mt**3)*v0 + 3*(mt**2)*t*v1 + 3*mt*(t**2)*v2 + (t**3)*v3
        tan = (-3*(mt**2)*v0 + 3*(mt**2 - 2*mt*t)*v1 + 3*(2*mt*t - t**2)*v2 + 3*(t**2)*v3).normalized()
        rad_out = (pos - Vector((0, 0, 0.17))).normalized()
        side_vec = tan.cross(rad_out)
        if side_vec.length < 1e-4:
            side_vec = Vector((0, 1, 0))
        else:
            side_vec.normalize()
        out_vec = side_vec.cross(tan).normalized()

        profile = math.sin(math.pi * (t ** 0.72)) if t < 0.98 else 0.02
        w = max(0.0005, width * profile)
        th = max(0.0004, thick * profile)

        pts = [
            pos + side_vec * w,
            pos + side_vec * (w * 0.35) + out_vec * th,
            pos - side_vec * (w * 0.35) + out_vec * th,
            pos - side_vec * w,
            pos - side_vec * (w * 0.35) - out_vec * (th * 0.45),
            pos + side_vec * (w * 0.35) - out_vec * (th * 0.45),
        ]
        ring_verts.append([bm.verts.new((p.x, p.y, p.z)) for p in pts])

    for r in range(len(ring_verts) - 1):
        r1, r2 = ring_verts[r], ring_verts[r + 1]
        for s in range(6):
            sn = (s + 1) % 6
            f = bm.faces.new((r1[s], r1[sn], r2[sn], r2[s]))
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1
    obj.parent = parent
    return obj


def create_quad_limb(name, parent, materials, rings, segs=22, local_loc=(0, 0, 0),
                     local_rot=(0, 0, 0), scale=(1, 1, 1), subsurf=2, glute_lobe=0.0, short_tri=False):
    """
    Overlapping Ball-Socket Ends (`+0.75 * rxn` beyond pivot) -> ZERO Pinched Elbow/Knee Seams!
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for m in materials:
        obj.data.materials.append(m)

    bm = bmesh.new()
    z0, rx0, ry0, ox0, m0 = rings[0]
    zn, rxn, ryn, oxn, mn = rings[-1]
    full_rings = (
        [(z0 - rx0 * 0.75, 0.002, 0.002, ox0, m0), (z0 - rx0 * 0.38, rx0 * 0.78, ry0 * 0.78, ox0, m0)]
        + list(rings)
        + [(zn + rxn * 0.38, rxn * 0.78, ryn * 0.78, oxn, mn), (zn + rxn * 0.75, 0.002, 0.002, oxn, mn)]
    )

    ring_verts, ring_mats = [], []
    for (z, rx, ry, ox, mat_idx) in full_rings:
        v_loop = []
        for s in range(segs):
            ang = (2.0 * math.pi * s) / segs
            ca, sa = math.cos(ang), math.sin(ang)
            x, y = ox + rx * ca, ry * sa
            if glute_lobe > 0.0 and -0.09 <= z <= 0.04 and ca < -0.15:
                z_fac = math.sin(math.pi * (z + 0.09) / 0.13)
                x -= glute_lobe * z_fac * (sa * sa) * (abs(ca) ** 0.7) * 2.2
            v_loop.append(bm.verts.new((x, y, z)))
        ring_verts.append(v_loop)
        ring_mats.append(mat_idx)

    for r in range(len(ring_verts) - 1):
        r1, r2 = ring_verts[r], ring_verts[r + 1]
        m_idx = ring_mats[r + 1]
        for s in range(segs):
            sn = (s + 1) % segs
            f = bm.faces.new((r1[s], r1[sn], r2[sn], r2[s]))
            f.smooth = True
            # Dark-Grey Side Triangle Slit on Fighter B's White Booty Shorts (Image 2!)
            if short_tri and m_idx == 1:
                ang_m = (2.0 * math.pi * (s + 0.5)) / segs
                if abs(math.sin(ang_m)) > 0.88 and len(materials) > 2:
                    f.material_index = 2
                else:
                    f.material_index = m_idx
            else:
                f.material_index = m_idx

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    if subsurf > 0:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = subsurf
        sub.render_levels = subsurf
    obj.parent = parent
    obj.location = local_loc
    obj.rotation_euler = [math.radians(a) for a in local_rot]
    obj.scale = scale
    return obj


# ==============================================================================
# 3. COMPLETE CHARACTER BUILDER (CLAUDIA, SHORT-HAIRED GIRL & REFEREE)
# ==============================================================================

def build_anime_fighter(prefix, base_x, z_rot_deg, is_blue_hoodie=True):
    is_claudia = is_blue_hoodie

    if is_claudia:
        # Rich Bronze-Tan Skin & Deep Espresso Glossy Hair (Exact Match to Image 2!)
        skin_mat = create_toon_material(f"{prefix}_Skin", (0.58, 0.37, 0.24, 1), (0.40, 0.24, 0.15, 1))
        ear_sh_mat = create_toon_material(f"{prefix}_EarSh", (0.36, 0.20, 0.12, 1), (0.26, 0.14, 0.08, 1), ink_edge=False)
        hair_mat = create_toon_material(f"{prefix}_Hair", (0.16, 0.08, 0.05, 1), (0.06, 0.03, 0.02, 1), glossy_shine=True)
        top_mat = create_toon_material(f"{prefix}_TopWhite", (0.98, 0.98, 1.00, 1), (0.80, 0.82, 0.88, 1))
        pant_mat = create_toon_material(f"{prefix}_PantWhite", (0.97, 0.97, 0.99, 1), (0.78, 0.80, 0.86, 1))
    else:
        # Warm Peach Skin & Jet-Black Glossy Pixie Hair (Exact Match to Image 2!)
        skin_mat = create_toon_material(f"{prefix}_Skin", (0.98, 0.84, 0.74, 1), (0.84, 0.66, 0.55, 1))
        ear_sh_mat = create_toon_material(f"{prefix}_EarSh", (0.74, 0.54, 0.44, 1), (0.60, 0.42, 0.32, 1), ink_edge=False)
        hair_mat = create_toon_material(f"{prefix}_Hair", (0.03, 0.03, 0.04, 1), (0.01, 0.01, 0.01, 1), glossy_shine=True)
        top_mat = create_toon_material(f"{prefix}_TopBlack", (0.08, 0.08, 0.10, 1), (0.02, 0.02, 0.03, 1))
        pant_mat = create_toon_material(f"{prefix}_ShortWhite", (0.98, 0.98, 1.00, 1), (0.80, 0.82, 0.88, 1))

    white_mat = create_toon_material(f"{prefix}_White", (0.98, 0.98, 1.0, 1), (0.80, 0.82, 0.88, 1), ink_edge=False)
    black_mat = create_toon_material(f"{prefix}_Black", (0.06, 0.06, 0.08, 1), (0.01, 0.01, 0.02, 1))
    grey_mat = create_toon_material(f"{prefix}_GreyTri", (0.28, 0.29, 0.32, 1), (0.18, 0.19, 0.22, 1))
    red_mat = create_toon_material(f"{prefix}_RedCord", (0.86, 0.10, 0.12, 1), (0.56, 0.04, 0.06, 1))
    iris_mat = create_toon_material(f"{prefix}_Iris", (0.10, 0.07, 0.06, 1), (0.03, 0.02, 0.02, 1), ink_edge=False)
    mouth_mat = create_toon_material(f"{prefix}_MouthIn", (0.42, 0.10, 0.12, 1), (0.25, 0.05, 0.06, 1), ink_edge=False)
    tongue_mat = create_toon_material(f"{prefix}_Tongue", (0.92, 0.44, 0.46, 1), (0.72, 0.28, 0.30, 1), ink_edge=False)

    root = create_joint(f"{prefix}_Root", None, (0, 0, 0))
    pelvis = create_joint(f"{prefix}_Pelvis", root, (0, 0, 0.80))

    create_quad_limb(
        f"{prefix}_PelvisMesh", pelvis, [pant_mat, red_mat],
        rings=[
            (-0.08, 0.096, 0.132, 0.000, 0),
            (-0.03, 0.108, 0.142, -0.005, 0),
            (0.02, 0.098, 0.130, 0.000, 0),
            (0.048, 0.088, 0.116, 0.002, 1 if is_claudia else 0),
            (0.070, 0.083, 0.110, 0.004, 0),
        ],
        glute_lobe=0.035
    )
    if is_claudia:
        # White Belt Loops over Claudia's Red Belt + Red Hanging Tassel (Image 2!)
        for lp_ang in (-50, 0, 50, 130, 180, -130):
            r_a = math.radians(lp_ang)
            bpy.ops.mesh.primitive_cube_add(size=0.014)
            lp = bpy.context.active_object
            lp.name = f"{prefix}_BeltLoop_{lp_ang}"
            lp.data.materials.append(pant_mat)
            lp.parent = pelvis
            lp.location = (0.090 * math.cos(r_a), 0.118 * math.sin(r_a), 0.048)
            lp.rotation_euler = (0, 0, r_a)
            lp.scale = (0.4, 0.8, 2.2)

        create_bezier_hair_strand(
            f"{prefix}_RedCordTassel", pelvis, red_mat,
            p0=(-0.01, 0.116, 0.05), p1=(-0.03, 0.132, -0.02),
            p2=(-0.05, 0.140, -0.10), p3=(-0.07, 0.145, -0.19),
            width=0.010, thick=0.008
        )

    torso = create_joint(f"{prefix}_Torso", pelvis, (0, 0, 0.07))
    create_anatomical_torso_mesh(f"{prefix}_SeamlessTorso", torso, skin_mat, top_mat, white_mat, is_claudia=is_claudia)

    head = create_joint(f"{prefix}_Head", torso, (0, 0, 0.42))
    create_sculpted_anime_head(f"{prefix}_SculptedHead", head, skin_mat)

    create_bezier_hair_strand(
        f"{prefix}_NoseBridge", head, skin_mat,
        p0=(0.095, 0, 0.156), p1=(0.104, 0, 0.144),
        p2=(0.113, 0, 0.134), p3=(0.096, 0, 0.126),
        width=0.008, thick=0.006, steps=6
    )

    create_detailed_ear(f"{prefix}_Ear_L", head, skin_mat, ear_sh_mat, 0.088)
    create_detailed_ear(f"{prefix}_Ear_R", head, skin_mat, ear_sh_mat, -0.088)

    create_flush_anime_eye(prefix, "L", 0.036, head, white_mat, iris_mat, black_mat, skin_mat, hair_mat)
    create_flush_anime_eye(prefix, "R", -0.036, head, white_mat, iris_mat, black_mat, skin_mat, hair_mat)

    create_detailed_mouth(prefix, head, mouth_mat, white_mat, tongue_mat)

    # Full Back-of-Head Hair Cap extending down to Nape (z=0.068) so Neck/Back Skull is 100% Covered!
    create_quad_limb(
        f"{prefix}_HairBaseCap", head, [hair_mat],
        rings=[
            (0.068, 0.055, 0.068, -0.036, 0),
            (0.110, 0.082, 0.088, -0.026, 0),
            (0.165, 0.098, 0.096, -0.012, 0),
            (0.215, 0.102, 0.095, -0.002, 0),
            (0.252, 0.078, 0.074, -0.006, 0),
        ]
    )

    bangs_j = create_joint(f"{prefix}_HairBangs", head, (0, 0, 0))
    pt_joint = create_joint(f"{prefix}_Ponytail", head, (-0.092, 0, 0.220))
    pt_tip = create_joint(f"{prefix}_Ponytail_Tip", pt_joint, (-0.04, 0, 0.01))

    if is_claudia:
        # Flush Skull-Hugging Curtain Bangs (Image 2!)
        claudia_strands = [
            ((0.02, 0.01, 0.26), (0.086, 0.04, 0.235), (0.096, 0.068, 0.175), (0.078, 0.074, 0.095), 0.024),
            ((0.03, 0.01, 0.26), (0.092, 0.03, 0.230), (0.098, 0.052, 0.175), (0.088, 0.058, 0.115), 0.020),
            ((0.04, 0.00, 0.26), (0.096, 0.010, 0.228), (0.101, 0.008, 0.192), (0.099, 0.005, 0.162), 0.009),
            ((0.04, 0.00, 0.26), (0.096, -0.010, 0.228), (0.101, -0.010, 0.194), (0.099, -0.006, 0.165), 0.008),
            ((0.03, -0.01, 0.26), (0.092, -0.03, 0.230), (0.098, -0.052, 0.175), (0.088, -0.058, 0.115), 0.020),
            ((0.02, -0.01, 0.26), (0.086, -0.04, 0.235), (0.096, -0.068, 0.175), (0.078, -0.074, 0.095), 0.024),
            ((-0.02, 0.04, 0.25), (0.02, 0.092, 0.21), (0.01, 0.095, 0.15), (-0.01, 0.086, 0.085), 0.022),
            ((-0.02, -0.04, 0.25), (0.02, -0.092, 0.21), (0.01, -0.095, 0.15), (-0.01, -0.086, 0.085), 0.022),
        ]
        for idx, (p0, p1, p2, p3, w) in enumerate(claudia_strands):
            create_bezier_hair_strand(f"{prefix}_HairLock_{idx}", bangs_j, hair_mat, p0, p1, p2, p3, width=w, thick=0.007)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.040)
        bun = bpy.context.active_object
        bun.name = f"{prefix}_CrownBun"
        bpy.ops.object.shade_smooth()
        bun.data.materials.append(hair_mat)
        bun.parent = pt_joint
        bun.location = (-0.01, 0, 0.015)

        # Spiky Messy Bun Strands Fanning Up & Back (Exact Match to Image 2!)
        for p_i, (sy, sz_end) in enumerate([(-0.04, 0.06), (-0.02, 0.08), (0.0, 0.05), (0.02, 0.08), (0.04, 0.06), (0.0, -0.04)]):
            create_bezier_hair_strand(
                f"{prefix}_BunSpike_{p_i}", pt_tip, hair_mat,
                p0=(0.02, 0, 0.01), p1=(-0.01, sy * 0.6, 0.03),
                p2=(-0.04, sy * 1.1, sz_end * 0.7), p3=(-0.07, sy * 1.4, sz_end),
                width=0.018, thick=0.008
            )
    else:
        # Flush Pixie Bangs Resting Directly on Forehead Skin (No Floating Wire Gap!)
        pixie_strands = [
            ((0.02, 0.00, 0.258), (0.085, 0.052, 0.232), (0.096, 0.058, 0.202), (0.094, 0.054, 0.174), 0.018),
            ((0.03, 0.00, 0.258), (0.090, 0.028, 0.232), (0.098, 0.030, 0.204), (0.097, 0.026, 0.180), 0.015),
            ((0.03, 0.00, 0.258), (0.092, 0.004, 0.232), (0.099, 0.003, 0.206), (0.098, 0.001, 0.182), 0.014),
            ((0.03, 0.00, 0.258), (0.090, -0.022, 0.232), (0.098, -0.024, 0.204), (0.097, -0.020, 0.180), 0.015),
            ((0.02, 0.00, 0.258), (0.085, -0.050, 0.232), (0.096, -0.055, 0.202), (0.094, -0.052, 0.174), 0.018),
            ((0.00, 0.03, 0.25), (0.035, 0.086, 0.215), (0.030, 0.090, 0.185), (0.020, 0.084, 0.160), 0.016),
            ((0.00, -0.03, 0.25), (0.035, -0.086, 0.215), (0.030, -0.090, 0.185), (0.020, -0.084, 0.160), 0.016),
        ]
        for idx, (p0, p1, p2, p3, w) in enumerate(pixie_strands):
            create_bezier_hair_strand(f"{prefix}_PixieLock_{idx}", bangs_j, hair_mat, p0, p1, p2, p3, width=w, thick=0.006)

    for side, y_dir in [("L", 1), ("R", -1)]:
        sh = create_joint(f"{prefix}_Shoulder_{side}", torso, (0, 0.148 * y_dir, 0.365))
        create_quad_limb(
            f"{prefix}_UpperArm_{side}", sh, [skin_mat],
            rings=[
                (-0.25, 0.033, 0.033, 0.0, 0),
                (-0.12, 0.038, 0.037, 0.002, 0),
                (0.00, 0.043, 0.043, 0.0, 0),
            ]
        )

        elb = create_joint(f"{prefix}_Elbow_{side}", sh, (0, 0, -0.25))
        create_quad_limb(
            f"{prefix}_Forearm_{side}", elb, [skin_mat, white_mat, black_mat],
            rings=[
                (-0.21, 0.030, 0.028, 0.0, 2),
                (-0.17, 0.032, 0.030, 0.0, 1),
                (-0.14, 0.031, 0.030, 0.0, 0),
                (-0.06, 0.037, 0.036, 0.002, 0),
                (0.00, 0.034, 0.034, 0.0, 0),
            ]
        )

        wrist = create_joint(f"{prefix}_Wrist_{side}", elb, (0, 0, -0.21))
        create_quad_limb(
            f"{prefix}_MMAGlove_{side}", wrist, [black_mat, white_mat],
            rings=[
                (-0.044, 0.030, 0.022, 0.004, 1),
                (-0.030, 0.033, 0.024, 0.005, 0),
                (-0.008, 0.031, 0.023, 0.002, 0),
                (0.005, 0.028, 0.022, 0.000, 0),
            ]
        )

        create_quad_limb(
            f"{prefix}_Thumb_{side}", wrist, [skin_mat],
            rings=[(-0.032, 0.007, 0.007, 0.0, 0), (-0.015, 0.009, 0.009, 0.0, 0), (0.0, 0.011, 0.011, 0.0, 0)],
            segs=10, local_loc=(0.018, 0.018 * y_dir, -0.018), local_rot=(-15 * y_dir, 28, 0), subsurf=1
        )

        fingers_j = create_joint(f"{prefix}_Fingers_{side}", wrist, (0.008, 0, -0.042))
        for f_name, fy, flen, frad in [
            ("Index", 0.015 * y_dir, 0.034, 0.0062),
            ("Middle", 0.005 * y_dir, 0.037, 0.0065),
            ("Ring", -0.005 * y_dir, 0.034, 0.0060),
            ("Pinky", -0.015 * y_dir, 0.028, 0.0052),
        ]:
            create_quad_limb(
                f"{prefix}_{f_name}_{side}", fingers_j, [skin_mat],
                rings=[(-flen, frad * 0.8, frad * 0.8, 0.0, 0), (-flen * 0.5, frad, frad, 0.002, 0), (0.0, frad, frad, 0.0, 0)],
                segs=10, local_loc=(0, fy, 0), subsurf=1
            )

    for side, y_dir in [("L", 1), ("R", -1)]:
        hip = create_joint(f"{prefix}_Hip_{side}", pelvis, (0, 0.092 * y_dir, -0.04))
        if is_claudia:
            create_quad_limb(
                f"{prefix}_CapoeiraThigh_{side}", hip, [pant_mat],
                rings=[
                    (-0.39, 0.060, 0.058, 0.0, 0),
                    (-0.20, 0.072, 0.070, 0.004, 0),
                    (0.00, 0.082, 0.080, 0.0, 0),
                ]
            )
        else:
            # White Booty Shorts with Dark-Grey Side Triangle Slit (`short_tri=True`!)
            create_quad_limb(
                f"{prefix}_Thigh_{side}", hip, [skin_mat, pant_mat, grey_mat],
                rings=[
                    (-0.39, 0.046, 0.044, 0.0, 0),
                    (-0.22, 0.062, 0.060, 0.004, 0),
                    (-0.08, 0.074, 0.072, 0.002, 0),
                    (-0.06, 0.080, 0.078, 0.002, 1),
                    (0.01, 0.082, 0.080, 0.0, 1),
                ],
                short_tri=True
            )

        knee = create_joint(f"{prefix}_Knee_{side}", hip, (0, 0, -0.39))
        if is_claudia:
            create_quad_limb(
                f"{prefix}_CapoeiraFlare_{side}", knee, [pant_mat],
                rings=[
                    (-0.37, 0.076, 0.068, 0.010, 0),
                    (-0.22, 0.065, 0.061, 0.004, 0),
                    (-0.08, 0.059, 0.057, 0.000, 0),
                    (0.00, 0.057, 0.055, 0.000, 0),
                ]
            )
        else:
            create_quad_limb(
                f"{prefix}_BareCalf_{side}", knee, [skin_mat],
                rings=[
                    (-0.37, 0.031, 0.030, 0.0, 0),
                    (-0.24, 0.038, 0.037, 0.0, 0),
                    (-0.10, 0.051, 0.049, -0.006, 0),
                    (0.00, 0.046, 0.045, 0.0, 0),
                ]
            )

        create_quad_limb(
            f"{prefix}_BareFoot_{side}", knee, [skin_mat],
            rings=[
                (-0.415, 0.068, 0.034, 0.028, 0),
                (-0.390, 0.052, 0.031, 0.016, 0),
                (-0.365, 0.034, 0.028, 0.002, 0),
            ],
            segs=16
        )
        for t_name, ty, tlen, trad in [
            ("BigToe", -0.020 * y_dir, 0.020, 0.0072),
            ("Toe2", -0.009 * y_dir, 0.018, 0.0052),
            ("Toe3", 0.000, 0.016, 0.0048),
            ("Toe4", 0.009 * y_dir, 0.014, 0.0045),
            ("Toe5", 0.017 * y_dir, 0.012, 0.0042),
        ]:
            create_quad_limb(
                f"{prefix}_{t_name}_{side}", knee, [skin_mat],
                rings=[(-tlen, trad * 0.85, trad * 0.85, 0.0, 0), (0.0, trad, trad, 0.0, 0)],
                segs=8, local_loc=(0.088, ty, -0.410), local_rot=(0, -88, 0), subsurf=1
            )

    root.location = (base_x, 0, 0)
    root.rotation_euler = (0, 0, math.radians(z_rot_deg))

    # Automatically build the Female Referee in the Octagon whenever FB is built!
    if prefix == "FB":
        build_referee(0.55, 1.15, -110)

    return root


def build_referee(base_x=0.55, base_y=1.15, z_rot_deg=-110):
    for obj in list(bpy.data.objects):
        if obj.name.startswith("REF_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    ref_root = build_anime_fighter("REF", base_x, z_rot_deg, is_blue_hoodie=False)
    ref_root.location = (base_x, base_y, 0)

    blue_polo = create_toon_material("REF_BluePolo", (0.12, 0.32, 0.78, 1), (0.06, 0.18, 0.48, 1))
    black_pants = create_toon_material("REF_BlackPants", (0.06, 0.06, 0.08, 1), (0.02, 0.02, 0.03, 1))
    brown_shoe = create_toon_material("REF_BrownShoe", (0.24, 0.12, 0.08, 1), (0.12, 0.05, 0.03, 1))

    torso_obj = bpy.data.objects.get("REF_SeamlessTorso")
    if torso_obj:
        for i in range(len(torso_obj.data.materials)):
            torso_obj.data.materials[i] = blue_polo

    # Black Bowtie on Referee's Collar (Image 2!)
    head_j = bpy.data.objects.get("REF_Head")
    if head_j:
        bpy.ops.mesh.primitive_cube_add(size=0.022)
        bow = bpy.context.active_object
        bow.name = "REF_Bowtie"
        bow.data.materials.append(black_pants)
        bow.parent = head_j
        bow.location = (0.055, 0, -0.01)
        bow.scale = (0.4, 1.8, 1.1)

    pelvis_obj = bpy.data.objects.get("REF_PelvisMesh")
    if pelvis_obj:
        pelvis_obj.data.materials[0] = black_pants

    for side in ("L", "R"):
        for p_name in (f"REF_Thigh_{side}", f"REF_BareCalf_{side}"):
            o = bpy.data.objects.get(p_name)
            if o:
                for i in range(len(o.data.materials)):
                    o.data.materials[i] = black_pants
        f_obj = bpy.data.objects.get(f"REF_BareFoot_{side}")
        if f_obj:
            f_obj.data.materials[0] = brown_shoe

    # Pose Referee in Alert Walking/Watching Stance (Like Image 2!)
    for j_n, r_d in [
        ("REF_Pelvis", (0, 4, 10)),
        ("REF_Torso", (0, 6, -10)),
        ("REF_Shoulder_L", (12, -18, 0)),
        ("REF_Elbow_L", (0, -25, 0)),
        ("REF_Shoulder_R", (-12, 12, 0)),
        ("REF_Elbow_R", (0, -22, 0)),
        ("REF_Hip_L", (0, -18, 0)),
        ("REF_Knee_L", (0, 22, 0)),
        ("REF_Hip_R", (0, 18, 0)),
        ("REF_Knee_R", (0, 15, 0)),
    ]:
        o = bpy.data.objects.get(j_n)
        if o:
            o.rotation_euler = [math.radians(a) for a in r_d]

    return ref_root
