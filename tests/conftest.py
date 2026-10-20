import pytest
from fastapi.testclient import TestClient
from opspilot import storage
from opspilot.api import app
@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(storage.settings,"data_dir",str(tmp_path))
    with TestClient(app) as c: yield c
