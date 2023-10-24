import fastapi as fa

from core.enums import ResponseDetailEnum


class BadRequestException(fa.HTTPException):
    def __init__(self, detail):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UnauthorizedException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized if detail is None else detail,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidCredentialsException(fa.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseDetailEnum.invalid_credentials,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UserAlreadyExistsException(fa.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseDetailEnum.user_already_exists,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class UserWasNotRegisteredException(fa.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseDetailEnum.user_was_not_registered,
            headers={'WWW-Authenticate': 'Bearer'},
        )
