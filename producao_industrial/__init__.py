from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from .config import Config
import os

# ✅ ÚNICA INSTÂNCIA GLOBAL
db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(int(user_id))

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    os.makedirs(app.instance_path, exist_ok=True)
    
    # ✅ INICIALIZA ÚNICA VEZ
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'main.login_admin'
    login_manager.login_message = 'Acesso restrito. Faça login como administrador.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # ✅ IMPORTA MODELS E ROUTES NO CONTEXTO
    with app.app_context():
        from . import models  # Registra models com db correto
        from .routes import main
        app.register_blueprint(main)
        db.create_all()
        print("✅ ✅ DB + MODELS + ROUTES PRONTOS!")

    return app