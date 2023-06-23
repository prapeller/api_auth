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
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class InvalidCredentialsException(fa.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseDetailEnum.invalid_credentials,
            headers={'WWW-Authenticate': 'Bearer'},
        )
