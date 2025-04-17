from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agricultura.db')
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'uma_chave_super_secreta'

def get_db():
    """Conecta ao banco de dados SQLite."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row  # Para acessar colunas por nome
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Fecha a conexão com o banco de dados."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa o banco de dados."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Comando CLI para inicializar o banco de dados."""
    init_db()
    print('Banco de dados inicializado.')

@app.template_filter('format_datetime')
def format_datetime(value):
    if value:
        date_object = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return date_object.strftime('%d/%m/%Y %H:%M:%S')
    else:
        return ""

@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html', active_page='dashboard', now=datetime.now())

@app.route('/api/culturas-ativas')
def culturas_ativas():
    """API para obter culturas ativas."""
    try:
        with get_db() as conn:
            # Consulta para obter culturas ativas
            culturas = conn.execute("SELECT id, nome, ciclo FROM cultura").fetchall()
        # Formata os resultados para JSON
        culturas_json = [{'id': c['id'], 'nome': c['nome'], 'ciclo': c['ciclo']} for c in culturas]
        return jsonify(culturas_json)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/culturas')
def culturas():
    """Página para listar todas as culturas"""
    try:
        with get_db() as conn:
            # Modifique a consulta SQL para selecionar apenas as colunas existentes
            lista_culturas = conn.execute("SELECT id, nome, ciclo FROM cultura ORDER BY nome ASC").fetchall()
        # Renderiza o template cultura.html
        return render_template('cultura.html',
                            culturas=lista_culturas,
                            active_page='cultura',
                            now=datetime.now())
    except sqlite3.Error as e:
         flash(f"Erro ao buscar lista de culturas: {e}", "danger")
         return render_template('cultura.html', culturas=[], active_page='cultura', now=datetime.now())

def get_defensivos(classe=None):
    """Obtém a lista de defensivos do banco de dados."""
    try:
        with get_db() as conn:
            if classe:
                cursor = conn.execute("SELECT id, nome_comercial, classe FROM defensivo WHERE classe = ?", (classe,))
            else:
                cursor = conn.execute("SELECT id, nome_comercial, classe FROM defensivo")
            return cursor.fetchall()
    except sqlite3.Error as e:
        flash(f'Erro ao obter defensivos: {e}', 'danger')
        print(f'Erro ao obter defensivos: {e}')
        return []

def get_setores():
    """Obtém a lista de setores únicos do banco de dados."""
    try:
        with get_db() as conn:
            cursor = conn.execute("SELECT DISTINCT id, nome FROM setor")
            return cursor.fetchall()
    except sqlite3.Error as e:
        flash(f'Erro ao obter setores: {e}', 'danger')
        print(f'Erro ao obter setores: {e}')
        return []

def get_canteiros():
    """Obtém a lista de números de canteiros únicos do banco de dados."""
    try:
        with get_db() as conn:
            cursor = conn.execute("SELECT DISTINCT canteiro_numero FROM canteiro")
            result = cursor.fetchall()
            print("Dados retornados por get_canteiros:", result)
            return [row['canteiro_numero'] for row in result if row['canteiro_numero'] is not None]
    except sqlite3.Error as e:
        flash(f'Erro ao obter canteiros: {e}', 'danger')
        print(f'Erro ao obter canteiros: {e}')
        return []

def get_culturas_list():
    """Obtém a lista de culturas do banco de dados para o formulário."""
    try:
        with get_db() as conn:
            cursor = conn.execute("SELECT id, nome FROM cultura")
            return cursor.fetchall()
    except sqlite3.Error as e:
        flash(f'Erro ao obter culturas: {e}', 'danger')
        print(f'Erro ao obter culturas: {e}')
        return []

