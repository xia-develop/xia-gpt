from xia_gpt.models import GptKnowledge
from xia_pattern import PythonPattern


class GptPythonPattern(PythonPattern):
    _knowledge_class = GptKnowledge
