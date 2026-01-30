from flask import Flask
from .shutdown import init_shutdown

def create_app():
    print("Creating app...")
    app = Flask(__name__)

    # 初始化优雅下线与健康检查
    init_shutdown(app)

    from .routes import main
    app.register_blueprint(main)
    print("App created")
    return app
