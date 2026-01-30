from app import create_app


def test_readiness_default():
    app = create_app()
    client = app.test_client()

    resp = client.get("/readyz")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["ready"] is True
    assert data["draining"] is False


def test_draining_blocks_requests():
    app = create_app()
    client = app.test_client()
    manager = app.extensions["shutdown_manager"]

    manager.start_drain(reason="test")

    ready = client.get("/readyz")
    webhook = client.post("/webhook", json={"hello": "world"})

    assert ready.status_code == 503
    assert webhook.status_code == 503


def test_in_flight_count_resets():
    app = create_app()
    client = app.test_client()
    manager = app.extensions["shutdown_manager"]

    resp = client.post("/webhook", json={"ping": "pong"})

    assert resp.status_code == 200
    assert manager.readiness_payload()["in_flight"] == 0
