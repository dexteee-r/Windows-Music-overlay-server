"""Music Overlay Server.

Serveur web local qui expose la lecture en cours de Windows sous forme
d'overlay HTML utilisable dans OBS et les autres logiciels de streaming.

Ce module est l'unique source de vérité pour le numéro de version : la GUI,
la documentation et les scripts de build le lisent ici.
"""

__version__ = "3.0.1"
__author__ = "dexteee-r"
__app_name__ = "Music Overlay Server"

__all__ = ["__app_name__", "__author__", "__version__"]
