import os


class Config:
    def __init__(self, config_type='mini'):
        self.opts = Options()
        self.resource = ResourceConfig()
        if config_type == 'mini':
            import src.configs.mini as config
        elif config_type == 'normal':
            import src.configs.normal as config
        else:
            raise RuntimeError(f'未知配置:{config_type}')
        self.model = config.ModelConfig()
        self.play = config.PlayConfig()
        self.play_data = config.PlayDataConfig()
        self.trainer = config.TrainerConfig()
        self.eval = config.EvaluateConfig()


class Options:
    new = False
    light = True
    device_list = '0,1'
    bg_style = 'WOOD'
    piece_style = 'WOOD'


class ResourceConfig:
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", self._project_dir())
        self.data_dir = os.environ.get("DATA_DIR", os.path.join(self.project_dir, "data"))
        self.model_dir = os.environ.get("MODEL_DIR", os.path.join(self.data_dir, "model"))
        self.resource_dir = os.environ.get("RESOURCE_DIR", os.path.join(self.project_dir, "resource"))
        self.model_best_config_path = os.path.join(self.model_dir, "model_best_config.json")
        self.model_best_weight_path = os.path.join(self.model_dir, "model_best_weight.h5")
        self.next_generation_model_dir = os.path.join(self.model_dir, "next_generation")
        self.next_generation_config_path = os.path.join(self.next_generation_model_dir, "next_generation_config.json")
        self.next_generation_weight_path = os.path.join(self.next_generation_model_dir, "next_generation_weight.h5")
        self.play_data_dir = os.path.join(self.data_dir, "play_data")
        self.play_data_filename_tmpl = "play_%s.json"
        self.play_record_dir = os.path.join(self.data_dir, "play_record")
        self.play_record_filename_tmpl = "record_%s.qp"
        self.log_dir = os.path.join(self.project_dir, "logs")
        self.main_log_path = os.path.join(self.log_dir, "main.log")
        self.opt_log_path = os.path.join(self.log_dir, "opt.log")
        self.play_log_path = os.path.join(self.log_dir, "play.log")
        self.eval_log_path = os.path.join(self.log_dir, "eval.log")
        self.font_path = os.path.join(self.resource_dir, 'font', 'PingFang.ttc')
        self.image_path = os.path.join(self.resource_dir, 'images')

    def create_directories(self):
        dirs = [self.project_dir, self.data_dir, self.model_dir, self.play_data_dir, self.log_dir,
                self.play_record_dir, self.next_generation_model_dir]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

    @staticmethod
    def _project_dir():
        d = os.path.dirname
        return d(d(os.path.abspath(__file__)))


class PlayWithHumanConfig:
    def __init__(self):
        self.simulation_num_per_move = 800
        self.c_puct = 1
        self.search_threads = 20
        self.noise_eps = 0
        self.tau_decay_rate = 0
        self.dirichlet_alpha = 0.2

    def update_play_config(self, pc):
        pc.simulation_num_per_move = self.simulation_num_per_move
        pc.c_puct = self.c_puct
        pc.noise_eps = self.noise_eps
        pc.tau_decay_rate = self.tau_decay_rate
        pc.search_threads = self.search_threads
        pc.dirichlet_alpha = self.dirichlet_alpha


if __name__ == '__main__':
    c = Config()
    print(c.__dict__)

    # r = ResourceConfig()
    # r.create_directories()
    # c.resource = r
    import json

    myClassJson = json.dumps(c.resource.__dict__)
    print(myClassJson)
