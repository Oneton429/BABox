from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
from maa.define import CustomRecognitionResult

import utils

@AgentServer.custom_action("check_and_stop_student_info_task")
class CheckAndStopStudentInfoTask(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        if argv.reco_detail.all_results and isinstance(argv.reco_detail.all_results[0], CustomRecognitionResult) and \
           isinstance(argv.reco_detail.all_results[0].detail, dict) and argv.reco_detail.all_results[0].detail.get("endTask", False):
            utils.logger.info("Box识别任务完成。")
            return False

        if argv.reco_detail.box is not None:
            context.run_action(
                "NextOne",
                pipeline_override={
                    "NextOne": {
                        "action": "Click",
                        "target": [
                            argv.reco_detail.box.x,
                            argv.reco_detail.box.y,
                            argv.reco_detail.box.w,
                            argv.reco_detail.box.h
                        ]
                    }
                }
            )
            return True
        return False
