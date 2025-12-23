from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sys
import os
import pickle
import json
from config import libs
from config.db import DB_CONFIG

# Adiciona o diretório pai ao path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_db_config
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Configurações de produção
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_ENV', 'production') == 'development'
app.config['TESTING'] = False

# Configuração do secret key para sessões
secret_key = os.getenv('FLASK_SECRET_KEY', None)
if not secret_key:
    # Gera uma chave secreta padrão se não estiver definida (não recomendado para produção)
    secret_key = os.urandom(24).hex()
    print(f"{libs.horaagora()} - ⚠️  AVISO: FLASK_SECRET_KEY não definido. Usando chave gerada automaticamente.")
    print(f"{libs.horaagora()} -    Configure FLASK_SECRET_KEY nas variáveis de ambiente para produção.")
app.config['SECRET_KEY'] = secret_key

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Classe User para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def verify_credentials(username: str, password: str) -> bool:
    """Verifica as credenciais do usuário."""
    # Obtém credenciais das variáveis de ambiente
    env_username = os.getenv('FLASK_ADMIN_USERNAME', 'master')
    env_password = os.getenv('FLASK_ADMIN_PASSWORD', 'S&gred0')

    if not env_password:
        print(f"{libs.horaagora()} - ⚠️  AVISO: FLASK_ADMIN_PASSWORD não definido. Usando senha padrão 'master'.")
        print(f"{libs.horaagora()} -    Configure FLASK_ADMIN_PASSWORD nas variáveis de ambiente para produção.")
        env_password = 'admin'

    # Verifica se o usuário e senha correspondem
    print(username ,env_username ,password,env_password)
    if username == env_username and password == env_password:
        return True
    return False

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    # Tenta obter uma configuração validada
    try:
        db_config_validated = get_db_config()
    except Exception as e:
        print(f"{libs.horaagora()} - ❌ Erro ao obter DB_CONFIG validado: {e}")
        db_config_validated = DB_CONFIG.copy() if isinstance(DB_CONFIG, dict) else {}
        if 'host' not in db_config_validated or not db_config_validated.get('host'):
            print(f"{libs.horaagora()} - ❌ Erro: DB_CONFIG_HOST não está definido! O psycopg2 usaria 'localhost' como padrão.")
            print(f"{libs.horaagora()} -    DB_CONFIG disponível: {list(db_config_validated.keys())}")
            return None

        # Validação adicional: host não pode ser localhost
        host_value = str(db_config_validated.get('host', '')).strip()
        if not host_value or host_value == 'localhost':
            print(f"{libs.horaagora()} - ❌ Host inválido: '{host_value}'. Verifique DB_CONFIG_HOST nas variáveis de ambiente.")
            print(f"{libs.horaagora()} -    DB_CONFIG completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in db_config_validated.items())}")
            return None

    try:
        conn = psycopg2.connect(**db_config_validated)
        return conn
    except psycopg2.OperationalError as e:
        print(f"{libs.horaagora()} - ❌ Erro ao conectar ao PostgreSQL: {e}")
        print(f"{libs.horaagora()} - app.py:   Configuração: host={db_config_validated.get('host')}, port={db_config_validated.get('port')}, dbname={db_config_validated.get('dbname')}")
        print(f"{libs.horaagora()} -    DB_CONFIG completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in db_config_validated.items())}")
        print(f"{libs.horaagora()} -    Dica: Se estiver usando Docker, verifique se DB_CONFIG_HOST está configurado corretamente")
        return None
    except Exception as e:
        print(f"{libs.horaagora()} - ❌ Erro inesperado ao conectar ao banco de dados: {e}")
        print(f"{libs.horaagora()} -    DB_CONFIG completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in db_config_validated.items())}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if verify_credentials(username, password):
            user = User(username)
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário."""
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Página inicial com dashboard."""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Erro ao conectar ao banco de dados")

    try:
        with conn.cursor() as cur:
            # Estatísticas gerais
            cur.execute("SELECT COUNT(*) FROM telegram_sessions")
            sessions_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM telegram_events")
            events_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM telegram_type_events")
            types_count = cur.fetchone()[0]

            # Últimos eventos por tipo
            cur.execute("""
                SELECT type_name, hits, created_at, updated_at
                FROM telegram_type_events
                ORDER BY hits DESC
                LIMIT 30
            """)
            top_types = cur.fetchall()

            # Eventos recentes
            cur.execute("""
                SELECT id, created_at
                FROM telegram_events
                ORDER BY created_at DESC
                LIMIT 30
            """)
            recent_events = cur.fetchall()

        conn.close()

        return render_template('index.html',
                             sessions_count=sessions_count,
                             events_count=events_count,
                             types_count=types_count,
                             top_types=top_types,
                             recent_events=recent_events)
    except Exception as e:
        conn.close()
        return render_template('error.html', error=str(e))

@app.route('/sessions')
@login_required
def sessions():
    """Lista todas as sessões do Telegram."""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Erro ao conectar ao banco de dados")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, session_name, created_at, updated_at,
                       LENGTH(session_data) as session_size
                FROM telegram_sessions
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
            """)
            sessions = cur.fetchall()
        conn.close()

        return render_template('sessions.html', sessions=sessions)
    except Exception as e:
        conn.close()
        return render_template('error.html', error=str(e))

@app.route('/events')
@login_required
def events():
    """Lista todos os eventos do Telegram."""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Erro ao conectar ao banco de dados")

    try:
        page = int(request.args.get('page', 1))
        per_page = 50
        offset = (page - 1) * per_page

        with conn.cursor() as cur:
            # Conta total de eventos
            cur.execute("SELECT COUNT(*) FROM telegram_events")
            total = cur.fetchone()[0]

            # Busca eventos paginados
            cur.execute("""
                SELECT id, event_name, created_at, updated_at, deleted_at,
                       LENGTH(event_data) as event_size
                FROM telegram_events
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            events = cur.fetchall()

        conn.close()

        total_pages = (total + per_page - 1) // per_page

        return render_template('events.html',
                             events=events,
                             page=page,
                             total_pages=total_pages,
                             total=total)
    except Exception as e:
        conn.close()
        return render_template('error.html', error=str(e))

@app.route('/event-types')
@login_required
def event_types():
    """Lista todos os tipos de eventos."""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Erro ao conectar ao banco de dados")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, type_name, descricao, hits, created_at, updated_at
                FROM telegram_type_events
                ORDER BY hits DESC, type_name ASC
            """)
            types = cur.fetchall()
        conn.close()

        return render_template('event_types.html', types=types)
    except Exception as e:
        conn.close()
        return render_template('error.html', error=str(e))

@app.route('/event/<int:event_id>')
@login_required
def event_detail(event_id):
    """Visualiza detalhes de um evento específico (deserializado)."""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Erro ao conectar ao banco de dados")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, event_data, created_at, updated_at, deleted_at
                FROM telegram_events
                WHERE id = %s
            """, (event_id,))
            row = cur.fetchone()

            if not row:
                conn.close()
                return render_template('error.html', error=f"Evento #{event_id} não encontrado")

            event_id_db, event_data_bytes, created_at, updated_at, deleted_at = row

            # Deserializa o evento
            try:
                event_data = pickle.loads(event_data_bytes)
                # Converte para formato JSON-serializável
                event_json = _convert_to_json_serializable(event_data)
                # Converte para string JSON formatada
                event_json_str = json.dumps(event_json, indent=2, ensure_ascii=False)
            except Exception as e:
                event_json_str = json.dumps({"error": f"Erro ao deserializar evento: {str(e)}"}, indent=2, ensure_ascii=False)

        conn.close()

        return render_template('event_detail.html',
                             event_id=event_id_db,
                             event_data_json=event_json_str,
                             created_at=created_at,
                             updated_at=updated_at,
                             deleted_at=deleted_at)
    except Exception as e:
        conn.close()
        return render_template('error.html', error=str(e))

def _convert_to_json_serializable(obj):
    """Converte objetos Python para formato JSON-serializável."""
    if isinstance(obj, dict):
        return {k: _convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return str(obj)

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint para estatísticas em JSON."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro ao conectar ao banco de dados"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM telegram_sessions")
            sessions_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM telegram_events")
            events_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM telegram_type_events")
            types_count = cur.fetchone()[0]

            cur.execute("SELECT SUM(hits) FROM telegram_type_events")
            total_hits = cur.fetchone()[0] or 0

        conn.close()

        return jsonify({
            "sessions": sessions_count,
            "events": events_count,
            "types": types_count,
            "total_hits": total_hits
        })
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # produção
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    app.run(debug=debug_mode, host=host, port=port)

