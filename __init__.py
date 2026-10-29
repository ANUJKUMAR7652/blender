bl_info = {
    "name": "Anime Fight Generator Pro v8.0 (Multi-File)",
    "author": "AI Fight Director",
    "version": (8, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar (N) > Fight Gen Pro",
    "description": "Multi-File Seamless Quad Anime Fighters, 3D Orbit Camera, VFX, Audio & 105+ Fights",
    "category": "Animation",
}

import bpy
import os
from .materials_arena import setup_studio_environment
from .character_builder import build_anime_fighter
from .audio_vfx import build_vfx_system, generate_fight_sfx
from .combat_engine import apply_fight_choreography


def rebuild_full_scene():
    setup_studio_environment()
    build_anime_fighter("FA", -0.80, 0, is_blue_hoodie=True)
    build_anime_fighter("FB", 0.80, 180, is_blue_hoodie=False)
    build_vfx_system()

    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'
                        space.show_region_ui = True
                        space.region_3d.view_perspective = 'CAMERA'
                        space.overlay.show_relationship_lines = False
                        space.overlay.show_extras = False


class FIGHTGEN_Properties(bpy.types.PropertyGroup):
    fight_number: bpy.props.IntProperty(name="Fight No. (1-105)", default=6, min=1, max=105)
    fight_duration: bpy.props.FloatProperty(name="Duration (Seconds)", default=26.0, min=3.0, max=300.0)


class FIGHTGEN_OT_SetupArena(bpy.types.Operator):
    bl_idname = "fightgen.setup_arena"
    bl_label = "1. Rebuild Studio & Clean Quad Fighters"

    def execute(self, context):
        rebuild_full_scene()
        bpy.ops.fightgen.start_fight()
        return {'FINISHED'}


class FIGHTGEN_OT_StartFight(bpy.types.Operator):
    bl_idname = "fightgen.start_fight"
    bl_label = "2. Generate & Play Fight!"

    def execute(self, context):
        props = context.scene.fightgen_props
        if not bpy.data.objects.get("FA_Root") or not bpy.data.objects.get("FB_Root"):
            rebuild_full_scene()

        total_frames = max(48, int(props.fight_duration * context.scene.render.fps))
        context.scene.frame_start = 1
        context.scene.frame_end = total_frames
        context.scene.frame_current = 1
        context.scene.use_audio = False
        context.scene.sync_mode = 'AUDIO_SYNC'
        context.scene.use_audio_scrub = True

        apply_fight_choreography(props.fight_number, 1, total_frames)

        if not context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        return {'FINISHED'}


class FIGHTGEN_OT_ConfigureMP4(bpy.types.Operator):
    bl_idname = "fightgen.configure_mp4"
    bl_label = "3. Setup MP4 Video + Audio Export"

    def execute(self, context):
        scene = context.scene
        out_path = os.path.join(os.path.expanduser("~"), "Desktop", f"Anime_Fight_{scene.fightgen_props.fight_number}.mp4")
        scene.render.filepath = out_path
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.audio_codec = 'AAC'
        self.report({'INFO'}, f"MP4 Export Ready: {out_path}")
        return {'FINISHED'}


class FIGHTGEN_PT_MainPanel(bpy.types.Panel):
    bl_label = "Fight Generator Pro v8.0 (Modular)"
    bl_idname = "FIGHTGEN_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Fight Gen Pro'

    def draw(self, context):
        layout = self.layout
        props = context.scene.fightgen_props
        box = layout.box()
        box.label(text="v8.0 Clean Quad Body + 3D Orbit Cam", icon='ARMATURE_DATA')
        box.operator("fightgen.setup_arena", icon='SCENE_DATA')
        box.prop(props, "fight_number")
        box.prop(props, "fight_duration")
        row = layout.row()
        row.scale_y = 1.6
        row.operator("fightgen.start_fight", icon='PLAY')
        layout.operator("fightgen.configure_mp4", icon='RENDER_ANIMATION')


classes = (
    FIGHTGEN_Properties,
    FIGHTGEN_OT_SetupArena,
    FIGHTGEN_OT_StartFight,
    FIGHTGEN_OT_ConfigureMP4,
    FIGHTGEN_PT_MainPanel,
)


def register():
    generate_fight_sfx()
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)
    bpy.types.Scene.fightgen_props = bpy.props.PointerProperty(type=FIGHTGEN_Properties)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
