import psycopg2
from telethon.sessions import MemorySession
import pickle
import config.libs as libs

class PostgresSession(MemorySession):
    def __init__(self, session_name, db_config):
        super().__init__()
        self.session_name = session_name
        # Faz uma cópia profunda do db_config para evitar modificações acidentais
        self.db_config = db_config.copy() if isinstance(db_config, dict) else dict(db_config)
        self._load_session()

    def _connect(self):
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.OperationalError as e:
            print(f"{libs.horaagora()} - ❌ Erro ao conectar ao PostgreSQL: {e}")
            print(f"{libs.horaagora()} - psession:   Configuração: host={self.db_config.get('host')}, port={self.db_config.get('port')}, dbname={self.db_config.get('dbname')}")
            print(f"{libs.horaagora()} -    db_config completo (sem senha): {dict((k, '***' if k == 'password' else v) for k, v in self.db_config.items())}")
            raise

    def _load_session(self):
        """Carrega a sessão do PostgreSQL."""
        try:
            with self._connect() as conn:
                print(f"{libs.horaagora()} - Conexão estabelecida com o PostgreSQL!")
                # print(f"Conexão estabelecida com o PostgreSQL: {conn}")
                with conn.cursor() as cur:
                    cur.execute("SELECT session_data FROM telegram_sessions WHERE session_name = %s", (self.session_name,))
                    row = cur.fetchone()
                    if row and row[0]:
                        try:
                            self._set_state(pickle.loads(row[0]))
                        except Exception as e:
                            print(f"{libs.horaagora()} - Erro ao carregar sessão: {e}")
                            self._set_state({})
                    else:
                        self._set_state({})
        except Exception as e:
            print(f"{libs.horaagora()} - ❌ Erro ao carregar sessão do PostgreSQL: {e}")
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
