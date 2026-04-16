import enum


class TransactionTypeEnum(enum.StrEnum):
    WELCOME_BONUS = "WELCOME_BONUS"
    ADMIN_TOP_UP = "ADMIN_TOP_UP"
    LLM_CALL = "LLM_CALL"
