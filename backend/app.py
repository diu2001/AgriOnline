import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify, request

# =============================================
# CONFIGURAÇÃO INICIAL
# =============================================
app = Flask(__name__)

# Configura caminhos ABSOLUTOS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.template_folder = os.path.abspath(os.path.join(BASE_DIR, '../frontend/templates'))
app.static_folder = os.path.abspath(os.path.join(BASE_DIR, '../frontend/static'))


# =============================================
# BANCO DE DADOS (Sistema Agrícola)
# =============================================
def get_db():
    """Cria conexão com o banco SQLite"""
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'agricultura.db'))
    conn.row_factory = sqlite3.Row  # Retorna dicionários
    return conn


def init_db():
    """Inicializa tabelas se não existirem"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS culturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                dias_colheita INTEGER DEFAULT 30
            );

            CREATE TABLE IF NOT EXISTS canteiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setor_numero INTEGER NOT NULL,
                canteiro_numero INTEGER NOT NULL,
                cultura_id INTEGER REFERENCES culturas(id)
            );

            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT CHECK(tipo IN ('Plantio', 'Colheita', 'Aplicação')),
                data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                cultura_id INTEGER REFERENCES culturas(id)
            );

            CREATE TABLE IF NOT EXISTS defensivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_comercial TEXT NOT NULL
            );
        """)
        conn.commit()


# =============================================
# ROTAS PRINCIPAIS (Frontend)
# =============================================
@app.route('/')
def index():
    """Página inicial com dashboard"""
    with get_db() as conn:
        culturas = conn.execute("""
            SELECT 
                c.nome,
                ct.setor_numero,
                ct.canteiro_numero,
                (c.dias_colheita - (julianday('now') - julianday(m.data))) AS dias_restantes
            FROM culturas c
            LEFT JOIN canteiros ct ON c.id = ct.cultura_id
            LEFT JOIN movimentacoes m ON m.cultura_id = c.id AND m.tipo = 'Plantio'
            WHERE ct.cultura_id IS NOT NULL
            ORDER BY dias_restantes ASC
        """).fetchall()

        return render_template('index.html',
                               culturas_ativas=culturas,
                               now=datetime.now())


@app.route('/cadastros')
def cadastros():
    """Página de cadastros"""
    return render_template('cadastros.html')


@app.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')


# =============================================
# API (Para o calendário)
# =============================================
@app.route('/api/culturas-ativas')
def api_culturas_ativas():
    """Endpoint que fornece dados para o calendário"""
    with get_db() as conn:
        try:
            culturas = conn.execute("""
                SELECT 
                    c.nome,
                    c.dias_colheita,
                    ct.setor_numero AS setor,
                    ct.canteiro_numero AS canteiro,
                    m.data AS data_plantio,
                    d.nome_comercial AS defensivo,
                    (c.dias_colheita - (julianday('now') - julianday(m.data))) AS dias_restantes
                FROM culturas c
                JOIN canteiros ct ON ct.cultura_id = c.id
                JOIN movimentacoes m ON m.cultura_id = c.id AND m.tipo = 'Plantio'
                LEFT JOIN defensivos d ON (
                    SELECT defensivo_recomendado_id FROM doencas_pragas 
                    WHERE cultura_afetada_id = c.id LIMIT 1
                ) = d.id
                WHERE ct.cultura_id IS NOT NULL
            """).fetchall()

            return jsonify([dict(row) for row in culturas])

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# =============================================
# ROTAS AUXILIARES (Arquivos estáticos)
# =============================================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.static_folder, 'img'), 'favicon.ico')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve todos os arquivos estáticos"""
    return send_from_directory(app.static_folder, filename)


# =============================================
# INICIALIZAÇÃO DO SISTEMA
# =============================================
if __name__ == '__main__':
    # Verificação de pastas
    print(f"✅ Templates: {app.template_folder}")
    print(f"✅ Static files: {app.static_folder}")

    # Banco de dados
    if not os.path.exists(os.path.join(BASE_DIR, 'agricultura.db')):
        open(os.path.join(BASE_DIR, 'agricultura.db'), 'w').close()
        print("✅ Banco de dados criado")

    init_db()

    # Inicia o servidor
    print("🚀 Servidor iniciado em http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)