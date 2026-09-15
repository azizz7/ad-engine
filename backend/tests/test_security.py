from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = get_password_hash("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_roundtrip():
    token = create_access_token({"sub": "user@example.com"})
    assert decode_access_token(token) == "user@example.com"


def test_expired_token_is_rejected():
    token = create_access_token({"sub": "user@example.com"}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_garbage_token_is_rejected():
    assert decode_access_token("not-a-real-token") is None
