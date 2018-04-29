import tensorflow as tf
import keras.backend as K
def set_session_config(per_process_gpu_memory_fraction=None, allow_growth=None, device_list='0'):
    config = tf.ConfigProto(
        gpu_options=tf.GPUOptions(
            per_process_gpu_memory_fraction=per_process_gpu_memory_fraction,
            allow_growth=allow_growth,
            visible_device_list=device_list
        )
    )
    sess = tf.Session(config=config)
    K.set_session(sess)