import bpy

def append_node_group(name, path):
    with bpy.data.libraries.load(path) as (data_from, data_to):
        nt = data_from.node_groups
        data_to.node_groups.append(nt[nt.index(name)])
