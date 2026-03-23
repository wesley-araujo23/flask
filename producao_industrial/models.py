from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Maquina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Parada')  # Default
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    producoes = db.relationship('Producao', backref='maquina', lazy=True, cascade='all, delete-orphan')
    manutencoes = db.relationship('Manutencao', backref='maquina', lazy=True, cascade='all, delete-orphan')

class Operador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(100), nullable=False)

class Producao(db.Model):
    __table_args__ = (db.Index('idx_data', 'data'),)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    tempo = db.Column(db.Float, nullable=False)  # horas
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Manutencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)  # Aumentei tamanho
    data = db.Column(db.DateTime, default=datetime.utcnow)
    resolvida = db.Column(db.Boolean, default=False)