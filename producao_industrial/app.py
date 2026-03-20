from flask import Flask, render_template, request, redirect, make_response, flash, session
from config import Config
from models import db, Maquina, Operador, Producao, Manutencao
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io

# ---------------- ADMIN ----------------
ADMIN_USER = 'admin'
ADMIN_PASS = '123'

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- LOGIN ADMIN ----------------
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin')

        flash('Login inválido')

    return render_template('adm/login_admin.html')

@app.route('/logout_admin')
def logout_admin():
    session.pop('admin', None)
    return redirect('/')

# ---------------- PAINEL ADMIN ----------------
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login_admin')

    maquinas = Maquina.query.all()
    operadores = Operador.query.all()
    return render_template('adm/admin.html', maquinas=maquinas, operadores=operadores)

# ---------------- DASHBOARD ----------------
@app.route('/')
def dashboard():
    maquinas = Maquina.query.all()
    producoes = Producao.query.all()
    manutencoes = Manutencao.query.all()

    total = len(maquinas)
    ligadas = len([m for m in maquinas if m.status == 'Ligada'])
    manutencao_count = len([m for m in maquinas if m.status == 'Manutenção'])
    paradas = len([m for m in maquinas if m.status == 'Parada'])

    total_produzido = sum(p.quantidade for p in producoes)

    maquina_mais_usada = None
    if producoes:
        contador = {}
        for p in producoes:
            contador[p.maquina_id] = contador.get(p.maquina_id, 0) + p.quantidade
        maquina_id = max(contador, key=contador.get)
        maquina_mais_usada = Maquina.query.get(maquina_id)

    ultima_manutencao = manutencoes[-1] if manutencoes else None

    return render_template(
        'dashboard.html',
        maquinas=maquinas,
        total=total,
        ligadas=ligadas,
        manutencao=manutencao_count,
        paradas=paradas,
        total_produzido=total_produzido,
        maquina_mais_usada=maquina_mais_usada,
        ultima_manutencao=ultima_manutencao
    )

# ---------------- MAQUINAS ----------------
@app.route('/maquinas', methods=['GET', 'POST'])
def maquinas_view():
    if request.method == 'POST':
        nova = Maquina(
            nome=request.form['nome'],
            setor=request.form['setor'],
            status=request.form['status']
        )
        db.session.add(nova)
        db.session.commit()
        flash('Máquina cadastrada com sucesso!')
        return redirect('/maquinas')

    maquinas = Maquina.query.all()
    return render_template('maquinas.html', maquinas=maquinas)

# ---------------- OPERADORES ----------------
@app.route('/operadores', methods=['GET', 'POST'])
def operadores_view():
    if request.method == 'POST':
        novo = Operador(
            nome=request.form['nome'],
            setor=request.form['setor'],
            turno=request.form['turno']
        )
        db.session.add(novo)
        db.session.commit()
        flash('Operador cadastrado com sucesso!')
        return redirect('/operadores')

    operadores = Operador.query.all()
    return render_template('operadores.html', operadores=operadores)

# ---------------- MANUTENÇÃO ----------------
@app.route('/manutencao', methods=['GET', 'POST'])
def manutencao_view():
    if request.method == 'POST':
        nova = Manutencao(
            maquina_id=request.form['maquina_id'],
            descricao=request.form['descricao']
        )
        db.session.add(nova)
        db.session.commit()
        flash('Manutenção registrada com sucesso!')
        return redirect('/manutencao')

    manutencoes = Manutencao.query.all()
    maquinas = Maquina.query.all()
    return render_template('manutencao.html', manutencoes=manutencoes, maquinas=maquinas)

# ---------------- RELATÓRIOS ----------------
@app.route('/relatorios')
def relatorios_view():
    total_maquinas = Maquina.query.count()
    total_operadores = Operador.query.count()
    total_producao = Producao.query.count()
    total_manutencao = Manutencao.query.count()
    
    valores = [total_maquinas, total_operadores, total_producao, total_manutencao]
    maximo = max(valores) if valores else 1

    return render_template(
        'relatorios.html',
        total_maquinas=total_maquinas,
        total_operadores=total_operadores,
        total_producao=total_producao,
        total_manutencao=total_manutencao,
        maximo=maximo
    )

# ---------------- PDF ----------------
@app.route('/gerar_pdf')
def gerar_pdf():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, 750, "Relatório Industrial")

    y = 720
    for maquina in Maquina.query.all():
        pdf.drawString(100, y, f"{maquina.nome} | {maquina.setor} | {maquina.status}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio.pdf'
    return response

# ---------------- EXCEL ----------------
@app.route('/gerar_excel')
def gerar_excel():
    wb = Workbook()
    ws = wb.active
    ws.append(['Nome', 'Setor', 'Status'])

    for maquina in Maquina.query.all():
        ws.append([maquina.nome, maquina.setor, maquina.status])

    arquivo = io.BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    response = make_response(arquivo.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_maquinas.xlsx'
    return response

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)