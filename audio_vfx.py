import bpy
import math
import random
import wave
import struct
import os
import tempfile
from .materials_arena import create_vfx_emission_material

SFX_CACHE = {}


def generate_fight_sfx():
    tmp_dir = tempfile.gettempdir()
    sample_rate = 22050

    def write_wav(filename, samples):
        path = os.path.join(tmp_dir, filename)
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            data = b''.join(struct.pack('<h', max(-32767, min(32767, int(s * 32767)))) for s in samples)
            wf.writeframes(data)
        return path

    rng = random.Random(101)

    whoosh = [
        max(-1.0, min(1.0, (0.38 * math.sin(2 * math.pi * (220 + 280 * (1 - i / 2425)) * (i / sample_rate)) + 0.62 * rng.uniform(-1, 1)) * (math.sin(math.pi * (i / 2425)) ** 1.3) * 0.48))
        for i in range(2425)
    ]
    SFX_CACHE['WHOOSH'] = write_wav("fg8_whoosh.wav", whoosh)

    punch = [
        max(-1.0, min(1.0, (0.82 * math.cos(2 * math.pi * (165 * math.exp(-(i / sample_rate) * 16) + 42) * (i / sample_rate)) + 0.78 * rng.uniform(-1, 1) * math.exp(-(i / sample_rate) * 58)) * math.exp(-(i / sample_rate) * 24) * 0.98))
        for i in range(4410)
    ]
    SFX_CACHE['PUNCH'] = write_wav("fg8_punch.wav", punch)

    block = [
        max(-1.0, min(1.0, (0.62 * math.cos(2 * math.pi * (350 * math.exp(-(i / sample_rate) * 20) + 98) * (i / sample_rate)) + 0.85 * rng.uniform(-1, 1) * math.exp(-(i / sample_rate) * 52)) * math.exp(-(i / sample_rate) * 35) * 0.92))
        for i in range(3087)
    ]
    SFX_CACHE['BLOCK'] = write_wav("fg8_block.wav", block)

    kick = [
        max(-1.0, min(1.0, (0.88 * math.cos(2 * math.pi * (200 * math.exp(-(i / sample_rate) * 16) + 35) * (i / sample_rate)) + 0.85 * rng.uniform(-1, 1) * math.exp(-(i / sample_rate) * 40)) * math.exp(-(i / sample_rate) * 18) * 1.0))
        for i in range(5733)
    ]
    SFX_CACHE['KICK'] = write_wav("fg8_kick.wav", kick)

    slam = [
        max(-1.0, min(1.0, (0.90 * math.cos(2 * math.pi * (108 * math.exp(-(i / sample_rate) * 9) + 26) * (i / sample_rate)) + 0.58 * rng.uniform(-1, 1) * math.exp(-(i / sample_rate) * 19)) * math.exp(-(i / sample_rate) * 9.8) * 1.0))
        for i in range(9702)
    ]
    SFX_CACHE['SLAM'] = write_wav("fg8_slam.wav", slam)

    step_snd = [
        max(-1.0, min(1.0, (math.cos(2 * math.pi * 140 * (i / sample_rate)) + rng.uniform(-1, 1) * 0.5) * math.exp(-(i / sample_rate) * 55) * 0.32))
        for i in range(1543)
    ]
    SFX_CACHE['STEP'] = write_wav("fg8_step.wav", step_snd)
    return SFX_CACHE


def clear_vse_audio():
    scene = bpy.context.scene
    if scene.sequence_editor:
        for seq in list(scene.sequence_editor.sequences_all):
            scene.sequence_editor.sequences.remove(seq)


def add_sfx_at_frame(sfx_type, frame, channel=1):
    scene = bpy.context.scene
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    if not SFX_CACHE:
        generate_fight_sfx()
    filepath = SFX_CACHE.get(sfx_type)
    if filepath and os.path.exists(filepath):
        ch = channel
        while ch < 32:
            try:
                strip = scene.sequence_editor.sequences.new_sound(
                    name=f"SFX_{sfx_type}_{frame}", filepath=filepath,
                    channel=ch, frame_start=max(1, int(frame))
                )
                strip.volume = 1.0
                break
            except Exception:
                ch += 1


def build_vfx_system():
    bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.018, major_segments=28, minor_segments=12)
    ring = bpy.context.active_object
    ring.name = "VFX_Shockwave"
    ring.rotation_euler = (0, math.radians(90), 0)
    ring.scale = (0, 0, 0)
    ring.data.materials.append(create_vfx_emission_material("VFX_Ring_Mat", (0.85, 0.96, 1.0, 1.0), 8.0))

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.16)
    sparks = bpy.context.active_object
    sparks.name = "VFX_Sparks"
    sparks.scale = (0, 0, 0)
    sparks.data.materials.append(create_vfx_emission_material("VFX_Spark_Mat", (1.0, 0.72, 0.18, 1.0), 10.0))

    bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.024, major_segments=28, minor_segments=12)
    dust = bpy.context.active_object
    dust.name = "VFX_DustRing"
    dust.scale = (0, 0, 0)
    dust.data.materials.append(create_vfx_emission_material("VFX_Dust_Mat", (0.90, 0.90, 0.92, 1.0), 3.0))


def trigger_vfx(vfx_name, frame, loc, max_scale=1.0, duration=4):
    obj = bpy.data.objects.get(vfx_name)
    if not obj:
        return
    obj.location = loc
    obj.keyframe_insert(data_path="location", frame=max(1, frame - 1))
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="location", frame=frame + duration)

    for fr, sc in [
        (max(1, frame - 1), 0.001),
        (frame, max_scale * 0.55),
        (frame + duration - 1, max_scale),
        (frame + duration, 0.001),
    ]:
        obj.scale = (sc, sc, sc)
        obj.keyframe_insert(data_path="scale", frame=fr)
