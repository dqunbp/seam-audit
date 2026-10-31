from datetime import datetime, timezone

import pytest

from pixforge import clock, db
from pixforge.users import create_user

from .fakes import FakeLumenClient


@pytest.fixture(autouse=True)
def frozen_clock():
    clock.set_now(datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc))
    yield
    clock.set_now(None)


@pytest.fixture
def conn():
    connection = db.connect()
    db.migrate(connection)
    yield connection
    connection.close()


@pytest.fixture
def user_id(conn):
    return create_user(conn, "free@example.com", plan="free", balance=100)


@pytest.fixture
def pro_user_id(conn):
    return create_user(conn, "pro@example.com", plan="pro", balance=100)


@pytest.fixture
def lumen():
    return FakeLumenClient()
