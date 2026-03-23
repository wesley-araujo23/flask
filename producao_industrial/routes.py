from flask import Blueprint, render_template, request, redirect, make_response, flash, session, url_for
from . import db  # ← IMPORT LOCAL DO PACOTE
from .models import Maquina, Operador, Producao, Manutencao  # ← IMPORTS DIRETOS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io
from datetime import datetime

main = Blueprint('main', __name__)

ADMIN_USER = 'admin'
ADMIN_PASS = '123456'

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            flash('Acesso negado. Faça login como admin.')
            return redirect(url_for('main.login_admin'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@main.route('/')
def dashboard():
    maquinas = Maquina.query.all()
    producoes = Producao.query.order_by(Producao.data.desc()).limit(50).all()
    
    total = len(maquinas)
    ligadas = len([m for m in maquinas if m.status == 'Ligada'])
    paradas = len([m for m in maquinas if m.status == 'Parada'])
    total_produzido = sum(p.quantidade for p in producoes)

    return render_template('dashboard.html', 
                         maquinas=maquinas, total=total, ligadas=ligadas, 
                         paradas=paradas, total_produzido=total_produzido,
                         producoes=producoes)

# ---------------- MAQUINAS ----------------
@main.route('/maquinas', methods=['GET', 'POST'])
def maquinas_view():
    if request.method == 'POST':
        nova = Maquina(
            nome=request.form['nome'].strip(),
            setor=request.form['setor'].strip(),
            status=request.form['status']
        )
        db.session.add(nova)
        db.session.commit()
        flash('✅ Máquina cadastrada!')
        return redirect(url_for('main.maquinas_view'))

    maquinas = Maquina.query.all()
    return render_template('maquinas.html', maquinas=maquinas)

# ---------------- OPERADORES ----------------
@main.route('/operadores', methods=['GET', 'POST'])
def operadores_view():
    if request.method == 'POST':
        novo = Operador(
            nome=request.form['nome'].strip(),
            setor=request.form['setor'].strip(),
            turno=request.form['turno'].strip()
        )
        db.session.add(novo)
        db.session.commit()
        flash('✅ Operador cadastrado!')
        return redirect(url_for('main.operadores_view'))

    operadores = Operador.query.all()
    return render_template('operadores.html', operadores=operadores)

# ---------------- MANUTENÇÃO ----------------
@main.route('/manutencao', methods=['GET', 'POST'])
def manutencao_view():
    if request.method == 'POST':
        nova = Manutencao(
            maquina_id=int(request.form['maquina_id']),
            descricao=request.form['descricao'].strip()
        )
        db.session.add(nova)
        db.session.commit()
        flash('✅ Manutenção registrada!')
        return redirect(url_for('main.manutencao_view'))

    manutencoes = Manutencao.query.order_by(Manutencao.data.desc()).all()
    maquinas = Maquina.query.all()
    return render_template('manutencao.html', manutencoes=manutencoes, maquinas=maquinas)

# ---------------- PRODUÇÃO ----------------
@main.route('/producao')
def producao_view():
    maquinas = Maquina.query.all()
    producoes = Producao.query.order_by(Producao.data.desc()).all()
    return render_template('producao.html', maquinas=maquinas, producoes=producoes)

@main.route('/registrar_producao', methods=['POST'])
def registrar_producao():
    nova = Producao(
        maquina_id=int(request.form['maquina_id']),
        quantidade=int(request.form['quantidade']),
        tempo=float(request.form['tempo'])
    )
    db.session.add(nova)
    db.session.commit()
    flash('✅ Produção registrada!')
    return redirect(url_for('main.producao_view'))

# ---------------- RELATÓRIOS ----------------
@main.route('/relatorios')
def relatorios_view():
    stats = {
        'total_maquinas': Maquina.query.count(),
        'total_operadores': Operador.query.count(),
        'total_producao': Producao.query.count(),
        'total_manutencao': Manutencao.query.count()
    }
    
    maximo = max(stats.values()) if stats['total_maquinas'] > 0 else 1
    return render_template('relatorios.html', **stats, maximo=maximo)

# ---------------- PDF ----------------
@main.route('/gerar_pdf')
def gerar_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 750, "📊 RELATÓRIO INDUSTRIAL - SENAI")
    pdf.setFont("Helvetica", 12)
    
    y = 720
    for maquina in Maquina.query.all():
        pdf.drawString(100, y, f"🔧 {maquina.nome} | {maquina.setor} | {maquina.status}")
        y -= 25
        if y < 100:
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
    return response

# ---------------- ADMIN ----------------
@main.route('/excluir_manutencao/<int:id>')
@admin_required
def excluir_manutencao(id):
    manutencao = Manutencao.query.get_or_404(id)
    db.session.delete(manutencao)
    db.session.commit()
    flash('✅ Excluído!')
    return redirect(url_for('main.manutencao_view'))

@main.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('user', '').strip()
        password = request.form.get('pass', '').strip()
        
        # CREDENCIAIS FIXAS
        if username == 'admin' and password == '123456':
            session['admin'] = True
            flash('✅ Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('❌ Usuário ou senha incorretos!', 'danger')
    
    return render_template('login_admin.html')

@main.route('/logout_admin')
def logout_admin():
    session.pop('admin', None)
    flash('👋 Logout!')
    return redirect(url_for('main.login_admin'))