from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


password_manager = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_manager.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return password_manager.verify(plain_password, password_hash)
    except (UnknownHashError, ValueError):
        return False
