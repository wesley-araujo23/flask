from flask import Blueprint, render_template, request, redirect, make_response, flash, session, url_for
from .models import db, Maquina, Operador, Producao, Manutencao
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io
from datetime import datetime

main = Blueprint('main', __name__)

ADMIN_USER = 'admin'
ADMIN_PASS = '123456'  # Senha mais forte

def admin_required(f):
    """Decorator para proteger rotas admin"""
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            flash('Acesso negado. Faça login como admin.')
            return redirect(url_for('main.login_admin'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ---------------- LOGIN ADMIN ----------------
@main.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        senha = request.form['senha']
        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            session['admin'] = True
            flash('Login realizado com sucesso!')
            return redirect(url_for('main.admin'))
        flash('Usuário ou senha inválidos!')
    return render_template('adm/login_admin.html')

@main.route('/logout_admin')
def logout_admin():
    session.pop('admin', None)
    flash('Logout realizado!')
    return redirect(url_for('main.dashboard'))

# ---------------- PAINEL ADMIN ----------------
@main.route('/admin')
@admin_required
def admin():
    maquinas = Maquina.query.all()
    operadores = Operador.query.all()
    return render_template('adm/admin.html', maquinas=maquinas, operadores=operadores)

# ---------------- DASHBOARD ----------------
@main.route('/')
def dashboard():
    maquinas = Maquina.query.all()
    producoes = Producao.query.order_by(Producao.data.desc()).limit(50).all()  # Performance
    manutencoes = Manutencao.query.order_by(Manutencao.data.desc()).limit(10).all()

    # Stats otimizados com queries
    total = Maquina.query.count()
    ligadas = Maquina.query.filter_by(status='Ligada').count()
    manutencao_count = Maquina.query.filter_by(status='Manutenção').count()
    paradas = Maquina.query.filter_by(status='Parada').count()
    
    total_produzido = db.session.query(db.func.sum(Producao.quantidade)).scalar() or 0

    # Maquina mais usada (query otimizada)
    maquina_mais_usada = db.session.query(
        Producao.maquina_id, 
        db.func.sum(Producao.quantidade).label('total')
    ).group_by(Producao.maquina_id).order_by('total desc').first()
    
    if maquina_mais_usada:
        maquina_mais_usada = Maquina.query.get(maquina_mais_usada.maquina_id)

    ultima_manutencao = Manutencao.query.order_by(Manutencao.data.desc()).first()

    return render_template(
        'dashboard.html',
        maquinas=maquinas, total=total, ligadas=ligadas, manutencao=manutencao_count,
        paradas=paradas, total_produzido=total_produzido,
        maquina_mais_usada=maquina_mais_usada, ultima_manutencao=ultima_manutencao
    )

# ---------------- CRUD MAQUINAS ----------------
@main.route('/maquinas', methods=['GET', 'POST'])
def maquinas_view():
    if request.method == 'POST':
        if not all([request.form['nome'], request.form['setor'], request.form['status']]):
            flash('Preencha todos os campos!')
            return redirect(url_for('main.maquinas_view'))
            
        nova = Maquina(
            nome=request.form['nome'].strip(),
            setor=request.form['setor'].strip(),
            status=request.form['status']
        )
        db.session.add(nova)
        db.session.commit()
        flash('✅ Máquina cadastrada com sucesso!')
        return redirect(url_for('main.maquinas_view'))

    maquinas = Maquina.query.all()
    return render_template('maquinas.html', maquinas=maquinas)

# ---------------- CRUD OPERADORES ----------------
@main.route('/operadores', methods=['GET', 'POST'])
def operadores_view():
    if request.method == 'POST':
        if not all([request.form['nome'], request.form['setor'], request.form['turno']]):
            flash('Preencha todos os campos!')
            return redirect(url_for('main.operadores_view'))
            
        novo = Operador(
            nome=request.form['nome'].strip(),
            setor=request.form['setor'].strip(),
            turno=request.form['turno'].strip()
        )
        db.session.add(novo)
        db.session.commit()
        flash('✅ Operador cadastrado com sucesso!')
        return redirect(url_for('main.operadores_view'))

    operadores = Operador.query.all()
    return render_template('operadores.html', operadores=operadores)

# ---------------- CRUD MANUTENÇÃO ----------------
@main.route('/manutencao', methods=['GET', 'POST'])
def manutencao_view():
    if request.method == 'POST':
        if not all([request.form['maquina_id'], request.form['descricao']]):
            flash('Preencha todos os campos!')
            return redirect(url_for('main.manutencao_view'))
            
        nova = Manutencao(
            maquina_id=int(request.form['maquina_id']),
            descricao=request.form['descricao'].strip()
        )
        db.session.add(nova)
        db.session.commit()
        flash('✅ Manutenção registrada com sucesso!')
        return redirect(url_for('main.manutencao_view'))

    manutencoes = Manutencao.query.order_by(Manutencao.data.desc()).all()
    maquinas = Maquina.query.all()
    return render_template('manutencao.html', manutencoes=manutencoes, maquinas=maquinas)

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

# ---------------- PDF/EXCEL (mantidos iguais, funcionam bem) ----------------
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
        if y < 100:  # Nova página
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_industrial.pdf'
    return response

@main.route('/gerar_excel')
def gerar_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Máquinas"
    ws.append(['ID', 'Nome', 'Setor', 'Status', 'Data Cadastro'])

    for maquina in Maquina.query.all():
        ws.append([
            maquina.id, maquina.nome, maquina.setor, 
            maquina.status, maquina.data_cadastro
        ])

    arquivo = io.BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    response = make_response(arquivo.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_maquinas.xlsx'
    return response


@main.route('/excluir_manutencao/<int:id>')
@admin_required  # Só admin pode excluir
def excluir_manutencao(id):
    manutencao = Manutencao.query.get_or_404(id)
    db.session.delete(manutencao)
    db.session.commit()
    flash('Manutenção excluída com sucesso!')
    return redirect(url_for('main.manutencao_view'))

# Rotas DELETE/EDIT para operadores (admin only)
@main.route('/excluir_operador/<int:id>')
@admin_required
def excluir_operador(id):
    op = Operador.query.get_or_404(id)
    db.session.delete(op)
    db.session.commit()
    flash('Operador excluído!')
    return redirect(url_for('main.operadores_view'))

@main.route('/editar_operador/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_operador(id):
    op = Operador.query.get_or_404(id)
    if request.method == 'POST':
        op.nome = request.form['nome']
        op.setor = request.form['setor']
        op.turno = request.form['turno']
        db.session.commit()
        flash('Operador atualizado!')
        return redirect(url_for('main.operadores_view'))
    
    return render_template('operadores_edit.html', operador=op)


@main.route('/producao')
def producao_view():
    maquinas = Maquina.query.all()
    producoes = Producao.query.order_by(Producao.data.desc()).all()
    
    # Stats (você pode otimizar com queries)
    total_hoje = Producao.query.filter(
        Producao.data >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    return render_template('producao.html', maquinas=maquinas, producoes=producoes)

@main.route('/registrar_producao', methods=['POST'])
def registrar_producao():
    if not all([request.form['maquina_id'], request.form['quantidade'], request.form['tempo']]):
        flash('Preencha todos os campos!')
        return redirect(url_for('main.producao_view'))
    
    nova = Producao(
        maquina_id=int(request.form['maquina_id']),
        quantidade=int(request.form['quantidade']),
        tempo=float(request.form['tempo'])
    )
    db.session.add(nova)
    db.session.commit()
    flash('✅ Produção registrada com sucesso!')
    return redirect(url_for('main.producao_view'))

    # Rotas EDIT/DELETE para ADMIN
@main.route('/excluir_maquina/<int:id>')
@admin_required
def excluir_maquina(id):
    maq = Maquina.query.get_or_404(id)
    db.session.delete(maq)
    db.session.commit()
    flash('Máquina excluída!')
    return redirect(url_for('main.admin'))

@main.route('/editar_maquina/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_maquina(id):
    maq = Maquina.query.get_or_404(id)
    if request.method == 'POST':
        maq.nome = request.form['nome']
        maq.setor = request.form['setor']
        maq.status = request.form['status']
        db.session.commit()
        flash('Máquina atualizada!')
        return redirect(url_for('main.admin'))
    return render_template('adm/editar_maquina.html', maquina=maq)

