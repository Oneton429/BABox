from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

import json
import os
import reco_get_student_info
import utils

@AgentServer.custom_action("save_and_stop_student_info_task")
class SaveAndStopStudentInfoTask(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        try:
            with open("box.json", "w", encoding="UTF-8") as f:
                json.dump(reco_get_student_info.student_info, f, ensure_ascii=False, indent=2)
            utils.logger.info("学生信息已保存至 box.json 文件。")
        except Exception as e:
            utils.logger.error(f"学生信息任务停止失败: {e}.")
        os.startfile("box.json")
        context.run_action(
            "Quit",
            pipeline_override={
                "Quit": {
                    "action": "StopTask"
                }
            }
        )
        return True
