from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
from typing import Dict, Union

import json
import numpy
import utils

cnt: int = 0
student_info: Dict[str, Dict[str, Union[int, Dict[str, int], Dict[str, Dict[str, int]], None]]] = {}

@AgentServer.custom_recognition("get_student_info")
class StudentInfo(CustomRecognition):

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        name = utils.getText(
            context, argv.image, roi=[106, 820, 290, 60], match=r"[\s\S]*"
        )
        if name is not None:
            if name not in student_info.keys():
                global cnt
                cnt += 1
                utils.logger.info(f"[{str(cnt).zfill(3)}]识别到学生姓名: {name}")
                student_info[name] = self.process(context, argv.image)
                utils.logger.debug(
                    json.dumps(student_info[name], ensure_ascii=False)
                )
                return CustomRecognition.AnalyzeResult(
                    box=(1850, 540, 50, 70),
                    detail={},
                )
            else:
                return CustomRecognition.AnalyzeResult(
                    box=(1850, 540, 50, 70),
                    detail={
                        "endTask": True
                    },
                )
        else:
            utils.logger.warn(f"[{str(cnt).zfill(3)}]未识别到学生姓名")
            return CustomRecognition.AnalyzeResult(
                box=(1850, 540, 50, 70),
                detail={},
            )

    def process(self, context: Context, image: numpy.ndarray) -> dict:
        level = None
        for _ in range(3):
            if s := utils.getText(
                context, image, roi=[50, 880, 87, 35], match=r"([Ll][Vv]\.\d+)||(等级\d+)"
            ):
                level = int(s[3:]) if s.lower().startswith("lv.") else int(s[2:])
                break
        tier = self.getStudentStars(context, image)
        relationship = None
        for _ in range(3):
            if s := utils.getText(context, image, roi=[69, 839, 30, 25], match=r"\d+"):
                relationship = int(s)
                break

        ex_level = None
        for _ in range(3):
            if s := utils.getText(
                context, image, roi=[1025, 605, 120, 30], match=r"(MAX)||(最大值)||([Ll][Vv]\.\d+)||(等级\d+)"
            ):
                ex_level = 5 if (s == "MAX" or s == "最大值") else (int(s[3:]) if s.lower().startswith("lv.") else int(s[2:]))
                break
        ns_level = None
        for _ in range(3):
            if s := utils.getText(
                context, image, roi=[1190, 605, 120, 30], match=r"(MAX)||(最大值)||([Ll][Vv]\.\d+)||(等级\d+)"
            ):
                ns_level = 10 if (s == "MAX" or s == "最大值") else (int(s[3:]) if s.lower().startswith("lv.") else int(s[2:]))
                break

        ps_level = None
        for _ in range(3):
            if utils.templateMatch(
                context, image, roi=[1390, 510, 55, 55], template_name="Locked.png"
            ):
                ps_level = 0
                break
            elif s := utils.getText(
                context, image, roi=[1350, 605, 120, 30], match=r"(MAX)||(最大值)||([Ll][Vv]\.\d+)||(等级\d+)"
            ):
                ps_level = 10 if (s == "MAX" or s == "最大值") else (int(s[3:]) if s.lower().startswith("lv.") else int(s[2:]))
                break

        ss_level = None
        for _ in range(3):
            if utils.templateMatch(
                context, image, roi=[1550, 510, 55, 55], template_name="Locked.png"
            ):
                ss_level = 0
                break
            elif s := utils.getText(
                context, image, roi=[1510, 605, 120, 30], match=r"(MAX)||(最大值)||([Ll][Vv]\.\d+)||(等级\d+)"
            ):
                ss_level = 10 if (s == "MAX" or s == "最大值") else (int(s[3:]) if s.lower().startswith("lv.") else int(s[2:]))
                break

        equip1_level = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1068, 838, 41, 26], match=r"\d+"):
                # utils.logger.info(f"Raw equip1 level text: {s}")
                fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
                equip1_level = int(fixed)
                break
        equip1_tier = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1025, 923, 30, 25], match=r"T\d+"):
                equip1_tier = int(s[1:])
                break

        equip2_level = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1208, 838, 41, 26], match=r"\d+"):
                # utils.logger.info(f"Raw equip2 level text: {s}")
                fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
                equip2_level = int(fixed)
                break
        equip2_tier = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1165, 923, 30, 25], match=r"T\d+"):
                equip2_tier = int(s[1:])
                break

        equip3_level = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1347, 838, 41, 26], match=r"\d+"):
                # utils.logger.info(f"Raw equip3 level text: {s}")
                fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
                equip3_level = int(fixed)
                break
        equip3_tier = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1305, 923, 30, 25], match=r"T\d+"):
                equip3_tier = int(s[1:])
                break

        equip_gear_tier = 0
        for _ in range(3):
            if s := utils.getText(context, image, roi=[1445, 923, 30, 25], match=r"T\d+"):
                equip_gear_tier = int(s[1:])
                break

        weapon_level = 0
        for _ in range(3):
            if s := utils.getText(
                context, image, roi=[1165, 680, 91, 34], match=r"[Ll][Vv]\.\d+||(等级\d+)"
            ):
                weapon_level = int(s[3:]) if s.lower().startswith("lv.") else int(s[2:])
                break
        weapon_tier = self.getWeaponStars(context, image)

        return {
            "level": level,
            "tier": tier,
            "relationship": relationship,
            "skill": {
                "ex": ex_level,
                "ns": ns_level,
                "ps": ps_level,
                "ss": ss_level,
            },
            "weapon": {
                "level": weapon_level,
                "tier": weapon_tier,
            },
            "equipment": {
                "1": {
                    "level": equip1_level,
                    "tier": equip1_tier,
                },
                "2": {
                    "level": equip2_level,
                    "tier": equip2_tier,
                },
                "3": {
                    "level": equip3_level,
                    "tier": equip3_tier,
                },
                "gear": {
                    "tier": equip_gear_tier,
                },
            },
        }

    def getStudentStars(
        self,
        context: Context,
        image: numpy.ndarray,
    ) -> int:
        stars = 0
        for i in range(5):
            result = context.run_recognition(
                "ColorMatch",
                image,
                pipeline_override={
                    "ColorMatch": {
                        "recognition": "ColorMatch",
                        "roi": [485 - i * 20, 855, 12, 12],
                        "lower": [245, 225, 107],
                        "upper": [255, 245, 127]
                    }
                },
            )
            if result and result.hit:
                stars += 1
        return stars

    def getWeaponStars(
        self,
        context: Context,
        image: numpy.ndarray,
    ) -> int:
        stars = 0
        for i in range(5):
            result = context.run_recognition(
                "ColorMatch",
                image,
                pipeline_override={
                    "ColorMatch": {
                        "recognition": "ColorMatch",
                        "roi": [1615 - i * 20,780,10,10],
                        "lower": [86, 219, 243],
                        "upper": [106, 239, 255]
                    }
                },
            )
            if result and result.hit:
                stars += 1
        return stars