from app.security.passwords import hash_password, verify_password


def test_hashes_are_salted_and_password_verification_is_safe():
    first = hash_password("cloud12345")
    second = hash_password("cloud12345")
    assert first.startswith("$argon2id$")
    assert first != second
    assert verify_password("cloud12345", first)
    assert not verify_password("wrongpassword", first)
    assert not verify_password("cloud12345", "invalid-hash")
