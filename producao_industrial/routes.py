from flask import Blueprint, render_template, request, redirect, make_response, flash, session, url_for, abort
from . import db
from .models import Maquina, Operador, Producao, Manutencao
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io
from datetime import datetime, date
from sqlalchemy import func, desc, or_

main = Blueprint('main', __name__)

ADMIN_USER = 'admin'
ADMIN_PASS = '123456'

def admin_required(f):
    """Decorator para rotas que exigem autenticação admin"""
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            flash('Acesso negado. Faça login como admin.', 'danger')
            return redirect(url_for('main.login_admin'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# =====================================================================
# DASHBOARD E PÁGINAS PÚBLICAS
# =====================================================================
@main.route('/')
def dashboard():
    """Dashboard principal com estatísticas"""
    maquinas = Maquina.query.all()
    producoes_recentes = Producao.query.order_by(Producao.data.desc()).limit(10).all()
    
    total_maquinas = len(maquinas)
    ligadas = len([m for m in maquinas if m.status == 'Ligada'])
    paradas = len([m for m in maquinas if m.status == 'Parada'])
    total_produzido = Producao.query.with_entities(func.sum(Producao.quantidade)).scalar() or 0
    
    hoje = date.today()
    producao_hoje = Producao.query.filter(
        func.date(Producao.data) == hoje
    ).with_entities(func.sum(Producao.quantidade)).scalar() or 0

    return render_template('dashboard.html', 
                         maquinas=maquinas, 
                         total_maquinas=total_maquinas,
                         ligadas=ligadas, paradas=paradas, 
                         total_produzido=total_produzido,
                         producao_hoje=producao_hoje,
                         producoes_recentes=producoes_recentes)

# =====================================================================
# ADMIN - PAINEL PRINCIPAL
# =====================================================================
@main.route('/admin')
@main.route('/admin/painel')
@admin_required
def admin_painel():
    """Painel administrativo principal"""
    operadores = Operador.query.order_by(Operador.nome).all()
    maquinas = Maquina.query.order_by(Maquina.nome).all()
    
    # Estatísticas para o painel
    stats = {
        'total_operadores': len(operadores),
        'total_maquinas': len(maquinas),
        'maquinas_ligadas': len([m for m in maquinas if m.status == 'Ligada'])
    }
    
    manutencoes_count = Manutencao.query.count()
    producoes_count = Producao.query.count()
    
    return render_template('adm/admin.html',  # ✅ CORRIGIDO para pasta adm/
                         operadores=operadores, 
                         maquinas=maquinas,
                         stats=stats,
                         manutencoes_count=manutencoes_count,
                         producoes_count=producoes_count)

# =====================================================================
# MÁQUINAS - CRUD
# =====================================================================
@main.route('/admin/nova_maquina')
@main.route('/admin/editar_maquina/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_maquina(id=None):
    """CRUD completo para máquinas (admin) - cria e edita"""
    if id:
        maquina = Maquina.query.get_or_404(id)
    else:
        maquina = Maquina()  # ✅ OBJETO VAZIO PARA NOVO
    
    if request.method == 'POST':
        try:
            maquina.nome = request.form['nome'].strip()
            maquina.setor = request.form['setor'].strip()
            maquina.status = request.form['status']
            maquina.observacoes = request.form.get('observacoes', '').strip()
            
            if id:  # Editar
                db.session.commit()
                flash('✅ Máquina atualizada!', 'success')
            else:  # Criar novo
                db.session.add(maquina)
                db.session.commit()
                flash('✅ Nova máquina criada!', 'success')
            
            return redirect(url_for('main.admin_painel'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao salvar!', 'danger')
            print(f"Erro: {e}")
    
    # Estatísticas da máquina (só se existir)
    tempo_total = 0.0
    ultima_manutencao = None
    if id:
        tempo_total = sum(p.tempo for p in getattr(maquina, 'producoes', [])) if hasattr(maquina, 'producoes') else 0.0
        ultima_manutencao_obj = getattr(maquina.manutencoes, '0', None)
        ultima_manutencao = ultima_manutencao_obj.data.strftime('%d/%m/%Y') if ultima_manutencao_obj else None
    
    return render_template('adm/editar_maquina.html', 
                         maquina=maquina, 
                         tempo_total=tempo_total,
                         ultima_manutencao=ultima_manutencao)
# =====================================================================
# OPERADORES - CRUD ✅ ATUALIZADO
# =====================================================================
@main.route('/admin/novo_operador')
@main.route('/admin/editar_operador/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_operador(id=None):
    """CRUD completo para operadores (admin) - cria e edita"""
    if id:
        operador = Operador.query.get_or_404(id)
    else:
        operador = Operador()  # ✅ OBJETO VAZIO PARA NOVO
    
    if request.method == 'POST':
        try:
            operador.nome = request.form['nome'].strip()
            operador.setor = request.form.get('setor', '').strip()
            operador.turno = request.form['turno'].strip()
            operador.observacoes = request.form.get('observacoes', '').strip()
            operador.meta_producao = request.form.get('meta_producao', type=int, default=0)
            
            if id:  # Editar
                db.session.commit()
                flash('✅ Operador atualizado!', 'success')
            else:  # Criar novo
                db.session.add(operador)
                db.session.commit()
                flash('✅ Novo operador criado!', 'success')
            
            return redirect(url_for('main.admin_painel'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao salvar!', 'danger')
    
    tempo_total = 0.0
    if id:
        tempo_total = sum(p.tempo for p in getattr(operador, 'producoes', [])) if hasattr(operador, 'producoes') else 0.0
    
    return render_template('adm/editar_operador.html', 
                         operador=operador, 
                         tempo_total=tempo_total)

@main.route('/admin/excluir_operador/<int:id>')
@admin_required
def excluir_operador(id):
    """Exclui operador"""
    try:
        operador = Operador.query.get_or_404(id)
        db.session.delete(operador)
        db.session.commit()
        flash('✅ Operador excluído!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Erro ao excluir!', 'danger')
    
    return redirect(url_for('main.admin_painel'))

@main.route('/operadores', methods=['GET', 'POST'])
def operadores_view():
    """Lista e gerencia operadores (público)"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'create':
                novo = Operador(
                    nome=request.form['nome'].strip(),
                    setor=request.form.get('setor', '').strip(),
                    turno=request.form['turno'].strip(),
                    observacoes=request.form.get('observacoes', '').strip(),
                    meta_producao=request.form.get('meta_producao', type=int, default=0)
                )
                db.session.add(novo)
                db.session.commit()
                flash('✅ Operador cadastrado!', 'success')
                
            elif action == 'update':
                operador = Operador.query.get_or_404(request.form['id'])
                operador.nome = request.form['nome'].strip()
                operador.setor = request.form.get('setor', '').strip()
                operador.turno = request.form['turno'].strip()
                operador.observacoes = request.form.get('observacoes', '').strip()
                operador.meta_producao = request.form.get('meta_producao', type=int, default=0)
                db.session.commit()
                flash('✅ Operador atualizado!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao salvar operador!', 'danger')
            print(f"Erro: {e}")
        
        return redirect(url_for('main.operadores_view'))

    operadores = Operador.query.order_by(Operador.nome).all()
    return render_template('operadores.html', operadores=operadores)

@main.route('/operador/<int:id>')
def operador_detalhes(id):
    """Detalhes do operador"""
    operador = Operador.query.get_or_404(id)
    tempo_total = sum(p.tempo for p in getattr(operador, 'producoes', [])) if hasattr(operador, 'producoes') else 0.0
    return render_template('operador_detalhes.html', operador=operador, tempo_total=tempo_total)

# =====================================================================
# PRODUÇÃO - CRUD ✅ ATUALIZADO
# =====================================================================
@main.route('/admin/nova_producao')
@main.route('/admin/editar_producao/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_producao(id=None):
    """CRUD completo para produção (admin) - cria e edita"""
    if id:
        producao = Producao.query.get_or_404(id)
    else:
        producao = Producao()  # ✅ OBJETO VAZIO PARA NOVO
    
    if request.method == 'POST':
        try:
            producao.maquina_id = int(request.form['maquina_id'])
            producao.operador_id = int(request.form.get('operador_id') or 1)
            producao.quantidade = int(request.form['quantidade'])
            producao.tempo = float(request.form['tempo'])
            producao.observacoes = request.form.get('observacoes', '').strip()
            producao.data = datetime.now()
            
            if id:  # Editar
                db.session.commit()
                flash('✅ Produção atualizada!', 'success')
            else:  # Criar novo
                db.session.add(producao)
                db.session.commit()
                flash('✅ Nova produção registrada!', 'success')
            
            return redirect(url_for('main.producao_view'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao salvar!', 'danger')
    
    maquinas = Maquina.query.all()
    operadores = Operador.query.all()
    return render_template('adm/editar_producao.html', 
                         producao=producao, 
                         maquinas=maquinas,
                         operadores=operadores)

@main.route('/producao')
def producao_view():
    """Visão geral da produção"""
    maquinas = Maquina.query.order_by(Maquina.nome).all()
    operadores = Operador.query.order_by(Operador.nome).all()
    producoes = Producao.query.order_by(Producao.data.desc()).limit(100).all()
    return render_template('producao.html', maquinas=maquinas, operadores=operadores, producoes=producoes)

@main.route('/registrar_producao', methods=['POST'])
def registrar_producao():
    """Registra nova produção"""
    try:
        nova = Producao(
            maquina_id=int(request.form['maquina_id']),
            operador_id=int(request.form.get('operador_id') or 1),
            quantidade=int(request.form['quantidade']),
            tempo=float(request.form['tempo']),
            observacoes=request.form.get('observacoes', '').strip()
        )
        db.session.add(nova)
        db.session.commit()
        flash('✅ Produção registrada!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Erro ao registrar produção!', 'danger')
        print(f"Erro: {e}")
    
    return redirect(url_for('main.producao_view'))

@main.route('/admin/excluir_producao/<int:id>')
@admin_required
def excluir_producao(id):
    """Exclui produção (admin)"""
    try:
        producao = Producao.query.get_or_404(id)
        db.session.delete(producao)
        db.session.commit()
        flash('✅ Produção excluída!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Erro ao excluir!', 'danger')
    
    return redirect(url_for('main.producao_view'))

@main.route('/producao/<int:id>')
def producao_detalhes(id):
    """Detalhes da produção"""
    producao = Producao.query.get_or_404(id)
    produtividade = producao.quantidade / producao.tempo if producao.tempo > 0 else 0
    return render_template('producao_detalhes.html', producao=producao, produtividade=produtividade)

# =====================================================================
# MANUTENÇÃO - CRUD ✅ ATUALIZADO
# =====================================================================
@main.route('/admin/nova_manutencao')
@main.route('/admin/editar_manutencao/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_manutencao(id=None):
    """CRUD completo para manutenção (admin) - cria e edita"""
    if id:
        manutencao = Manutencao.query.get_or_404(id)
    else:
        manutencao = Manutencao()  # ✅ OBJETO VAZIO PARA NOVO
    
    if request.method == 'POST':
        try:
            manutencao.maquina_id = int(request.form['maquina_id'])
            manutencao.descricao = request.form['descricao'].strip()
            manutencao.resolvida = request.form.get('resolvida') == 'on'
            manutencao.data_resolucao = request.form.get('data_resolucao') if request.form.get('data_resolucao') else None
            manutencao.custo = float(request.form.get('custo', 0) or 0)
            
            if id:  # Editar
                db.session.commit()
                flash('✅ Manutenção atualizada!', 'success')
            else:  # Criar novo
                manutencao.data = datetime.now()  # ✅ DATA AUTOMÁTICA
                db.session.add(manutencao)
                db.session.commit()
                flash('✅ Nova manutenção registrada!', 'success')
            
            return redirect(url_for('main.manutencao_view'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao salvar!', 'danger')
            print(f"Erro: {e}")
    
    maquinas = Maquina.query.all()
    return render_template('adm/editar_manutencao.html', 
                         manutencao=manutencao, 
                         maquinas=maquinas)

@main.route('/manutencao', methods=['GET', 'POST'])
def manutencao_view():
    """Gerencia manutenções"""
    if request.method == 'POST':
        try:
            nova = Manutencao(
                maquina_id=int(request.form['maquina_id']),
                descricao=request.form['descricao'].strip(),
                resolvida=request.form.get('resolvida') == 'on',
                data_resolucao=request.form.get('data_resolucao') if request.form.get('data_resolucao') else None,
                custo=float(request.form.get('custo', 0) or 0),
                data=datetime.now()  # ✅ DATA AUTOMÁTICA
            )
            db.session.add(nova)
            db.session.commit()
            flash('✅ Manutenção registrada!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('❌ Erro ao registrar!', 'danger')
            print(f"Erro: {e}")
        return redirect(url_for('main.manutencao_view'))

    manutencoes = Manutencao.query.order_by(Manutencao.data.desc()).all()
    maquinas = Maquina.query.order_by(Maquina.nome).all()
    return render_template('manutencao.html', manutencoes=manutencoes, maquinas=maquinas)

@main.route('/admin/excluir_manutencao/<int:id>')
@admin_required
def excluir_manutencao(id):
    """Exclui manutenção (admin)"""
    try:
        manutencao = Manutencao.query.get_or_404(id)
        db.session.delete(manutencao)
        db.session.commit()
        flash('✅ Manutenção excluída!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Erro ao excluir!', 'danger')
        print(f"Erro: {e}")
    
    return redirect(url_for('main.manutencao_view'))
# =====================================================================
# RELATÓRIOS
# =====================================================================
@main.route('/relatorios')
def relatorios_view():
    """Dashboard de relatórios"""
    stats = {
        'total_maquinas': Maquina.query.count(),
        'total_operadores': Operador.query.count(),
        'total_producao': Producao.query.count(),
        'total_manutencao': Manutencao.query.count(),
        'producao_hoje': Producao.query.filter(
            func.date(Producao.data) == date.today()
        ).with_entities(func.sum(Producao.quantidade)).scalar() or 0,
        'maquinas_ligadas': Maquina.query.filter_by(status='Ligada').count()
    }
    
    maximo = max(stats.values()) if any(stats.values()) else 1
    return render_template('relatorios.html', **stats, maximo=maximo)

@main.route('/relatorios/excel')
def relatorios_excel():
    """Exporta relatório em Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Produção Industrial"
    
    # Headers
    ws.append(['ID', 'Máquina', 'Operador', 'Quantidade', 'Tempo (h)', 'Produtividade (p/h)', 'Data'])
    
    for prod in Producao.query.order_by(Producao.data.desc()).all():
        produtividade = prod.quantidade / prod.tempo if prod.tempo > 0 else 0
        ws.append([
            prod.id,
            prod.maquina.nome,
            prod.operador.nome,
            prod.quantidade,
            f"{prod.tempo:.1f}",
            f"{produtividade:.1f}",
            prod.data.strftime('%d/%m/%Y %H:%M')
        ])
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_producao.xlsx'
    return response

@main.route('/relatorios/pdf')
def gerar_pdf():
    """Gera relatório em PDF"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(100, 750, "📊 RELATÓRIO INDUSTRIAL - SENAI")
    pdf.setFont("Helvetica", 12)
    
    y = 700
    pdf.drawString(100, y, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 40
    
    total_producao = Producao.query.with_entities(func.sum(Producao.quantidade)).scalar() or 0
    pdf.drawString(100, y, f"📈 Total Produzido: {total_producao:,} peças")
    y -= 50
    
    pdf.drawString(100, y, "🏭 MÁQUINAS:")
    y -= 30
    
    for maquina in Maquina.query.order_by(Maquina.nome).limit(10).all():
        pdf.drawString(120, y, f"🔧 {maquina.nome} | {maquina.setor} | {maquina.status}")
        y -= 25
        if y < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 750
    
    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
    return response

# =====================================================================
# AUTENTICAÇÃO ADMIN
# =====================================================================
@main.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    """Login do administrador"""
    if request.method == 'POST':
        username = request.form.get('user', '').strip()
        password = request.form.get('pass', '').strip()
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin'] = True
            flash('✅ Login realizado com sucesso!', 'success')
            return redirect(url_for('main.admin_painel'))
        else:
            flash('❌ Usuário ou senha incorretos!', 'danger')
    
    return render_template('login_admin.html')

@main.route('/logout')
@main.route('/logout_admin')
def logout_admin():
    """Logout do administrador"""
    session.pop('admin', None)
    flash('👋 Você foi deslogado com sucesso!', 'info')
    return redirect(url_for('main.login_admin'))

# =====================================================================
# BUSCA E FILTROS
# =====================================================================
@main.route('/busca')
def busca():
    """Busca global em todas as entidades"""
    termo = request.args.get('q', '').lower().strip()
    
    if not termo:
        return redirect(url_for('main.dashboard'))
    
    # Busca em múltiplas entidades
    maquinas = Maquina.query.filter(
        Maquina.nome.contains(termo) | Maquina.setor.contains(termo)
    ).all()
    
    operadores = Operador.query.filter(
        Operador.nome.contains(termo) | Operador.setor.contains(termo)
    ).all()
    
    producoes = Producao.query.join(Maquina).join(Operador).filter(
        or_(
            Maquina.nome.contains(termo),
            Operador.nome.contains(termo)
        )
    ).order_by(Producao.data.desc()).limit(20).all()
    
    return render_template('busca.html', 
                         termo=termo,
                         maquinas=maquinas,
                         operadores=operadores,
                         producoes=producoes)

# =====================================================================
# API ENDPOINTS (JSON)
# =====================================================================
@main.route('/api/maquinas')
def api_maquinas():
    """API para listar máquinas em JSON"""
    maquinas = Maquina.query.all()
    return {
        'maquinas': [{
            'id': m.id,
            'nome': m.nome,
            'status': m.status,
            'setor': m.setor
        } for m in maquinas]
    }

@main.route('/api/status_maquinas')
def api_status_maquinas():
    """API para status das máquinas"""
    stats = {
        'ligadas': Maquina.query.filter_by(status='Ligada').count(),
        'paradas': Maquina.query.filter_by(status='Parada').count(),
        'total': Maquina.query.count()
    }
    return stats

# =====================================================================
# ERRO HANDLERS
# =====================================================================
@main.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# =====================================================================
# MÁQUINAS - LISTA E CRUD PÚBLICO
# =====================================================================
@main.route('/maquinas')
def maquinas_view():
    """Lista todas as máquinas (público)"""
    maquinas = Maquina.query.order_by(Maquina.nome).all()
    
    # Estatísticas
    stats = {
        'total': len(maquinas),
        'ligadas': len([m for m in maquinas if m.status == 'Ligada']),
        'paradas': len([m for m in maquinas if m.status == 'Parada']),
        'manutencao': len([m for m in maquinas if m.status == 'Manutenção'])
    }
    
    return render_template('maquinas.html', 
                         maquinas=maquinas, 
                         stats=stats)

@main.route('/maquina/<int:id>')
def maquina_detalhes(id):
    """Detalhes da máquina"""
    maquina = Maquina.query.get_or_404(id)
    
    # Estatísticas
    tempo_total = sum(p.tempo for p in maquina.producoes) if maquina.producoes else 0
    total_produzido = sum(p.quantidade for p in maquina.producoes) if maquina.producoes else 0
    produtividade = total_produzido / tempo_total if tempo_total > 0 else 0
    manutencoes_pendentes = [m for m in maquina.manutencoes if not m.resolvida]
    
    return render_template('maquina_detalhes.html', 
                         maquina=maquina,
                         tempo_total=tempo_total,
                         total_produzido=total_produzido,
                         produtividade=produtividade,
                         manutencoes_pendentes=manutencoes_pendentes)