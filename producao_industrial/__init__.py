from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# Instâncias globais das extensões
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurações do LoginManager
    login_manager.login_view = 'main.login_admin'
    login_manager.login_message = 'Acesso restrito. Faça login como administrador.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # Registrar blueprint
    from .routes import main
    app.register_blueprint(main)

    # Criar tabelas com tratamento de erro melhorado
    with app.app_context():
        try:
            db.create_all()
            print("✅ Banco de dados criado/atualizado com sucesso!")
        except Exception as e:
            print(f"⚠️  Erro ao criar banco: {e}")
            # Não falha a aplicação por erro de BD

    return app