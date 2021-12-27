# Copyright (C) 2021  Gurpreet Singh

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "GLSL Script",
    "author": "Gurpreet Singh",
    "blender": (3, 0, 0),
    "category": "Node",
    "version": (0, 0, 1),
}

import bpy

import pkgutil
import importlib
from pathlib import Path

from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory

print(__name__)

path = Path(__file__).parent

def get_modules(path):
    modules = [name for _, name, _ in pkgutil.iter_modules([path])]
    for module in modules:
        yield importlib.import_module(path.name + "." + module)

modules = get_modules(path)

def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    sn_category = [
        ShaderNodeCategory("SN_SCRIPT", "Script", items=[
            NodeItem("ShaderNodeGLSLScript"),
        ])
    ]
    register_node_categories("SN_SCRIPT", sn_category)

def unregister():
    unregister_node_categories("SN_SCRIPT")

    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
