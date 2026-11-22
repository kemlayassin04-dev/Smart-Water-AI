from flask import Flask
from config import get_config
from extensions import db, login_manager, limiter, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY manquante dans .env")

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL manquante dans .env")

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    from models.user import User
    from models.sector import Sector
    from models.alert import Alert
    from models.intervention import Intervention
    from models.network_performance import NetworkPerformance

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.pages import pages_bp
    from routes.auth import auth_bp
    from routes.sectors import sectors_bp
    from routes.alerts import alerts_bp


    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(sectors_bp)
    app.register_blueprint(alerts_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)