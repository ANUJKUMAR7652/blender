import bpy
import math
import random
from .audio_vfx import add_sfx_at_frame, trigger_vfx, clear_vse_audio


def kf(obj_name, frame, loc=None, rot_deg=None, scale=None, interp='BEZIER'):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        return
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot_deg is not None:
        obj.rotation_euler = [math.radians(a) for a in rot_deg]
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if int(kp.co.x) == int(frame):
                    kp.interpolation = interp


def set_camera_3d_orbit(frame, cam_loc, target_loc, lens=38.0):
    kf("FightCam", frame, loc=cam_loc)
    kf("CamTarget", frame, loc=target_loc)
    cam = bpy.data.objects.get("FightCam")
    if cam and cam.data:
        cam.data.lens = lens
        cam.data.keyframe_insert(data_path="lens", frame=frame)


def set_face_and_hair(p, f, mode="FIERCE", hair_whip=(0, 0, 0), open_hands=(False, False)):
    presets = {
        "WINCE": ((1, 1, 0.12), (1, 1, 0.12), 2.2, 2.2, (0.006, 0, 0), 24, (0.30, 1.2, 0.30)),
        "PAIN": ((1, 1, 0.25), (1, 1, 0.25), 1.8, 1.8, (0.006, 0, 0.003), -18, (0.30, 1.15, 0.90)),
        "DAZED_KO": ((1, 1, 0.42), (1, 1, 0.14), 1.5, 2.2, (0.006, 0.002, 0.005), -20, (0.32, 0.95, 1.05)),
        "FIERCE": ((1, 1, 1.0), (1, 1, 1.0), 0.5, 0.5, (0.006, 0, 0), 15, (0.30, 1.05, 0.22)),
    }
    el_s, er_s, ll_z, lr_z, ir_loc, br_t, m_sc = presets.get(mode, presets["FIERCE"])
    kf(f"{p}_Eye_L", f, scale=el_s)
    kf(f"{p}_Eye_R", f, scale=er_s)
    kf(f"{p}_Lid_L", f, scale=(1.0, 1.0, ll_z))
    kf(f"{p}_Lid_R", f, scale=(1.0, 1.0, lr_z))
    kf(f"{p}_Iris_L", f, loc=ir_loc)
    kf(f"{p}_Iris_R", f, loc=ir_loc)
    kf(f"{p}_Brow_L", f, rot_deg=(br_t, 0, -18))
    kf(f"{p}_Brow_R", f, rot_deg=(-br_t, 0, 18))
    kf(f"{p}_Mouth", f, scale=m_sc)

    hx, hy, hz = hair_whip
    kf(f"{p}_HairBangs", f, rot_deg=(hx * 0.3, hy * 0.25, hz * 0.25))
    kf(f"{p}_Ponytail", f, rot_deg=(hx, hy, hz))
    kf(f"{p}_Ponytail_Tip", f, rot_deg=(hx * 1.2, hy * 1.3, hz * 1.2))

    open_l, open_r = open_hands
    kf(f"{p}_Fingers_L", f, rot_deg=(0, 5 if open_l else -80, 0))
    kf(f"{p}_Fingers_R", f, rot_deg=(0, 5 if open_r else -80, 0))


def lock_char(p, f, x_world, z_rot, p_loc, p_rot, t_rot, h_rot,
              sh_l, el_l, sh_r, el_r, hip_l, kn_l, hip_r, kn_r,
              face="FIERCE", whip=(0, 0, 0), hands=(False, False)):
    kf(f"{p}_Root", f, loc=(x_world, 0, 0), rot_deg=(0, 0, z_rot))
    kf(f"{p}_Pelvis", f, loc=p_loc, rot_deg=p_rot)
    kf(f"{p}_Torso", f, rot_deg=t_rot)
    kf(f"{p}_Head", f, rot_deg=h_rot)
    kf(f"{p}_Shoulder_L", f, rot_deg=sh_l)
    kf(f"{p}_Elbow_L", f, rot_deg=el_l)
    kf(f"{p}_Shoulder_R", f, rot_deg=sh_r)
    kf(f"{p}_Elbow_R", f, rot_deg=el_r)
    kf(f"{p}_Hip_L", f, rot_deg=hip_l)
    kf(f"{p}_Knee_L", f, rot_deg=kn_l)
    kf(f"{p}_Hip_R", f, rot_deg=hip_r)
    kf(f"{p}_Knee_R", f, rot_deg=kn_r)
    set_face_and_hair(p, f, mode=face, hair_whip=whip, open_hands=hands)


