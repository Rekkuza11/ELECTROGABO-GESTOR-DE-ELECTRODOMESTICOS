from abc import ABC, abstractmethod


class Usuario(ABC):

    def __init__(self, id_usuario, password):
        self.id_usuario = id_usuario
        self.password = password

    def cambiar_password(self, nueva_password):
        self.password = nueva_password

    @abstractmethod
    def mostrar(self):
        pass