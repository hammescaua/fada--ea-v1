"""Testes de robustez/plataforma: CORS, /system, demo, dashboard, export CSV."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infra import models  # noqa: F401
from app.infra.db import Base, get_session
from app.main import app

pytestmark = pytest.mark.skipif(not settings.model_path.exists(), reason="modelo ausente")


@pytest.fixture
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    TS = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        s = TS()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_cors_header_present():
    client = TestClient(app)
    r = client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("access-control-allow-origin") == "*"


def test_system_status(client):
    s = client.get("/api/v1/system/status").json()
    assert s["status"] in {"ok", "degraded"}
    assert s["database"]["status"] == "ok"
    assert s["model"]["status"] == "ok"
    assert set(s["counts"]) == {"farms", "fields", "crop_cycles", "events"}


def test_demo_seed_populates(client):
    r = client.post("/api/v1/demo/seed")
    assert r.status_code == 201
    body = r.json()
    assert body["n_fields"] == 3
    counts = client.get("/api/v1/system/status").json()["counts"]
    assert counts["farms"] == 1 and counts["fields"] == 3 and counts["events"] > 0


def test_dashboard_after_demo(client):
    farm_id = client.post("/api/v1/demo/seed").json()["farm_id"]
    d = client.get(f"/api/v1/farms/{farm_id}/dashboard").json()
    assert d["n_fields"] == 3
    assert sum(d["attention"]["levels"].values()) == 3
    assert d["budget"]["planned_total"] > 0
    assert "next_operation" in d["agenda"]
    assert isinstance(d["insights"], list)


def test_dashboard_404(client):
    assert client.get("/api/v1/farms/999/dashboard").status_code == 404


def test_export_csv(client):
    farm_id = client.post("/api/v1/demo/seed").json()["farm_id"]
    r = client.get(f"/api/v1/farms/{farm_id}/operations.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    lines = r.text.strip().splitlines()
    assert lines[0] == "talhao,safra,data,operacao,produto,quantidade,unidade,custo"
    assert len(lines) > 1


def test_export_csv_404(client):
    assert client.get("/api/v1/farms/999/operations.csv").status_code == 404