def pose_guard(p, f, x, zr=0, open_lead=False):
    lock_char(p, f, x, zr, (0, 0, 0.76), (0, 6, -20), (0, 10, 20), (0, -8, -12),
              (16, -56, -15), (-12, -108, 0), (-16, -46, 15), (15, -112, 0),
              (5, -26, 0), (0, 32, 0), (-5, 20, 0), (0, 20, 0), "FIERCE", (0, 5, 0), (open_lead, False))


def pose_step(p, f, x, zr, phase=0):
    hl, kl = ((0, -42, 0), (0, 52, 0)) if phase % 2 == 0 else ((0, 28, 0), (0, 24, 0))
    hr, kr = ((0, 28, 0), (0, 24, 0)) if phase % 2 == 0 else ((0, -42, 0), (0, 52, 0))
    lock_char(p, f, x, zr, (0, 0, 0.74), (0, 16, 0), (0, 14, 12 if phase % 2 == 0 else -12), (0, -14, 0),
              (15, -35, 0), (0, -95, 0), (-15, -60, 0), (0, -95, 0), hl, kl, hr, kr, "FIERCE", (0, 22, 0))
    add_sfx_at_frame('STEP', f, 5)


def pose_chamber(p, f, x, zr, kind="PUNCH_R", grab=False):
    if kind in ("KICK_R", "KICK_L"):
        hl, kl = ((0, 6, 0), (0, 12, 0)) if kind == "KICK_R" else ((10, -82, 0), (0, 95, 0))
        hr, kr = ((-10, -82, 0), (0, 95, 0)) if kind == "KICK_R" else ((0, 6, 0), (0, 12, 0))
        lock_char(p, f, x, zr, (0.04, 0, 0.78), (0, -6, 0), (0, -4, -15), (0, 6, 0),
                  (20, -52, -15), (-10, -105, 0), (-20, -52, 15), (10, -105, 0), hl, kl, hr, kr, "FIERCE", (0, 15, 10))
    else:
        sh_l = (5, -88, 0) if grab else (18, -62, -15)
        el_l = (0, -12, 0) if grab else (0, -112, 0)
        lock_char(p, f, x, zr, (0, 0, 0.76), (0, 8, -14), (0, 12, -28), (0, -10, 16),
                  sh_l, el_l, (-25, 18, 20), (0, -112, 0),
                  (5, -28, 0), (0, 34, 0), (-5, 22, 0), (0, 22, 0), "FIERCE", (0, -12, 20), (grab, False))


