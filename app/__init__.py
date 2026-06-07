import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions (not yet bound to an app)
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_overrides: dict = None) -> Flask:
    """Application factory. Accepts optional config overrides for testing."""
    app = Flask(__name__)

    # --- Configuration ----------------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")

    if config_overrides:
        app.config.update(config_overrides)

    # --- Extensions -------------------------------------------------------------
    db.init_app(app)

    # --- Import all models so Alembic autogenerate sees every table -------------
    with app.app_context():
        from app.models import npc, player_profile, campaign, chat_message  # noqa: F401
    migrate.init_app(app, db)

    # --- Blueprints -------------------------------------------------------------
    from app.routes.npc import npc_bp
    from app.routes.player import player_bp
    from app.routes.campaign import campaign_bp

    app.register_blueprint(npc_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(campaign_bp)

    # Register debug routes only when running in debug mode
    if app.debug or os.getenv("FLASK_DEBUG", "0") == "1":
        from app.routes.debug import debug_bp
        app.register_blueprint(debug_bp)

    # Root route
    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
