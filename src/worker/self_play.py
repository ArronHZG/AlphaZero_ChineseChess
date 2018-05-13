import os
import gc
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone, timedelta
from logging import getLogger
from multiprocessing import Manager
from time import time, sleep
from collections import defaultdict
from random import random
from threading import Thread

import src.environment.light.static_env as senv
from src.agent.model import CChessModel
from src.agent.mcts import CChessPlayer, VisitState
from src.config import Config
from src.environment.light.lookup_tables import ActionLabelsRed, flip_policy
from src.utils.data_helper import get_game_data_filenames, write_game_data_to_file
from src.utils.model_helper import load_best_model_weight, save_as_best_model
from src.utils.tf_helper import set_session_config

logger = getLogger(__name__)

def load_model(config):
    model = CChessModel(config)
    if config.opts.new or not load_best_model_weight(model):
        model.build()
        save_as_best_model(model)
    return model

def start(config: Config):
    set_session_config(per_process_gpu_memory_fraction=1, allow_growth=True, device_list=config.opts.device_list)
    current_model = load_model(config)
    m = Manager()
    cur_pipes = m.list([current_model.get_pipes() for _ in range(config.play.max_processes)])
    # play_worker = SelfPlayWorker(config, cur_pipes, 0)
    # play_worker.start()
    with ProcessPoolExecutor(max_workers=config.play.max_processes) as executor:
        futures = []
        for i in range(config.play.max_processes):
            play_worker = SelfPlayWorker(config, cur_pipes, i)
            logger.debug("Initialize selfplay worker")
            futures.append(executor.submit(play_worker.start))

class SelfPlayWorker:
    def __init__(self, config: Config, pipes=None, pid=None):
        self.config = config
        self.player = None
        self.cur_pipes = pipes
        self.id = pid
        self.buffer = []
        self.pid = os.getpid()

    def start(self):
        self.pid = os.getpid()
        logger.debug(f"Selfplay#Start Process index = {self.id}, pid = {self.pid}")

        idx = 1
        self.buffer = []
        search_tree = defaultdict(VisitState)

        while True:
            start_time = time()
            search_tree = defaultdict(VisitState)
            value, turns, state, store = self.start_game(idx, search_tree)
            end_time = time()
            logger.debug(f"Process {self.pid}-{self.id} play game {idx} time={(end_time - start_time):.1f} sec, "
                         f"turn={turns / 2}, winner = {value:.2f} (1 = red, -1 = black, 0 draw)")
            if turns <= 10:
                senv.render(state)
            if store:
                idx += 1
            sleep(random())

    def start_game(self, idx, search_tree):
        pipes = self.cur_pipes.pop()

        if not self.config.play.share_mtcs_info_in_self_play or \
            idx % self.config.play.reset_mtcs_info_per_game == 0:
            search_tree = defaultdict(VisitState)

        if random() > self.config.play.enable_resign_rate:
            enable_resign = True
        else:
            enable_resign = False

        self.player = CChessPlayer(self.config, search_tree=search_tree, pipes=pipes, enable_resign=enable_resign, debugging=False)

        state = senv.INIT_STATE
        history = [state]
        # policys = [] 
        value = 0
        turns = 0       # even == red; odd == black
        game_over = False
        final_move = None
        no_eat_count = 0
        check = False

        while not game_over:
            no_act = None
            if not check and state in history[:-1]:
                no_act = []
                free_move = defaultdict(int)
                for i in range(len(history) - 1):
                    if history[i] == state:
                        # 如果走了下一步是将军或捉：禁止走那步
                        if senv.will_check_or_catch(state, history[i+1]):
                            no_act.append(history[i + 1])
                        # 否则当作闲着处理
                        else:
                            free_move[state] += 1
                            if free_move[state] >= 2:
                                # 作和棋处理
                                game_over = True
                                value = 0
                                logger.info("闲着循环三次，作和棋处理")
                                break
            if game_over:
                break
            start_time = time()
            action, policy = self.player.action(state, turns, no_act)
            end_time = time()
            if action is None:
                logger.debug(f"{turns % 2} (0 = red; 1 = black) has resigned!")
                value = -1
                break
            if self.config.opts.log_move:
                logger.info(f"Process{self.pid} Playing: {turns % 2}, action: {action}, time: {(end_time - start_time):.1f}s")
            # logger.info(f"Process{self.pid} Playing: {turns % 2}, action: {action}, time: {(end_time - start_time):.1f}s")
            # for move, action_state in self.player.search_results.items():
            #     if action_state[0] >= 20:
            #         logger.info(f"move: {move}, prob: {action_state[0]}, Q_value: {action_state[1]:.2f}, Prior: {action_state[2]:.3f}")
            # self.player.search_results = {}
            history.append(action)
            # policys.append(policy)
            try:
                state, no_eat = senv.new_step(state, action)
            except Exception as e:
                logger.error(f"{e}, no_act = {no_act}, policy = {policy}")
                game_over = True
                value = 0
                break
            turns += 1
            if no_eat:
                no_eat_count += 1
            else:
                no_eat_count = 0
            history.append(state)

            if no_eat_count >= 120 or turns / 2 >= self.config.play.max_game_length:
                game_over = True
                value = 0
            else:
                game_over, value, final_move, check = senv.done(state, need_check=True)
                if not game_over:
                    if not senv.has_attack_chessman(state):
                        logger.info(f"双方无进攻子力，作和。state = {state}")
                        game_over = True
                        value = 0

        if final_move:
            # policy = self.build_policy(final_move, False)
            history.append(final_move)
            # policys.append(policy)
            state = senv.step(state, final_move)
            turns += 1
            value = -value
            history.append(state)

        self.player.close()
        del search_tree
        del self.player
        gc.collect()
        if turns % 2 == 1:  # balck turn
            value = -value

        v = value
        if turns < 10:
            if random() > 0.9:
                store = True
            else:
                store = False
        else:
            store = True

        if store:
            data = [history[0]]
            for i in range(turns):
                k = i * 2
                data.append([history[k + 1], value])
                value = -value
            self.save_play_data(idx, data)

        self.cur_pipes.append(pipes)
        self.remove_play_data()
        return v, turns, state, store

    def save_play_data(self, idx, data):
        self.buffer += data

        if not idx % self.config.play_data.nb_game_in_file == 0:
            return

        rc = self.config.resource
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
        game_id = bj_dt.strftime("%Y%m%d-%H%M%S.%f")
        filename = rc.play_data_filename_tmpl % game_id
        path = os.path.join(rc.play_data_dir, filename)
        logger.info(f"Process {self.pid} save play data to {path}")
        write_game_data_to_file(path, self.buffer)
        self.buffer = []


    def remove_play_data(self):
        files = get_game_data_filenames(self.config.resource)
        if len(files) < self.config.play_data.max_file_num:
            return
        try:
            for i in range(len(files) - self.config.play_data.max_file_num):
                os.remove(files[i])
        except:
            pass

    def build_policy(self, action, flip):
        labels_n = len(ActionLabelsRed)
        move_lookup = {move: i for move, i in zip(ActionLabelsRed, range(labels_n))}
        policy = np.zeros(labels_n)

        policy[move_lookup[action]] = 1

        if flip:
            policy = flip_policy(policy)
        return list(policy)

