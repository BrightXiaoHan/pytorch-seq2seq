class DialogueConfig(object):
    """
    114移车系统配置类基类
    """
    def _get_connection(self):
        """获取配置数据库的连接
        """
        connection = None 
        return connection


    def reload(self):
        raise NotImplementedError


from .discourse import discourse_config
from .intent import intent_config
from .asr import asr_config

__all__ = ["discourse_config", "intent_config", "asr_config"]