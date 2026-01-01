from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context

import json
import numpy
import utils

cnt: int = 0
student_names: set[str] = set()


@AgentServer.custom_recognition("screenshot")
class MyRecongition(CustomRecognition):

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # Image.fromarray(argv.image[..., ::-1]).save(f"debug/detail/{str(self.cnt).zfill(3)}.png")
        name = utils.getText(
            context, argv.image, roi=[106, 820, 290, 60], match=r"[\s\S]*"
        )
        if name is not None:
            if name not in student_names:
                utils.logger.info(f"[{str(cnt).zfill(3)}]识别到学生姓名: {name}")
                student_names.add(name)
                utils.logger.info(
                    json.dumps(self.process(context, argv.image), ensure_ascii=False)
                )
                return CustomRecognition.AnalyzeResult(
                    box=(0, 0, 0, 0),
                    detail={},
                )
            else:
                return CustomRecognition.AnalyzeResult(
                    box=None,
                    detail={},
                )
        else:
            utils.logger.warn(f"[{str(cnt).zfill(3)}]未识别到学生姓名")
            return CustomRecognition.AnalyzeResult(
                box=(0, 0, 0, 0),
                detail={},
            )

    def process(self, context: Context, image: numpy.ndarray) -> dict:
        level = None
        if s := utils.getText(
            context, image, roi=[50, 880, 75, 35], match=r"[Ll][Vv]\.\d+"
        ):
            level = int(s[3:])
        tier = self.getStudentStars(context, image)
        relationship = None
        if s := utils.getText(context, image, roi=[60, 825, 50, 50], match=r"\d+"):
            relationship = int(s)
        ex_level = None
        if s := utils.getText(
            context, image, roi=[1025, 605, 120, 30], match=r"(MAX)||[Ll][Vv]\.\d+"
        ):
            ex_level = 5 if s == "MAX" else int(s[3:])
        ns_level = None
        if s := utils.getText(
            context, image, roi=[1190, 605, 120, 30], match=r"(MAX)||[Ll][Vv]\.\d+"
        ):
            ns_level = 10 if s == "MAX" else int(s[3:])

        ps_level = None
        if utils.templateMatch(
            context, image, roi=[1390, 510, 55, 55], template_name="Locked.png"
        ):
            ps_level = 0
        elif s := utils.getText(
            context, image, roi=[1350, 605, 120, 30], match=r"(MAX)||[Ll][Vv]\.\d+"
        ):
            ps_level = 10 if s == "MAX" else int(s[3:])

        ss_level = None
        if utils.templateMatch(
            context, image, roi=[1550, 510, 55, 55], template_name="Locked.png"
        ):
            ss_level = 0
        elif s := utils.getText(
            context, image, roi=[1510, 605, 120, 30], match=r"(MAX)||[Ll][Vv]\.\d+"
        ):
            ss_level = 10 if s == "MAX" else int(s[3:])

        equip1_level = 0
        if s := utils.getText(context, image, roi=[1068, 838, 31, 26], match=r"\d+"):
            fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
            equip1_level = int(fixed)
        equip1_tier = 0
        if s := utils.getText(context, image, roi=[1025, 923, 30, 25], match=r"T\d+"):
            equip1_tier = int(s[1:])

        equip2_level = 0
        if s := utils.getText(context, image, roi=[1208, 838, 31, 26], match=r"\d+"):
            fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
            equip2_level = int(fixed)
        equip2_tier = 0
        if s := utils.getText(context, image, roi=[1165, 923, 30, 25], match=r"T\d+"):
            equip2_tier = int(s[1:])

        equip3_level = 0
        if s := utils.getText(context, image, roi=[1347, 838, 31, 26], match=r"\d+"):
            fixed = "".join({"O": "0", "o": "0", "A": "4"}.get(ch, ch) for ch in s if ch in "0123456789OAoA")
            equip3_level = int(fixed)
        equip3_tier = 0
        if s := utils.getText(context, image, roi=[1305, 923, 30, 25], match=r"T\d+"):
            equip3_tier = int(s[1:])

        equip_love_tier = 0
        if s := utils.getText(context, image, roi=[1445, 923, 30, 25], match=r"T\d+"):
            equip_love_tier = int(s[1:])

        weapon_level = 0
        if s := utils.getText(
            context, image, roi=[1165, 680, 91, 35], match=r"[Ll][Vv]\.\d+"
        ):
            weapon_level = int(s[3:])
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
            "equip": {
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
                "love": {
                    "tier": equip_love_tier,
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