def pose_strike(p, f, x, zr, style="STRAIGHT"):
    if style in ("HIGH_KICK", "LOW_KICK", "TEEP_KICK", "KNEE"):
        if style == "HIGH_KICK":
            lock_char(p, f, x, zr, (0.12, 0, 0.78), (0, -14, 0), (0, -10, -28), (0, 14, 18),
                      (24, -48, -20), (-10, -95, 0), (-28, -35, 25), (10, -90, 0),
                      (0, 14, 0), (0, 8, 0), (0, -108, 0), (0, 4, 0), "FIERCE", (0, 34, 24))
        elif style == "TEEP_KICK":
            lock_char(p, f, x, zr, (0.12, 0, 0.78), (0, -12, 0), (0, -10, 22), (0, 12, -12),
                      (24, -38, -20), (-10, -90, 0), (-22, -52, 20), (10, -100, 0),
                      (0, -94, 0), (0, 4, 0), (0, 12, 0), (0, 8, 0), "FIERCE", (0, 28, -18))
        elif style == "LOW_KICK":
            lock_char(p, f, x, zr, (0.10, 0, 0.76), (0, 4, 0), (0, 10, -25), (0, -6, 15),
                      (20, -55, -18), (-10, -105, 0), (-25, -40, 22), (10, -95, 0),
                      (0, -8, 0), (0, 18, 0), (-8, -68, 0), (0, 8, 0), "FIERCE", (0, 22, 18))
        else:  # KNEE
            lock_char(p, f, x, zr, (0.10, 0, 0.79), (0, -6, 0), (0, 8, -18), (0, -6, 10),
                      (-12, -78, 0), (0, -85, 0), (12, -78, 0), (0, -85, 0),
                      (0, 6, 0), (0, 10, 0), (0, -92, 0), (0, 115, 0), "FIERCE", (0, 25, 10))
    else:
        pz = 0.68 if style == "BODY_BLOW" else 0.75
        sh_r = (-20, -92, 30) if style == "HOOK" else ((-8, -76, 15) if style == "UPPERCUT" else ((-26, -94, 42) if style == "ELBOW" else (4, -94, 0)))
        el_r = (0, -45, 0) if style == "HOOK" else ((0, -86, 0) if style == "UPPERCUT" else ((0, -122, 0) if style == "ELBOW" else (0, -6, 0)))
        lock_char(p, f, x, zr, (0.06, 0, pz), (0, 12, 18), (0, 16, 38), (0, -12, -22),
                  (20, -45, -20), (-15, -114, 0), sh_r, el_r,
                  (5, -34, 0), (0, 42, 0), (-5, 26, 0), (0, 16, 0), "FIERCE", (0, 32, -32))


def pose_react(p, f, x, zr, rtype="HEAD_SNAP", dazed=False):
    if rtype == "BLOCK":
        lock_char(p, f, x, zr, (0, 0, 0.75), (0, 4, 0), (0, -10, 10), (0, 14, -10),
                  (-16, -82, -22), (-22, -115, 0), (16, -78, 22), (22, -115, 0),
                  (5, -28, 0), (0, 36, 0), (-5, 24, 0), (0, 22, 0), "WINCE", (0, -18, 10), (True, False))
    elif rtype == "STOMACH":
        lock_char(p, f, x, zr, (-0.06, 0, 0.72), (0, -8, 0), (0, 36, 8), (0, 24, 0),
                  (-15, -48, -20), (-25, -105, 0), (15, -48, 20), (25, -105, 0),
                  (5, -22, 0), (0, 38, 0), (-5, 28, 0), (0, 26, 0), "PAIN", (0, 38, 0))
    elif rtype == "CHIN_UP":
        lock_char(p, f, x, zr, (0, 0, 0.77), (0, -10, 0), (0, -26, 0), (0, -48, 12),
                  (38, -42, -35), (0, -55, 0), (-38, -42, 35), (0, -55, 0),
                  (5, -18, 0), (0, 28, 0), (-5, 24, 0), (0, 22, 0), "PAIN", (0, -42, -12))
    elif rtype == "GUARD_BREAK":
        lock_char(p, f, x, zr, (0, 0, 0.75), (0, -8, 12), (0, -24, 18), (10, -28, 25),
                  (48, -75, -55), (0, -40, 0), (-48, -75, 55), (0, -40, 0),
                  (5, -24, 0), (0, 34, 0), (-5, 26, 0), (0, 24, 0), "PAIN", (10, -32, -25), (True, True))
    elif rtype == "LEG_BUCKLE":
        lock_char(p, f, x, zr, (0, 0, 0.60), (10, 16, -15), (0, 22, 15), (0, 16, -10),
                  (22, -48, -15), (0, -95, 0), (-22, -48, 15), (0, -95, 0),
                  (-20, -52, 0), (0, 82, 0), (0, 25, 0), (0, 48, 0), "PAIN", (0, 25, 12))
    elif rtype == "DUCK":
        lock_char(p, f, x, zr, (0, 0, 0.48), (0, 34, 0), (0, 28, 0), (0, -22, 0),
                  (15, -55, -15), (0, -110, 0), (-15, -55, 15), (0, -110, 0),
                  (0, -72, 0), (0, 92, 0), (0, 42, 0), (0, 82, 0), "FIERCE", (0, 28, 0))
    elif rtype == "KO_KNEES":
        lock_char(p, f, x, zr, (0, 0, 0.36), (0, 32, 0), (0, 38, 0), (0, 35, 0),
                  (8, -22, 0), (0, -12, 0), (-8, -22, 0), (0, -12, 0),
                  (0, -45, 0), (0, 125, 0), (0, -35, 0), (0, 125, 0), "DAZED_KO", (0, 40, 0), (True, True))
    else:  # HEAD_SNAP
        lock_char(p, f, x, zr, (0, 0, 0.75), (0, -6, 0), (0, -20, 20), (14, -32, 42),
                  (30, -58, -38), (0, -65, 0), (-30, -58, 38), (0, -65, 0),
                  (5, -24, 0), (0, 34, 0), (-5, 26, 0), (0, 24, 0),
                  "DAZED_KO" if dazed else "PAIN", (15, -38, -42))


