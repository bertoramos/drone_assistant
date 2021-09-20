
import bpy

from .meshModel import MeshModel
from .pose import Pose

class DroneModel(MeshModel):

    def __init__(self, mesh_id: str, pose: Pose, collider_id: str, note_id: str):
        super().__init__(mesh_id, pose, collider_id, note_id)