@app.route('/movimentacoes', methods=['GET', 'POST'])
def movimentacoes():
    """Página para listar e registrar movimentações."""
    try:
        if request.method == 'POST':
            tipo_produto = request.form.get('tipo_produto')
            produto = request.form.get('produto')
            setores = request.form.getlist('setor')
            canteiros_str = request.form.getlist('canteiro') # Recebe como string
            data = request.form.get('data')
            cultura_id = request.form.get('cultura_id')
            quantidade = request.form.get('quantidade')
            unidade_medida = request.form.get('unidade_medida')

            canteiros = [int(c) for c in canteiros_str if c != 'todos'] # Converte para inteiros

            if 'todos' in setores:
                setores_data = get_setores()
                setores = [setor['id'] for setor in setores_data]

            if 'todos' in canteiros_str:
                canteiros_data = get_canteiros()
                canteiros = [canteiro for canteiro in canteiros_data if canteiro is not None]

            with get_db() as conn:
                cursor = conn.cursor()
                for setor_id in setores:
                    for canteiro_num in canteiros:
                        cursor.execute("""
                            INSERT INTO movimentacao (tipo_produto, produto, setor, canteiro, data, cultura_id, quantidade, unidade_medida)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (tipo_produto, produto, setor_id, canteiro_num, data, cultura_id, quantidade, unidade_medida))
                conn.commit()

            flash('Movimentação registrada com sucesso!', 'success')
            return redirect(url_for('movimentacoes'))

        setores = get_setores()
        canteiros = get_canteiros()
        culturas = get_culturas_list()
        classes = ['Fungicida', 'Inseticida', 'Herbicida', 'Fertilizante', 'Adjuvante']
        defensivos = get_defensivos()

        return render_template('movimentacoes.html',
                               active_page='movimentacoes',
                               now=datetime.now(),
                               setores=setores,
                               canteiros=canteiros,
                               culturas=culturas,
                               defensivos=defensivos,
                               classes=classes)
    except Exception as e:
        print(f"Erro na rota /movimentacoes: {e}")
        return render_template('movimentacoes.html', error=str(e))

@app.route('/cadastros')
def cadastros():
    """Página inicial de cadastros com opções."""
    setores = get_setores()
    return render_template('cadastros.html', active_page='cadastros', now=datetime.now(), setores=setores)

@app.route('/adicionar_cultura', methods=['POST'])
def adicionar_cultura():
    """Rota para adicionar uma nova cultura."""
    nome = request.form.get('nome')
    ciclo = request.form.get('ciclo')
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO cultura (nome, ciclo) VALUES (?, ?)", (nome, ciclo))
            conn.commit()
        flash("Cultura adicionada com sucesso!", "success")
    except sqlite3.Error as e:
        flash(f"Erro ao adicionar cultura: {e}", "danger")
        return redirect(url_for('cadastros'))

    flash("Cultura adicionada com sucesso!", "success")
    return redirect(url_for('culturas'))

@app.route('/adicionar_canteiro', methods=['POST'])
def adicionar_canteiro():
    numero = request.form.get('canteiro_numero')
    setor_id = request.form.get('setor_id')
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO canteiro (canteiro_numero, setor_id) VALUES (?, ?)", (numero, setor_id))
            conn.commit()
        flash("Canteiro adicionado com sucesso!", "success")
    except sqlite3.Error as e:
        flash(f"Erro ao adicionar canteiro: {e}", "danger")
    return redirect(url_for('cadastros'))

@app.route('/adicionar_setor', methods=['POST'])
def adicionar_setor():
    nome = request.form.get('nome')
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO setor (nome) VALUES (?)", (nome,))
            conn.commit()
        flash("Setor adicionado com sucesso!", "success")
    except sqlite3.Error as e:
        flash(f"Erro ao adicionar setor: {e}", "danger")
    return redirect(url_for('cadastros'))

@app.route('/adicionar_defensivo', methods=['POST'])
def adicionar_defensivo():
    nome_comercial = request.form.get('nome_comercial')
    classe = request.form.get('classe')
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO defensivo (nome_comercial, classe) VALUES (?, ?)", (nome_comercial, classe))
            conn.commit()
        flash("Defensivo adicionado com sucesso!", "success")
    except sqlite3.Error as e:
        flash(f"Erro ao adicionar defensivo: {e}", "danger")
    return redirect(url_for('cadastros'))

@app.route('/adicionar_doenca_praga', methods=['POST'])
def adicionar_doenca_praga():
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    descricao = request.form.get('descricao')
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO doenca_praga (nome, tipo, descricao) VALUES (?, ?, ?)", (nome, tipo, descricao))
            conn.commit()
        flash("Doença/Praga adicionada com sucesso!", "success")
    except sqlite3.Error as e:
        flash(f"Erro ao adicionar Doença/Praga: {e}", "danger")
    return redirect(url_for('cadastros'))

@app.route('/relatorios')
def relatorios():
    """Página para listar todos os relatórios"""
    return render_template('relatorios.html', active_page='relatorios', now=datetime.now())

@app.route('/produtos/<classe>')
def produtos_por_classe(classe):
    """Retorna os produtos da classe selecionada em formato JSON."""
    defensivos = get_defensivos(classe)
    return jsonify([{'id': d['id'], 'nome_comercial': d['nome_comercial'], 'classe': d['classe']} for d in defensivos])

@app.route('/culturas/ativos')
def listar_cenario_culturas():
    """Página para listar o cenário atual das culturas (ativos em local_cultura)."""
    try:
        with get_db() as conn:
            locais_ativos = conn.execute('''
                SELECT
                    lc.id AS local_id,
                    c.nome AS cultura_nome,
                    s.nome AS setor_nome,
                    can.canteiro_numero AS canteiro_numero,
                    lc.data_plantio,
                    lc.data_prevista_colheita
                FROM local_cultura lc
                JOIN cultura c ON lc.cultura_id = c.id
                LEFT JOIN setor s ON lc.setor_id = s.id
                LEFT JOIN canteiro can ON lc.canteiro_id = can.id
                WHERE lc.ativo = 1
            ''').fetchall()
        return render_template('cultura_ativos.html', active_page='cultura', locais=locais_ativos, now=datetime.now())
    except sqlite3.Error as e:
        flash(f"Erro ao buscar cenário de culturas: {e}", "danger")
        return render_template('cultura_ativos.html', active_page='cultura', locais=[], now=datetime.now())

@app.route('/cultura_detalhes/<int:id>')
def cultura_detalhes(id):
    try:
        with get_db() as conn:
            cultura = conn.execute("SELECT id, nome, ciclo FROM cultura WHERE id = ?", (id,)).fetchone()
            locais_cultura = conn.execute("""
                SELECT
                    lc.id AS local_id,
                    lc.data_plantio,
                    lc.data_prevista_colheita,
                    lc.ativo,
                    s.id AS setor_id,
                    s.nome AS setor_nome,
                    c.id AS canteiro_id,
                    c.canteiro_numero
                FROM local_cultura lc
                JOIN setor s ON lc.setor_id = s.id
                JOIN canteiro c ON lc.canteiro_id = c.id
                WHERE lc.cultura_id = ?
                ORDER BY lc.data_plantio DESC
            """, (id,)).fetchall()

            if cultura:
                return render_template('cultura_detalhes.html', cultura=cultura, locais_cultura=locais_cultura, now=datetime.now())
            else:
                flash("Cultura não encontrada.", "danger")
                return redirect(url_for('culturas'))
    except sqlite3.Error as e:
        flash(f"Erro ao buscar detalhes da cultura: {e}", "danger")
        return redirect(url_for('culturas'))

if __name__ == '__main__':
    # Verifica se o banco de dados existe, senão inicializa
    if not os.path.exists(app.config['DATABASE']):
        init_db()
        print("✅ Banco de dados criado e inicializado.")
    else:
        print("✅ Banco de dados existente.")
    print("✅ Templates:", app.template_folder)
    print("✅ Static files:", app.static_folder)
    print("✅ Database file:", app.config['DATABASE'])
    app.run(debug=True)