def execute_combat_exchange(move_code, attacker, f_start, f_end, center_x=0.0, ex_idx=0):
    defender = "FB" if attacker == "FA" else "FA"
    span = max(18, f_end - f_start)
    F = lambda r: int(f_start + r * span)
    f_s1, f_s2, f_ch, f_im = F(0.10), F(0.20), max(F(0.20) + 2, F(0.32)), max(F(0.32) + 3, F(0.45))
    f_pre, f_rec_pk, f_end_g = f_im - 1, min(f_end - 4, F(0.66)), F(0.92)

    dist = 0.80 if "KICK" in move_code else (0.68 if move_code in ("ELBOW_STRIKE", "CLINCH_KNEE", "TAKEDOWN_SLAM", "WRIST_TRAP_BLOCK") else 0.76)
    xa = max(-1.9, min(1.2, center_x - dist * 0.5))
    xb = xa + dist
    pos_a, pos_d = (xa, xb) if attacker == "FA" else (xb, xa)
    rot_a, rot_d = (0, 180) if attacker == "FA" else (180, 0)
    k_dir = 0.22 if attacker == "FA" else -0.22
    mid_x = (xa + xb) * 0.5
    hit_x = mid_x + (0.08 if attacker == "FA" else -0.08)
    orb = 1 if ex_idx % 2 == 0 else -1

    set_camera_3d_orbit(f_s1, (mid_x - 0.55 * orb, -2.85, 1.18), (mid_x, 0, 1.15), 38.0)
    pose_step(attacker, f_s1, pos_a - k_dir * 0.35, rot_a, 0)
    pose_guard(attacker, f_s2, pos_a, rot_a)
    pose_guard(defender, f_s2, pos_d, rot_d)

    # Chamber Strike + Hold Defender in Guard until `f_pre` (ZERO FAKE REACTION!)
    k_type = "KICK_L" if move_code == "TEEP_KICK" else ("KICK_R" if "KICK" in move_code or move_code == "CLINCH_KNEE" else "PUNCH_R")
    if move_code not in ("DUCK_COUNTER", "TAKEDOWN_SLAM"):
        pose_chamber(attacker, f_ch, pos_a, rot_a, k_type, grab=(move_code == "WRIST_TRAP_BLOCK"))
        pose_guard(defender, f_pre, pos_d, rot_d, open_lead=(move_code == "WRIST_TRAP_BLOCK"))

    add_sfx_at_frame('WHOOSH', max(1, f_im - 2), 1)

    if move_code in ("JAB_BLOCK", "WRIST_TRAP_BLOCK"):
        set_camera_3d_orbit(f_ch, (hit_x - 0.55, -1.20, 1.42), (hit_x, 0, 1.38), 50.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "STRAIGHT")
        pose_react(defender, f_im, pos_d, rot_d, "BLOCK")
        set_camera_3d_orbit(f_rec_pk, (hit_x + 0.60, -1.15, 1.40), (pos_d, 0, 1.40), 52.0)
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.4, rot_d, "BLOCK")
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.38), 0.78, 4)
        add_sfx_at_frame('BLOCK', f_im, 2)

    elif move_code in ("CROSS_HIT", "DASH_ARM_TRAP_HOOK"):
        set_camera_3d_orbit(f_ch, (hit_x + 0.35 * orb, -1.55, 1.38), (pos_d, 0, 1.42), 46.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "STRAIGHT")
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.3, rot_d, "HEAD_SNAP")
        pose_step(defender, (f_im + f_rec_pk) // 2, pos_d + k_dir * 0.65, rot_d, 1)
        pose_react(defender, f_rec_pk, pos_d + k_dir * 1.0, rot_d, "HEAD_SNAP")
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.42), 0.95, 4)
        trigger_vfx("VFX_Sparks", f_im, (hit_x, 0, 1.42), 0.85, 4)
        add_sfx_at_frame('PUNCH', f_im, 2)

    elif move_code == "HOOK_GUARD_BREAK":
        set_camera_3d_orbit(f_ch, (hit_x - 0.45 * orb, -1.55, 1.34), (pos_d, 0, 1.34), 46.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "HOOK")
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.3, rot_d, "GUARD_BREAK")
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.8, rot_d, "GUARD_BREAK")
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.38), 1.0, 4)
        add_sfx_at_frame('PUNCH', f_im, 2)

    elif move_code == "BODY_BLOW":
        set_camera_3d_orbit(f_ch, (pos_a - k_dir * 1.8, -1.25, 1.25), (pos_d, 0, 1.04), 50.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "BODY_BLOW")
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.2, rot_d, "STOMACH")
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.5, rot_d, "STOMACH")
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.04), 0.92, 4)
        add_sfx_at_frame('PUNCH', f_im, 2)

    elif move_code in ("UPPERCUT_HIT", "DUCK_COUNTER"):
        if move_code == "DUCK_COUNTER":
            pose_strike(defender, f_ch, pos_d, rot_d, "HOOK")
            pose_react(attacker, f_ch, pos_a, rot_a, "DUCK")
            pose_guard(defender, f_pre, pos_d, rot_d)
        set_camera_3d_orbit(f_ch, (hit_x + 0.40, -1.45, 1.05), (pos_d, 0, 1.42), 48.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "UPPERCUT")
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.3, rot_d, "CHIN_UP")
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.7, rot_d, "CHIN_UP")
        trigger_vfx("VFX_Sparks", f_im, (hit_x, 0, 1.44), 1.0, 4)
        add_sfx_at_frame('PUNCH', f_im, 2)

    elif move_code == "ELBOW_STRIKE":
        set_camera_3d_orbit(f_ch, (hit_x - 0.35, -1.25, 1.40), (pos_d, 0, 1.42), 54.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "ELBOW")
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.3, rot_d, "HEAD_SNAP")
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.8, rot_d, "HEAD_SNAP")
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.42), 1.05, 4)
        add_sfx_at_frame('PUNCH', f_im, 2)

    elif move_code in ("HIGH_KICK", "LOW_KICK", "TEEP_KICK", "CLINCH_KNEE"):
        st = "KNEE" if move_code == "CLINCH_KNEE" else move_code
        rt = "LEG_BUCKLE" if move_code == "LOW_KICK" else ("STOMACH" if move_code in ("TEEP_KICK", "CLINCH_KNEE") else "HEAD_SNAP")
        tz = 0.58 if move_code == "LOW_KICK" else (1.05 if rt == "STOMACH" else 1.38)
        set_camera_3d_orbit(f_ch, (mid_x + 0.50 * orb, -2.15, tz + 0.1), (pos_d, 0, tz), 44.0)
        pose_strike(attacker, f_im, pos_a, rot_a, st)
        pose_react(defender, f_im + 1, pos_d + k_dir * 0.3, rot_d, rt)
        pose_react(defender, f_rec_pk, pos_d + k_dir * 0.8, rot_d, rt)
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, tz), 1.10, 4)
        add_sfx_at_frame('KICK', f_im, 3)

    elif move_code == "TAKEDOWN_SLAM":
        pose_strike(defender, f_ch, pos_d, rot_d, "HOOK")
        pose_react(attacker, f_ch, pos_a, rot_a, "DUCK")
        set_camera_3d_orbit(f_ch + 1, (hit_x + 0.35, -1.75, 0.28), (mid_x, 0, 1.05), 42.0)
        lock_char(attacker, f_im, pos_a, rot_a, (0.08, 0, 0.80), (0, -12, 0), (0, -10, 0), (0, 12, 0),
                  (-15, -85, 0), (0, -45, 0), (15, -85, 0), (0, -45, 0), (0, -20, 0), (0, 25, 0), (0, 20, 0), (0, 25, 0), "FIERCE", (0, -25, 0), (True, True))
        lock_char(defender, f_im, pos_d, rot_d, (0, 0, 1.32), (0, 42, 0), (0, 25, 0), (0, 20, 0),
                  (25, -45, -20), (0, -60, 0), (-25, -45, 20), (0, -60, 0), (0, -50, 0), (0, 45, 0), (0, 30, 0), (0, 45, 0), "PAIN", (0, 35, 0), (True, True))
        set_camera_3d_orbit(f_rec_pk - 1, (0, -2.95, 0.95), (mid_x, 0, 0.85), 38.0)
        pose_react(attacker, f_rec_pk, pos_a - k_dir * 0.5, rot_a, "DUCK")
        pose_guard(defender, f_rec_pk, pos_d + k_dir, rot_d)
        trigger_vfx("VFX_DustRing", f_rec_pk, (pos_d, 0, 0.02), 1.45, 5)
        add_sfx_at_frame('SLAM', f_rec_pk, 4)

    elif move_code == "KNOCKOUT_FINISHER":
        set_camera_3d_orbit(f_s2, (mid_x - 0.45, -1.65, 1.35), (pos_d, 0, 1.35), 45.0)
        pose_strike(attacker, f_ch, pos_a, rot_a, "HOOK")
        pose_react(defender, f_ch + 1, pos_d, rot_d, "GUARD_BREAK")
        add_sfx_at_frame('PUNCH', f_ch, 2)

        set_camera_3d_orbit(f_pre - 2, (pos_a + 0.35, -1.15, 1.42), (pos_d, 0, 1.40), 52.0)
        pose_chamber(attacker, f_pre, pos_a, rot_a, "PUNCH_R", grab=True)
        pose_react(defender, f_pre, pos_d, rot_d, "GUARD_BREAK")

        set_camera_3d_orbit(f_im, (pos_d - 0.15, -0.98, 1.43), (pos_d, 0, 1.42), 62.0)
        pose_strike(attacker, f_im, pos_a, rot_a, "ELBOW")
        pose_react(defender, f_im + 1, pos_d, rot_d, "HEAD_SNAP", dazed=True)
        pose_react(defender, f_rec_pk, pos_d, rot_d, "HEAD_SNAP", dazed=True)
        trigger_vfx("VFX_Shockwave", f_im, (hit_x, 0, 1.42), 1.15, 4)
        trigger_vfx("VFX_Sparks", f_im, (hit_x, 0, 1.42), 1.10, 4)
        add_sfx_at_frame('KICK', f_im, 3)

        set_camera_3d_orbit(f_rec_pk + 2, (-0.15, -2.85, 0.96), (mid_x, 0, 0.85), 38.0)
        pose_react(defender, f_end_g, pos_d, rot_d, "KO_KNEES")
        pose_guard(attacker, f_end_g, pos_a, rot_a)
        pose_react(defender, f_end, pos_d, rot_d, "KO_KNEES")
        pose_guard(attacker, f_end, pos_a, rot_a)
        trigger_vfx("VFX_DustRing", f_end_g - 1, (pos_d, 0, 0.02), 1.25, 5)
        add_sfx_at_frame('SLAM', f_end_g - 1, 4)
        return

    set_camera_3d_orbit(f_end_g, (mid_x + 0.30 * orb, -3.00, 1.12), (mid_x, 0, 1.12), 38.0)
    pose_guard(attacker, f_end_g, pos_a, rot_a)
    pose_guard(defender, f_end_g, pos_d, rot_d)


