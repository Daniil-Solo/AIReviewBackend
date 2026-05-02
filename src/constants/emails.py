import enum


class EmailSenderTypeEnum(str, enum.Enum):
    MAILEROO = "MAILEROO"
    SMTP = "SMTP"
    DISABLE = "DISABLE"
