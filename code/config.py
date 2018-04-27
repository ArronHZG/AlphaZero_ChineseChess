import os
# import getpass  # 获取用户名


class Config:
    def __init(self, config_type='mini'):
        self.opts = Options()
        self.resource = Resource()
        if config_type=='mini':
            import code.configs.mini as config
        elif config_type =='normal':
            import code.configs.normal as config
        else:
            raise RuntimeError(f'未知配置:{config_type}')
        self.model=config.ModelConfig()
        self.play=config.PlayConfig()
        self.play_data=config.PlayDataConfig()
        self.trainer=config.TrainerConfig()
        self.eval=config.EvaluateConfig()



class Options:
    pass


class Resource:
    def __init__(self):
        # self.project_dir=self._project_dir()
        self.project_dir = os.environ.get("PROJECT_DIR", self._project_dir())
        self.data_dir = os.environ.get("DATA_DIR", self._data_dir(self))

    @staticmethod
    def _project_dir():
        d = os.path.dirname
        return d(d(os.path.abspath(__file__)))

    @staticmethod
    def _data_dir(cls):
        return os.path.join(cls._project_dir(), "data")


if __name__=='__main__':
    c=Config()
    r=Resource()
    print(r.project_dir)
    print(r.data_dir)