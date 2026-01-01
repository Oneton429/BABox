from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

import my_reco
from utils import logger

@AgentServer.custom_action("clear_agent_cache")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            my_reco.cnt = 0
            my_reco.student_names.clear()
        except Exception as e:
            logger.error(f"清除缓存失败: {e}.")
            return False
        else:
            return True
