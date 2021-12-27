import bpy

class GLSL_NODE_OT_update(bpy.types.Operator):
    bl_idname = "glslnode.update"
    bl_label = "Update"

    node_name: bpy.props.StringProperty(default='')

    def execute(self, context):
        nt = context.object.active_material.node_tree
        node = nt.nodes[self.node_name]
        if node.frag:
            node.update_node(context)
        else:
            self.report({'WARNING'}, "No file specified in node, nothing to compile")
        return {'FINISHED'}

register, unregister = bpy.utils.register_classes_factory([GLSL_NODE_OT_update])
