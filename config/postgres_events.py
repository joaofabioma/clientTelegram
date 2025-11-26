import psycopg2
import pickle

class PostgresEvents():
    def __init__(self, session_name, db_config):
        super().__init__()
        self.session_name = session_name
        self.db_config = db_config
    
    def _connect(self):
        return psycopg2.connect(**self.db_config)
    
    def save_event(self, event):
        """Salva um evento bruto no banco de dados."""
        # self._set_last_event(event)
        with self._connect() as conn:
            with conn.cursor() as cur:
                serialized_event = pickle.dumps(event, protocol=pickle.HIGHEST_PROTOCOL)
                cur.execute("""
                    INSERT INTO telegram_events (event_data) VALUES (%s)
                """, (serialized_event,))
                conn.commit()
    
    def load_events(self):
        """Carrega eventos salvos do banco de dados."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT event_data FROM telegram_events")
                rows = cur.fetchall()
                return [pickle.loads(row[0]) for row in rows]
    
    def _set_last_event(self, event):
        """Define o ultimo evento salvo no PostgreSQL."""
        self.__dict__.update(event)
    
    def load_event_last(self):
        """Carrega ultimo evento salvo no banco de dados."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT event_data FROM telegram_events ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                if row and row[0]:
                    try:
                        self._set_state(pickle.loads(row[0]))
                    except Exception as e:
                        print(f"Erro ao carregar ultimo evento: {e}")
                        self._set_state({})
                else:
                    self._set_state({})