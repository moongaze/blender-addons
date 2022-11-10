# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Hotkey: 'Z'",
    "description": "Viewport Shading Menus",
    "author": "pitiwazou, meta-androcto",
    "version": (0, 1, 2),
    "blender": (3, 3, 0),
    "location": "3D View",
    "warning": "",
    "doc_url": "",
    "category": "Shading Pie"
    }

#from asyncio.base_futures import _FINISHED
import bpy
from bpy.types import (Menu,Operator)
from bpy.props import (BoolProperty, FloatProperty)
from math import radians



# Shade / Auto Smooth
class PIE_OT_ShadeAutoSmooth(Operator):
    bl_idname = "shade.autosmooth"
    bl_label = "Shade Smooth"
    bl_description = "Set smoothing properties on objects or faces"
    bl_options = {'REGISTER','UNDO'}
   
    hasSplitNormals = False # A mesh in the selection has custom normals
    onlyOne = False # The selection consists of one mesh

    autoSmoothToggle: BoolProperty(
        name="Auto Smooth",
        description="Set Auto Smooth",
        default=True
    )

    smoothAngle: FloatProperty(
        name="Auto Smooth Angle",
        description="Set Auto Smooth Angle",
        subtype= "ANGLE",
        unit="ROTATION",
        precision=3, 
        step=10,       
        default=0.523,
        min=0,
        max=3.14
    )

    # Redo Panel
    def draw(self, context):
        # Auto smooth checkbox
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self,"autoSmoothToggle")
        row.separator(factor=5)
        # Angle label
        split = layout.split(factor=0.4, align=True)
        col1 = split.column()
        col1.label(text="Angle Limit", icon='NORMALS_VERTEX_FACE')
        col2 = split.column()
        col2.enabled = self.autoSmoothToggle and not self.onlyOne
        # Angle value slider
        row1 = col2.row()        
        row1.prop(self,'smoothAngle', text ='')
        # Preset buttons
        row2 = col2.row(align=True)
        row2.operator('autosmooth.preset', text ='30°').anglePreset = radians(30)
        row2.operator('autosmooth.preset', text ='45°').anglePreset = radians(45)
        row2.operator('autosmooth.preset', text ='70°').anglePreset = radians(70)
        # Custom normals warning
        row = layout.row()
        row.separator(factor=2)
        if self.hasSplitNormals:            
            row = layout.row()        
            row.scale_y = 0.6        
            row.label(text='Angle will have no effect on meshes', icon='ERROR')
            row = layout.row()
            row.label(text='with Custom Split Normals Data.',icon='BLANK1')

    #Check and set autosmooth 
    def smoothify(self,context):
        obs = context.selected_objects

        if context.mode == 'EDIT_MESH':
            bpy.ops.mesh.faces_shade_smooth()
        if context.mode == 'OBJECT':
            bpy.ops.object.shade_smooth() 

        for ob in obs:
            if ob.type == 'MESH':    
                ob.data.use_auto_smooth = self.autoSmoothToggle
                if not ob.data.has_custom_normals: 
                    if context.scene.presetHappened == True:
                        ob.data.auto_smooth_angle = context.scene.autoSmoothAngle
                        self.smoothAngle = context.scene.autoSmoothAngle
                    else:
                        ob.data.auto_smooth_angle = self.smoothAngle                        
                else : 
                    self.hasSplitNormals = True
                    if len(obs)==1 : self.onlyOne = True

        setattr(bpy.types.Scene, "presetHappened", False)
        return {'FINISHED'}

    def execute(self, context):
        self.smoothify(context)
        return {'FINISHED'}

    # Make sure default of 30 degrees is enforced
    def invoke(self,context,event):
        self.smoothAngle = radians(30)
        self.smoothify(context)
        return {'FINISHED'}

class PIE_OT_SetASPreset(Operator):
    bl_idname = "autosmooth.preset"
    bl_label = 'SetPreset'

    anglePreset: FloatProperty(
        name="Auto Smooth Angle Preset",
        description="Set Auto Smooth Angle Preset",
        subtype= "ANGLE",
        unit="ROTATION",
        precision=3, 
        step=10,       
        default=0.523,
        min=0,
        max=3.14
    )

    def execute(self, context):  
        setattr(bpy.types.Scene, "autoSmoothAngle", self.anglePreset)
        setattr(bpy.types.Scene, "presetHappened", True)

        return {'FINISHED'}

class PIE_OT_ShowFaceOrientation(Operator):
    bl_idname = "toggle.faceorientation"
    bl_label = "Orientation Overlay"

    def execute(self, context):
        bpy.context.space_data.overlay.show_face_orientation = not bpy.context.space_data.overlay.show_face_orientation

        return {'FINISHED'}

class PIE_OT_ShowWireOverlay(Operator):
    bl_idname = "toggle.wireoverlay"
    bl_label = "Wireframe Overlay"

    def execute(self, context):
        bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes
        
        return {'FINISHED'}

# Pie Shading - Z
class PIE_MT_ShadingView(Menu):
    bl_idname = "PIE_MT_shadingview"
    bl_label = "Pie Shading"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        isMesh = False
        for ob in bpy.context.selected_objects:             
            if ob.type == "MESH":isMesh = True

        pie = layout.menu_pie()
        pie.prop(context.space_data.shading, "type", expand=True)

        if context.active_object:
            if context.mode == 'EDIT_MESH':
                #pie.operator("MESH_OT_faces_shade_smooth")
                pie.operator("shade.autosmooth")
                pie.operator("MESH_OT_faces_shade_flat")
                pie.operator("toggle.wireoverlay")                
                pie.operator("toggle.faceorientation")
            else:
                #pie.operator("OBJECT_OT_shade_smooth")
                if isMesh:
                    pie.operator("shade.autosmooth")
                    pie.operator("OBJECT_OT_shade_flat")
                else:
                    pie.separator()
                    pie.separator()
                pie.operator("toggle.wireoverlay")
                pie.operator("toggle.faceorientation")

            
    

classes = (
    PIE_MT_ShadingView,
    PIE_OT_ShadeAutoSmooth,
    PIE_OT_SetASPreset,
    PIE_OT_ShowFaceOrientation,
    PIE_OT_ShowWireOverlay
    )

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        # Shading
        km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'Z', 'PRESS')
        kmi.properties.name = "PIE_MT_shadingview"
        addon_keymaps.append((km, kmi))

    setattr(bpy.types.Scene, "autoSmoothAngle", 0.523)
    setattr(bpy.types.Scene, "presetHappened", False)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    delattr(bpy.types.Scene, "autoSmoothAngle")
    delattr(bpy.types.Scene, "presetHappened")

if __name__ == "__main__":
    register()
