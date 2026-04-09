from enum import Enum



class CriterionStageEnum(str, Enum):
    PROJECT_DOC = "projectdoc"   # проверяется только по документации
    CODEBASE = "codebase"       # проверяется только по кодовой базе
    AUTO = "auto"               # проверяется по всем: документация, кодовая база
    MANUAL = "manual"           # проверяется только в ходе ручной проверки


class CriterionStatusEnum(str, Enum):
    SUFFICIENT = "sufficient"  # полученных сведений достаточно для оценки удовлетворенности критерием
    NEEDS_CODE = "needs_code"  # нужно проверить код
    NEEDS_STUDENT = "needs_student"  # нужно запросить информацию у студента
    NEEDS_MANUAL = "needs_manual"  # нужна ручная проверка преподавателем
    NOT_APPLICABLE = "not_applicable"  # критерий не применим к проекту
