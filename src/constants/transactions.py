import enum


class TransactionTypeEnum(enum.StrEnum):
    WELCOME_BONUS = "WELCOME_BONUS"
    REVIEW = "REVIEW"
    ADMIN_TOP_UP = "ADMIN_TOP_UP"
    DEPOSIT = "DEPOSIT"
