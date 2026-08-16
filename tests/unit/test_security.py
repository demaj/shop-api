from datetime import timedelta
from uuid import uuid4

import jwt as pyjwt
import pytest

from core import security
from core.config import get_settings


def test_hash_verify_round_trip() -> None:
    hashed = security.hash_password_sync("correct horse battery")
    assert security.verify_password_sync("correct horse battery", hashed)
    assert not security.verify_password_sync("wrong password", hashed)


def test_garbage_hash_is_false_not_error() -> None:
    assert not security.verify_password_sync("anything", "not-a-real-hash")
    assert not security.verify_password_sync("anything", "")


def test_token_round_trip() -> None:
    user_id = uuid4()
    token = security.create_access_token(user_id)
    assert security.decode_access_token(token).sub == str(user_id)


def test_expired_token_rejected() -> None:
    token = security.create_access_token(uuid4(), expires_delta=timedelta(minutes=-1))
    with pytest.raises(pyjwt.ExpiredSignatureError):
        security.decode_access_token(token)


def test_tampered_signature_rejected() -> None:
    token = security.create_access_token(uuid4())
    with pytest.raises(pyjwt.InvalidTokenError):
        security.decode_access_token(token[:-4] + "AAAA")


def test_alg_none_rejected() -> None:
    payload = pyjwt.decode(
        security.create_access_token(uuid4()),
        get_settings().SECRET_KEY.get_secret_value(),
        algorithms=[get_settings().ALGORITHM],
    )
    unsigned = pyjwt.encode(payload, key=None, algorithm="none")
    with pytest.raises(pyjwt.InvalidTokenError):
        security.decode_access_token(unsigned)
