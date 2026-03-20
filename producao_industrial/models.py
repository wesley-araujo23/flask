from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ---------------- MAQUINA ----------------

class Maquina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    producoes = db.relationship('Producao', backref='maquina', lazy=True)
    manutencoes = db.relationship('Manutencao', backref='maquina', lazy=True)

    def __repr__(self):
        return f"<Maquina {self.nome}>"

# ---------------- OPERADOR ----------------

class Operador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Operador {self.nome}>"

# ---------------- PRODUCAO ----------------

class Producao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    tempo = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Producao {self.id}>"

# ---------------- MANUTENCAO ----------------

class Manutencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Manutencao {self.id}>"