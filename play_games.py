import os
import sys
import multiprocessing as mp

from src.utils.logger import setup_logger
from src.config import Config, PlayWithHumanConfig
from src.human import play

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)


def setup_parameters(config):
    num_cores = mp.cpu_count()
    search_threads = 10 if num_cores < 10 else 20
    print(f"search_threads = {search_threads}")
    config.play.search_threads = search_threads


if __name__ == "__main__":
    mp.freeze_support()
    sys.setrecursionlimit(10000)
    config_type = 'distribute'

    config = Config(config_type=config_type)
    config.opts.device_list = '0'
    config.resource.create_directories()
    setup_logger(config.resource.play_log_path)
    config.opts.new = False
    config.opts.light = False
    pwhc = PlayWithHumanConfig()
    pwhc.update_play_config(config.play)
    config.opts.bg_style = 'WOOD'
    setup_parameters(config)
    config.play.simulation_num_per_move = 10
    play.start(config, human_move_first=True)
    input('按任意键退出...')
