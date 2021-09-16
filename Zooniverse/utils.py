#Utils
from panoptes_client import Panoptes, Project
import tokens

def connect():
    Panoptes.connect(username=tokens.get_username(), password=tokens.get_password())
    everglades_watch = Project.find(10951)
    return everglades_watch