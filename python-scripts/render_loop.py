
import bpy
sc = bpy.context.scene
frames = list(range(198, 271)) + list(range(451, 721))
for f in frames:
    sc.frame_set(f)
    sc.render.filepath = r"D:\Blender_Files\Konark_Temple\frames_cine\c_%04d.png" % f
    bpy.ops.render.render(write_still=True)
    print("DONE", f, flush=True)
