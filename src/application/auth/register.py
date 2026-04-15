from dependency_injector.wiring import Provide, inject

from src.application.exceptions import ApplicationError, ConflictError, EntityNotFoundError, InvalidCredentialsError
from src.constants.transactions import TransactionTypeEnum
from src.di.container import Container
from src.dto.auth import TokenDTO
from src.dto.auth.register import (
    CodeInfoDTO,
    EmailConfirmationRequestDTO,
    EmailRegistrationRequestDTO,
)
from src.dto.common import SuccessOperationDTO
from src.dto.emails.emails import EmailMessageDTO
from src.dto.transactions.transactions import TransactionCreateDTO
from src.infrastructure.auth import create_access_token, hash_password
from src.infrastructure.auth.code import generate_code
from src.infrastructure.dao.registrations.interface import RegistrationsFlow
from src.infrastructure.email_sender.interface import EmailSenderInterface
from src.infrastructure.email_templater.interface import EmailTemplaterInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.rate_limiter.rate_limiter import RateLimiter
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import settings


logger = get_logger()


@inject
async def start_registration(
    data: EmailRegistrationRequestDTO,
    email_sender: EmailSenderInterface = Provide[Container.email_sender],
    email_templater: EmailTemplaterInterface = Provide[Container.email_templater],
    resend_code_rate_limiter: RateLimiter = Provide[Container.resend_code_rate_limiter],
    registration_flow: RegistrationsFlow = Provide[Container.registrations_flow],
    uow: UnitOfWork = Provide[Container.uow],
) -> SuccessOperationDTO:
    await resend_code_rate_limiter.check_limit(data.email)
    async with uow.connection():
        try:
            await uow.users.get_by_email(data.email)
            return SuccessOperationDTO(message="Данный email уже зарегистрирован на платформе")
        except EntityNotFoundError:
            pass

    code = generate_code()
    hashed_password = hash_password(data.password)
    data = CodeInfoDTO(email=data.email, hashed_password=hashed_password, code=code, fullname=data.fullname)
    await registration_flow.create(data)

    subject, plain, html = email_templater.render(
        template="register_confirm", code=code, platform_name=settings.PLATFORM_NAME
    )
    message = EmailMessageDTO(to=[data.email], subject=subject, html=html, plain=plain)
    try:
        await email_sender.send(message)
    except Exception:
        logger.exception("failed_to_send_email", email=data.email, type="start_registration")
        raise ApplicationError(message="Не удалось отправить письмо", code="email_send_failed")

    return SuccessOperationDTO(message="Письмо с кодом успешно отправлено")


@inject
async def confirm_registration(
    data: EmailConfirmationRequestDTO,
    resend_code_rate_limiter: RateLimiter = Provide[Container.resend_code_rate_limiter],
    registration_flow: RegistrationsFlow = Provide[Container.registrations_flow],
    uow: UnitOfWork = Provide[Container.uow],
) -> TokenDTO:
    code_info = await registration_flow.get(data.email)

    if code_info is None:
        raise ApplicationError(
            message="Код не существует или время его жизни истекло", code="expired_or_non_existing_code"
        )

    if code_info.attempts_count >= settings.auth.MAX_CONFIRM_COUNT:
        await registration_flow.delete(data.email)
        raise ApplicationError(
            message="Превышено максимальное количество попыток для подтерждения почты", code="attempts_exceeded"
        )

    if code_info.code != data.code:
        await registration_flow.update_attempts(data.email, code_info.attempts_count + 1)
        raise InvalidCredentialsError(message="Неверный код", code="invalid_code")

    async with uow.connection():
        try:
            await uow.users.get_by_email(data.email)
            raise ConflictError(message="Пользователь уже существует", code="user_exists")
        except EntityNotFoundError:
            pass

        user = await uow.users.create(
            email=data.email,
            fullname=code_info.fullname,
            hashed_password=code_info.hashed_password,
            is_admin=False,
            is_verified=True,
        )

        welcome_bonus = TransactionCreateDTO(
            user_id=user.id,
            amount=100.0,
            type=TransactionTypeEnum.WELCOME_BONUS.value,
            metadata={"source": "registration"},
        )
        await uow.transactions.create(welcome_bonus)
    await registration_flow.delete(data.email)
    await resend_code_rate_limiter.reset(data.email)
    access_token = create_access_token(user.as_short())
    return TokenDTO(access_token=access_token)
