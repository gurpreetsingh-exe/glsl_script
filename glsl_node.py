import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

import os
import numpy as np
from timeit import default_timer

class ShaderNodeGLSLScript(bpy.types.ShaderNodeCustomGroup):
    bl_idname = "ShaderNodeGLSLScript"
    bl_label = "GLSL Script"

    is_init: bpy.props.BoolProperty(default=False)
    time: bpy.props.FloatProperty(default=0, precision=4)

    def update_node(self, context):
        self.update()

    resolution: bpy.props.EnumProperty(name="Resolution", items=(
        (   '128',    '128', '', 0),
        (   '256',    '256', '', 1),
        (   '512',    '512', '', 2),
        (  '1024',   '1024', '', 3),
        (  '2048',   '2048', '', 4),
        ('CUSTOM', 'Custom', '', 5),
    ), default='512', update=update_node)
    custom_res: bpy.props.IntProperty(name="Custom Resolution", default=512, update=update_node)

    vert: bpy.props.StringProperty(name="Vertex Shader", default="""in vec2 a_position;
in vec2 a_uv;

out vec2 uv;

void main() {
    uv = a_uv;
    gl_Position = vec4(a_position, 0.0, 1.0);
}""", update=update_node)

    frag: bpy.props.PointerProperty(type=bpy.types.Text, name="Shader", update=update_node)

    image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image")

    def init(self, context):
        nt_name = f".{self.bl_idname}Group"
        if bpy.data.node_groups.get(nt_name):
            self.node_tree = bpy.data.node_groups.get(nt_name).copy()
        else:
            from .utils import append_node_group

            append_node_group(nt_name, os.path.join(os.path.dirname(__file__), "assets", "node_group.blend"))
            self.node_tree = bpy.data.node_groups.get(nt_name)

        image_name = f"{hash(self)}"
        size = self.custom_res if self.resolution == 'CUSTOM' else int(self.resolution)
        if bpy.data.images.get(image_name):
            self.image = bpy.data.images.get(image_name)
        else:
            self.image = bpy.data.images.new(name=image_name, width=size, height=size, alpha=False, float_buffer=True)

        self.set_image_props(size, 'sRGB')
        self.is_init = True

    def set_image_props(self, size, color_space):
        self.image.colorspace_settings.name = color_space
        self.image.use_generated_float = True
        self.image.generated_width = size
        self.image.generated_height = size

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "frag", text='')
        op = row.operator("glslnode.update", text='', icon='FILE_REFRESH')
        op.node_name = self.name

        if context.preferences.addons[__package__].preferences.debug_extras:
            box = layout.box()
            box.active = False
            box.prop(self, "time")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "resolution")
        if self.resolution == 'CUSTOM':
            layout.prop(self, "custom_res")

    def update(self):
        if not self.is_init:
            return

        if not self.frag:
            return
        start = default_timer()

        size = self.custom_res if self.resolution == 'CUSTOM' else int(self.resolution)
        self.set_image_props(size, 'sRGB')

        offscreen = gpu.types.GPUOffScreen(size, size)
        with offscreen.bind():
            shader = gpu.types.GPUShader(self.vert, self.frag.as_string())
            batch = batch_for_shader(shader, 'TRI_FAN', {
                'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1)),
                'a_uv': ((0, 0), (1, 0), (1, 1), (0, 1)),
            })
            shader.bind()
            batch.draw(shader)

            pixel_data = np.zeros((size * size * 4), dtype=np.float32)

            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, offscreen.color_texture)

            buffer = bgl.Buffer(bgl.GL_FLOAT, pixel_data.shape, pixel_data)
            bgl.glGetTexImage(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
            self.image.pixels.foreach_set(pixel_data)

        offscreen.free()
        del pixel_data
        self.node_tree.nodes['img'].image = self.image

        end = default_timer()
        self.time = (end - start) * 1000

    def free(self):
        nt = self.node_tree
        if nt.users <= 1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)

    def copy(self, node):
        print(node, " Copied")

register, unregister = bpy.utils.register_classes_factory([ShaderNodeGLSLScript])
