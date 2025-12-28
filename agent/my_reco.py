from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context

from PIL import Image
import sys

@AgentServer.custom_recognition("screenshot")
class MyRecongition(CustomRecognition):
    cnt = 0
    student_names = set()
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        self.cnt += 1
        Image.fromarray(argv.image[..., ::-1]).save(f"debug/detail/{str(self.cnt).zfill(3)}.png")

        reco_detail = context.run_recognition(
            "NameOfStudent",
            argv.image,
            pipeline_override={
                "NameOfStudent": {
                    "recognition": "OCR",
                    "roi": [75, 540, 270, 45],
                    "expected": ".*",
                }
            }
        )

        if reco_detail and reco_detail.hit and reco_detail.best_result:
            name = reco_detail.best_result.text
            if name not in self.student_names:
                sys.stderr.write(f"info: [{str(self.cnt).zfill(3)}]识别到学生姓名: {name}\n")
                self.student_names.add(name)
                return CustomRecognition.AnalyzeResult(
                    box = (0, 0, 0, 0),
                    detail = {},
                )
            else:
                return CustomRecognition.AnalyzeResult(
                    box = None,
                    detail = {},
                )

        else:
            sys.stderr.write(f"warn: [{str(self.cnt).zfill(3)}]未识别到学生姓名\n")
            return CustomRecognition.AnalyzeResult(
                box = (0, 0, 0, 0),
                detail = {},
            )
