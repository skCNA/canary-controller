import signal
import threading
import time
from flask import jsonify, g, request


class ShutdownManager:
    def __init__(self):
        self._draining = threading.Event()
        self._lock = threading.Lock()
        self._in_flight = 0
        self._drain_started_at = None
        self._shutdown_reason = None

    def start(self):
        # Gunicorn worker 收到 SIGTERM/SIGINT 时触发优雅下线
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, _frame):
        self.start_drain(reason=f"signal:{signum}")

    def start_drain(self, reason="manual"):
        if not self._draining.is_set():
            self._draining.set()
            self._drain_started_at = time.time()
            self._shutdown_reason = reason

    def is_draining(self):
        return self._draining.is_set()

    def before_request(self):
        if self._is_exempt_path(request.path):
            return None
        if self.is_draining():
            return jsonify({"status": "draining", "message": "服务正在下线中"}), 503
        with self._lock:
            self._in_flight += 1
        g._counted_in_flight = True
        return None

    def teardown_request(self):
        if getattr(g, "_counted_in_flight", False):
            with self._lock:
                self._in_flight = max(0, self._in_flight - 1)

    def readiness_payload(self):
        return {
            "ready": not self.is_draining(),
            "draining": self.is_draining(),
            "in_flight": self._in_flight,
            "drain_started_at": self._drain_started_at,
            "shutdown_reason": self._shutdown_reason,
        }

    @staticmethod
    def _is_exempt_path(path):
        return path in ("/healthz", "/readyz")


def init_shutdown(app):
    manager = ShutdownManager()
    manager.start()
    app.extensions["shutdown_manager"] = manager

    @app.before_request
    def _before_request():
        return manager.before_request()

    @app.teardown_request
    def _teardown_request(_exc):
        manager.teardown_request()

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    @app.get("/readyz")
    def readyz():
        if manager.is_draining():
            return jsonify(manager.readiness_payload()), 503
        return jsonify(manager.readiness_payload()), 200

    return manager
