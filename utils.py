""" Utilidades para el proyecto """
from colorama import Fore

class Color:
    """ Contiene métodos para devolver texto con color """
    @staticmethod
    def verde(string: str):
        ''' Texto verde '''
        return Fore.GREEN + string + Fore.RESET

    @staticmethod
    def rojo(string: str):
        ''' Texto rojo '''
        return Fore.RED + string + Fore.RESET

    @staticmethod
    def amarillo(string: str):
        ''' Texto amarillo '''
        return Fore.YELLOW + string + Fore.RESET
