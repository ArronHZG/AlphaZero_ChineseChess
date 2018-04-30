import os
import json
from glob import glob
from logging import getLogger

from src.config import ResourceConfig

logger = getLogger(__name__)

def get_game_data_filenames(rc: ResourceConfig):
    pattern = os.path.join(rc.play_data_dir, rc.play_data_filename_tmpl % "*")
    files = list(sorted(glob(pattern)))
    return files

def write_game_data_to_file(path, data):
    with open(path, "wt") as f:
        json.dump(data, f)


def read_game_data_from_file(path):
    with open(path, "rt") as f:
        return json.load(f)


if __name__=='__main__':
    rc=ResourceConfig()
    print(get_game_data_filenames(rc))