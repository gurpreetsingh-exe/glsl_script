import bpy

class GLSL_NODE_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    debug_extras: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "debug_extras", text="Debug Extras")

register, unregister = bpy.utils.register_classes_factory([GLSL_NODE_AddonPreferences])
