import psycopg2
from telethon.sessions import MemorySession
import pickle

class PostgresSession(MemorySession):
    def __init__(self, session_name, db_config):
        super().__init__()
        self.session_name = session_name
        self.db_config = db_config
        self._load_session()

    def _connect(self):
        return psycopg2.connect(**self.db_config)

    def _load_session(self):
        """Carrega a sessão do PostgreSQL."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT session_data FROM telegram_sessions WHERE session_name = %s", (self.session_name,))
                row = cur.fetchone()
                if row and row[0]:
                    try:
                        self._set_state(pickle.loads(row[0]))
                    except Exception as e:
                        print(f"Erro ao carregar sessão: {e}")
                        self._set_state({})
                else:
                    self._set_state({})

    def _set_state(self, state):
        """Define o estado da sessão carregada do PostgreSQL."""
        self.__dict__.update(state)

    def save(self):
        """Salva a sessão no PostgreSQL."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                serialized_state = pickle.dumps(self.__dict__, protocol=pickle.HIGHEST_PROTOCOL)
                cur.execute("""
                    INSERT INTO telegram_sessions (session_name, session_data)
                    VALUES (%s, %s)
                    ON CONFLICT (session_name) 
                    DO UPDATE SET session_data = EXCLUDED.session_data, 
                        updated_at = EXCLUDED.updated_at
                """, (self.session_name, serialized_state))  # Salvando como bytes
                conn.commit()