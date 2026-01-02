from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

import reco_get_student_info
from utils import logger

@AgentServer.custom_action("clear_student_info_cache")
class ClearStudentInfoCache(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        try:
            reco_get_student_info.cnt = 0
            reco_get_student_info.student_info.clear()
        except Exception as e:
            logger.error(f"Box缓存清除失败: {e}.")
            return False
        else:
            return True
