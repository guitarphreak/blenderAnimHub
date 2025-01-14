import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel

bl_info = { 
    "name": "Animation Tools",
    "author": "Andres Quiroz",
    "version": (1, 0, 0),
    "blender": (4, 2, 3),
    "location": "View3D > Toolshelf",
    "description": "Compilation of animation related tools.",
    "warning": "",
    "wiki_url": "",
    "category": "Animation Tools",
}

class VIEW3D_PT_AnimationTools(Panel):
    bl_label = "Animation Tools"
    bl_idname = "VIEW3D_PT_AnimationTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation Tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return (context.mode == "POSE" and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Armature Picker TODO", icon="OUTLINER_OB_ARMATURE")


class VIEW3D_PT_SelectionTools(Panel):
    bl_label = "Selection Sets"
    bl_idname = "VIEW3D_PT_SelectionTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "VIEW3D_PT_AnimationTools"
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        arm = context.object
        
        row = layout.row(align=True)
        row.prop(scene, "input")
        row.operator("object.addselectionset", icon="ADD")
        row.operator("object.removeselectionset", icon="REMOVE")

        row = layout.row()
        row.template_list("POSE_UL_selection_set", "", arm, "selection_sets", arm,  "active_selection_set")


class POSE_OT_AddSelectionSet(Operator):
    bl_idname = "object.addselectionset"
    bl_label = ""
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.mode == "POSE" and context.object.type == 'ARMATURE')

    def execute(self, context):
        arm = context.object
        sel_sets = arm.selection_sets
        
        new_set_name = "NewSelectionSet" if not context.scene.input else context.scene.input

        new_sel_set = sel_sets.add()
        new_sel_set.name = _uniqify(new_set_name, sel_sets.keys())

        act_sel_set = sel_sets[new_sel_set.name]
        
        if context.selected_pose_bones:
            for bone in context.selected_pose_bones:
                if bone.name not in act_sel_set.bone_ids:
                    bone_id = act_sel_set.bone_ids.add()
                    bone_id.name = bone.name

        context.scene.input = ""

        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()

        return {"FINISHED"}

class POSE_OT_RemoveSelectionSet(Operator):
    bl_idname = "object.removeselectionset"
    bl_label = ""
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.mode == "POSE" and context.object.type == 'ARMATURE')
    
    def execute(self, context):
        arm = context.object
        sel_sets = arm.selection_sets
        del_set_name = context.scene.input

        if del_set_name:
            sel_sets.remove(sel_sets.find(del_set_name))
            self.report({'INFO'}, f"Removed selection set: {del_set_name}")

            context.scene.input = ""
        
        else:
            arm.selection_sets.remove(arm.active_selection_set)

            if len(arm.selection_sets) > 0:
                arm.active_selection_set = len(arm.selection_sets) - 1

        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()
                
        return {"FINISHED"}

def _uniqify(name, other_names):
    # :arg name: The name to make unique.
    # :type name: str
    # :arg other_names: The name to make unique.
    # :type other_names: str
    # :return: Return a unique name with ``.xxx`` suffix if necessary.
    # :rtype: str
    #
    # Example usage:
    #
    # >>> _uniqify('hey', ['there'])
    # 'hey'
    # >>> _uniqify('hey', ['hey.001', 'hey.005'])
    # 'hey'
    # >>> _uniqify('hey', ['hey', 'hey.001', 'hey.005'])
    # 'hey.002'
    # >>> _uniqify('hey', ['hey', 'hey.005', 'hey.001'])
    # 'hey.002'
    # >>> _uniqify('hey', ['hey', 'hey.005', 'hey.001', 'hey.left'])
    # 'hey.002'
    # >>> _uniqify('hey', ['hey', 'hey.001', 'hey.002'])
    # 'hey.003'
    #
    # It also works with a dict_keys object:
    # >>> _uniqify('hey', {'hey': 1, 'hey.005': 1, 'hey.001': 1}.keys())
    # 'hey.002'

    if name not in other_names:
        return name

    # Construct the list of numbers already in use.
    offset = len(name) + 1
    others = (n[offset:] for n in other_names
              if n.startswith(name + '.'))
    numbers = sorted(int(suffix) for suffix in others
                     if suffix.isdigit())

    # Find the first unused number.
    min_index = 1
    for num in numbers:
        if min_index < num:
            break
        min_index = num + 1
    return "{:s}.{:03d}".format(name, min_index)


def register():
    bpy.utils.register_class(VIEW3D_PT_AnimationTools)
    bpy.utils.register_class(VIEW3D_PT_SelectionTools)
    bpy.utils.register_class(POSE_OT_AddSelectionSet)
    bpy.utils.register_class(POSE_OT_RemoveSelectionSet)

    bpy.types.Scene.input = StringProperty(name="", description="Name for the set to add/remove. Default NewSelectionSet")

def unregister():

    del bpy.types.Scene.input

    bpy.utils.unregister_class(VIEW3D_PT_AnimationTools)
    bpy.utils.unregister_class(VIEW3D_PT_SelectionTools)
    bpy.utils.unregister_class(POSE_OT_AddSelectionSet)
    bpy.utils.unregister_class(POSE_OT_RemoveSelectionSet)

register()
