from datetime import datetime

# IMPORTA db do __init__.py
from . import db

class Maquina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Parada')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    producoes = db.relationship('Producao', backref='maquina', lazy=True, cascade='all, delete-orphan')
    manutencoes = db.relationship('Manutencao', backref='maquina', lazy=True, cascade='all, delete-orphan')

class Operador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    turno = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(100), nullable=False)

class Producao(db.Model):
    __tablename__ = 'producao'
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    tempo = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.Index('idx_data', 'data'),)

class Manutencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maquina_id = db.Column(db.Integer, db.ForeignKey('maquina.id'), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    resolvida = db.Column(db.Boolean, default=False)