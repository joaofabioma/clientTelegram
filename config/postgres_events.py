import psycopg2
import pickle
from config.db import DB_CONFIG

class PostgresEvents():
    def __init__(self, session_name):
        super().__init__()
        self.session_name = session_name
        # Faz uma cópia profunda do db_config para evitar modificações acidentais

    def _connect(self):
        # Valida se host está definido (psycopg2 usa "localhost" como padrão se não estiver)
        if 'host' not in DB_CONFIG or not DB_CONFIG.get('host'):
            error_msg = f"❌ DB_CONFIG_HOST não está definido! O psycopg2 usaria 'localhost' como padrão."
            print(error_msg)
            print(f"   db_config recebido: {list(DB_CONFIG.keys())}")
            raise ValueError(error_msg)

        # Validação adicional: host não pode ser localhost a menos que explicitamente necessário
        host_value = str(DB_CONFIG.get('host', '')).strip()
        if not host_value or host_value == 'localhost':
            error_msg = f"❌ Host inválido: '{host_value}'. Verifique DB_CONFIG_HOST nas variáveis de ambiente."
            print(error_msg)
            print(f"   db_config completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in DB_CONFIG.items())}")
            raise ValueError(error_msg)

        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            print(f"events:   Configuração: host={DB_CONFIG.get('host')}, port={DB_CONFIG.get('port')}, dbname={DB_CONFIG.get('dbname')}")
            print(f"   DB_CONFIG completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in DB_CONFIG.items())}")
            raise

    def save_type_event(self, event_type, event_type_desc=""):
        """Salva o tipo do evento no banco de dados."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO telegram_type_events (type_name) VALUES (%s)
                            ON CONFLICT (type_name)
                            DO UPDATE SET
                            hits = telegram_type_events.hits + 1;
                """, (event_type,))
                conn.commit()

    def save_event(self, event):
        """Salva um evento bruto no banco de dados."""
        # self._set_last_event(event)
        with self._connect() as conn:
            with conn.cursor() as cur:
                serialized_event = pickle.dumps(event, protocol=pickle.HIGHEST_PROTOCOL)
                message_id = int(event["message"]) if event["message"] is not None else None

                cur.execute("""
                    INSERT INTO telegram_events (event_data, event_name, event_message_id) VALUES (%s, %s, %s)
                """, (serialized_event, event["type"], message_id))
                conn.commit()

    def load_events(self):
        """Carrega eventos salvos do banco de dados."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT event_data, event_name, event_message_id FROM telegram_events")
                rows = cur.fetchall()
                return [pickle.loads(row[0]) for row in rows]

    def _set_last_event(self, event):
        """Define o ultimo evento salvo no PostgreSQL."""
        self.__dict__.update(event)

    def load_event_last(self):
        """Carrega ultimo evento salvo no banco de dados."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT event_data, event_name, event_message_id FROM telegram_events ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                if row and row[0]:
                    try:
                        self._set_state(pickle.loads(row[0]))
                    except Exception as e:
                        print(f"Erro ao carregar ultimo evento: {e}")
                        self._set_state({})
                else:
                    self._set_state({})
