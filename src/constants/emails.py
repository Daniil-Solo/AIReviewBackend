from enum import StrEnum


class EmailSenderTypeEnum(StrEnum):
    MAILEROO = "MAILEROO"
    SMTP = "SMTP"
    DISABLE = "DISABLE"
