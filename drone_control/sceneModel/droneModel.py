
import bpy
from mathutils import Vector

from .meshModel import MeshModel
from .pose import Pose

class DroneModel(MeshModel):

    def __init__(self, mesh_id: str, pose: Pose, collider_id: str, note_id: str, address: tuple, server_address: str, server_port: int, client_address: str, client_port: int):
        super().__init__(mesh_id, pose, collider_id, note_id)
        self.__address = address
        self.__server_address = server_address
        self.__server_port = server_port
        self.__client_address = client_address
        self.__client_port = client_port
    
    def translate(self, pose: Pose):
        super().translate(pose)
        if self.meshID in bpy.data.objects:
            bpy.data.objects[self.meshID].location = pose.location
            bpy.data.objects[self.meshID].rotation_euler = pose.rotation
        else:
            import warnings
            warnings.warn(f"'{self.__meshID}' object not found in current scene", RuntimeWarning)
    
    def __get_address(self):
        return self.__address
    
    def __get_server_address(self):
        return self.__server_address
    
    def __get_server_port(self):
        return self.__server_port
    
    def __get_client_address(self):
        return self.__client_address
    
    def __get_client_port(self):
        return self.__client_port
    

    def __set_address(self, addr):
        self.__address = addr
    
    def __set_server_address(self, server_addr):
        self.__server_address = server_addr
    
    def __set_server_port(self, server_port):
        self.__server_port = server_port
    
    def __set_client_address(self, client_addr):
        self.__client_address = client_addr
    
    def __set_client_port(self, client_port):
        self.__client_port = client_port
    
    def __str__(self):
        txt = ""
        txt += f"Name           {self.meshID           }\n"
        txt += f"Pose           {self.pose             }\n"
        txt += f"Beacon address {self.__address        }\n"
        txt += f"Server address {self.__server_address }\n"
        txt += f"Server port    {self.__server_port    }\n"
        txt += f"Client address {self.__client_address }\n"
        txt += f"Client port    {self.__client_port    }\n"
        return txt
    
    address = property(fget=__get_address, fset=__set_address)
    serverAddress = property(fget=__get_server_address, fset=__set_server_address)
    serverPort = property(fget=__get_server_port, fset=__set_server_port)
    clientAddress = property(fget=__get_client_address, fset=__set_client_address)
    clientPort = property(fget=__get_client_port, fset=__set_client_port)