ALL_MOVES = [
    "JAB_BLOCK", "WRIST_TRAP_BLOCK", "CROSS_HIT", "DASH_ARM_TRAP_HOOK",
    "HOOK_GUARD_BREAK", "BODY_BLOW", "UPPERCUT_HIT", "ELBOW_STRIKE",
    "DUCK_COUNTER", "HIGH_KICK", "TEEP_KICK", "LOW_KICK", "CLINCH_KNEE", "TAKEDOWN_SLAM"
]


def get_fight_sequence(fight_no):
    presets = {
        1: [("JAB_BLOCK", "FB"), ("WRIST_TRAP_BLOCK", "FA"), ("CROSS_HIT", "FA")],
        2: [("JAB_BLOCK", "FA"), ("DUCK_COUNTER", "FA"), ("TAKEDOWN_SLAM", "FA")],
        3: [("DASH_ARM_TRAP_HOOK", "FB"), ("LOW_KICK", "FA"), ("CROSS_HIT", "FB")],
        4: [("BODY_BLOW", "FB"), ("UPPERCUT_HIT", "FB"), ("ELBOW_STRIKE", "FB")],
        5: [("HOOK_GUARD_BREAK", "FB"), ("ELBOW_STRIKE", "FB"), ("KNOCKOUT_FINISHER", "FB")],
        6: [
            ("JAB_BLOCK", "FB"), ("WRIST_TRAP_BLOCK", "FA"),
            ("DUCK_COUNTER", "FA"), ("TAKEDOWN_SLAM", "FA"),
            ("DASH_ARM_TRAP_HOOK", "FB"), ("LOW_KICK", "FA"),
            ("BODY_BLOW", "FB"), ("UPPERCUT_HIT", "FB"),
            ("HIGH_KICK", "FA"), ("KNOCKOUT_FINISHER", "FB")
        ],
    }
    if fight_no in presets:
        return presets[fight_no]
    rng = random.Random(fight_no * 9973)
    seq = [(rng.choice(ALL_MOVES), "FA" if (i + fight_no) % 2 == 0 else "FB") for i in range(5 + (fight_no % 4))]
    seq.append((rng.choice(["KNOCKOUT_FINISHER", "HIGH_KICK", "TAKEDOWN_SLAM"]), "FB" if fight_no % 2 == 1 else "FA"))
    return seq


def apply_fight_choreography(fight_no, start_f, end_f):
    for obj in bpy.data.objects:
        if obj.name.startswith(("FA_", "FB_", "FightCam", "CamTarget", "VFX_")):
            obj.animation_data_clear()
    clear_vse_audio()

    seq = get_fight_sequence(fight_no)
    step = max(36, end_f - start_f) // len(seq)
    pose_guard("FA", start_f, -0.80, 0)
    pose_guard("FB", start_f, 0.80, 180)
    set_camera_3d_orbit(start_f, (0, -3.10, 1.15), (0, 0, 1.15), 38.0)

    for idx, (mv, att) in enumerate(seq):
        s_f = start_f + idx * step
        e_f = start_f + (idx + 1) * step if idx < len(seq) - 1 else end_f
        execute_combat_exchange(mv, att, s_f, e_f, center_x=math.sin(idx * 1.2) * 0.15, ex_idx=idx)
