from maa.context import Context
from maa.define import OCRResult, RectType
import numpy
import sys

def getText(
    context: Context,
    image: numpy.ndarray,
    roi: RectType,
    match: str
) -> str | None:
    recognition_result = context.run_recognition(
        "GenericOCR",
        image,
        pipeline_override={
            "GenericOCR": {
                "recognition": "OCR",
                "roi": roi,
                "expected": match,
            }
        },
    )
    if recognition_result and recognition_result.hit and recognition_result.filtered_results and isinstance(recognition_result.filtered_results[0], OCRResult):
        return recognition_result.filtered_results[0].text
    else:
        return None

def templateMatch(
    context: Context,
    image: numpy.ndarray,
    roi: RectType,
    template_name: str
) -> bool:
    recognition_result = context.run_recognition(
        "TemplateMatch",
        image,
        pipeline_override={
            "TemplateMatch": {
                "recognition": "TemplateMatch",
                "roi": roi,
                "template_name": template_name,
            }
        },
    )
    if recognition_result and recognition_result.hit:
        return True
    else:
        return False

class Logger:
    @staticmethod
    def debug(message: str):
        sys.stderr.write(f"debug: {message}\n")

    @staticmethod
    def info(message: str):
        sys.stderr.write(f"info: {message}\n")

    @staticmethod
    def warn(message: str):
        sys.stderr.write(f"warn: {message}\n")

    @staticmethod
    def error(message: str):
        sys.stderr.write(f"error: {message}\n")

logger = Logger()