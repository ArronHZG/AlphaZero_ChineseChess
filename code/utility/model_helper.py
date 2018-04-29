import os
from logging import getLogger

logger = getLogger(__name__)


def load_best_model_weight(model):
    return model.load(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path)


def save_as_best_model(model):
    return model.save(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path)


def need_to_reload_best_model_weight(model):
    logger.debug("判断最有模型是否更新")
    digest = model.fetch_digest(model.config.resource.model_best_weight_path)
    if digest != model.digest:
        logger.debug("更新最优权重")
        return True
    else:
        logger.debug("最优权重未更新")
        return False


def load_model_weight(model, config_path, weight_path, name=None):
    if name is not None:
        logger.info(f"{name}: load model from {config_path}")
    return model.load(config_path, weight_path)


def save_as_next_generation_model(model):
    filename = model.digest + '.h5'
    weight_path = os.path.join(model.config.resource.next_generation_model_dir, filename)
    return model.save(model.config.resource.next_generation_config_path, weight_path)
