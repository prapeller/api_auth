from passlib.hash import bcrypt


def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)


def password_is_verified(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)
