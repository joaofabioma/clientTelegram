from dotenv import load_dotenv, find_dotenv
import os
import config.libs as libs

path_dotenv = find_dotenv()
if path_dotenv:
    # override=True garante que valores do .env sobrescrevam os do ambiente
    load_dotenv(path_dotenv, override=True)
    print(f"{libs.horaagora()} - ✅ Arquivo .env carregado de: {path_dotenv}")
else:
    print(f"{libs.horaagora()} - ℹ️  Arquivo .env não encontrado, usando variáveis de ambiente")

db_host_env = os.getenv("DB_CONFIG_HOST")
db_port_env = int(os.getenv("DB_CONFIG_PORT"))

if db_host_env:
    print(f"{libs.horaagora()} - 🔍 DB_CONFIG_HOST encontrado: {db_host_env}")
else:
    print(f"{libs.horaagora()} - ⚠️  DB_CONFIG_HOST não encontrado nas variáveis de ambiente!")

if db_port_env:
    print(f"{libs.horaagora()} - 🔍 DB_CONFIG_PORT encontrado: {db_port_env}")
else:
    print(f"{libs.horaagora()} - ⚠️  DB_CONFIG_PORT não encontrado nas variáveis de ambiente!")

config = {
    "api_id": os.getenv("APP_IP"),
    "api_hash": os.getenv("API_HASH"),
    "session": os.getenv("SESSION_NAME"),
    "phone": os.getenv("PHONE_NUMBER"),
    "phpass": os.getenv("TEL_PASSWORD"),
}

# Remove valores None do db_config para evitar que psycopg2 use "localhost" como padrão
_db_config_raw = {
    "dbname": os.getenv("DB_CONFIG_DBNAME"),
    "user": os.getenv("DB_CONFIG_USER"),
    "password": os.getenv("DB_CONFIG_PASSWORD"),
    "host": os.getenv("DB_CONFIG_HOST"),
    "port": int(os.getenv("DB_CONFIG_PORT"))
}

# Filtra apenas valores não-None e converte port para int se existir
db_config = {}
for k, v in _db_config_raw.items():
    if v is not None:
        if k == "port":
            try:
                db_config[k] = int(v)
            except (ValueError, TypeError):
                print(f"{libs.horaagora()} - ⚠️  Aviso: Porta inválida '{v}', ignorando...")
        else:
            db_config[k] = v

# Validação crítica: host deve estar sempre definido
if 'host' not in db_config or not db_config.get('host') or db_config.get('host') == '':
    print(f"{libs.horaagora()} - ❌ ERRO CRÍTICO: DB_CONFIG_HOST não está definido ou está vazio!")
    print(f"{libs.horaagora()} -    O psycopg2 usaria 'localhost' como padrão, o que causará erros de conexão.")
    print(f"{libs.horaagora()} -    Variáveis de ambiente disponíveis: {[k for k in os.environ.keys() if 'DB_CONFIG' in k]}")
    # Não definimos um host padrão, deixamos vazio para forçar o erro
else:
    # Garante que host não seja "localhost" a menos que explicitamente definido
    host_value = db_config.get('host', '').strip()
    if host_value.lower() == 'localhost' and os.getenv("DB_CONFIG_HOST", "").strip().lower() != 'localhost':
        print(f"{libs.horaagora()} - ⚠️  AVISO: Host está definido como 'localhost', mas DB_CONFIG_HOST={os.getenv('DB_CONFIG_HOST')}")
        print(f"{libs.horaagora()} -    Isso pode causar problemas de conexão em containers Docker.")

# Log da configuração (sem mostrar senha)
if db_config:
    db_config_log = {k: ("***" if k == "password" else v) for k, v in db_config.items()}
    print(f"{libs.horaagora()} - 📊 Configuração do banco de dados: {db_config_log}")
    if 'port' in db_config:
        print(f"{libs.horaagora()} - 🔍 Porta do banco de dados: {db_config['port']} (tipo: {type(db_config['port']).__name__})")
else:
    print(f"{libs.horaagora()} - ⚠️  Aviso: Nenhuma configuração de banco de dados encontrada!")


def get_db_config():
    """
    Retorna a configuração do banco de dados processada e validada.
    Esta função garante que sempre retornamos uma cópia independente e válida.
    """
    return get_db_config_copy()


def get_db_config_copy():
    """
    Retorna uma cópia do db_config válido.
    Esta função garante que sempre retornamos uma cópia independente e válida.
    """
    # Recarrega as variáveis de ambiente para garantir valores atualizados
    # (útil quando há múltiplos processos importando o módulo)
    _db_config_raw = {
        "dbname": os.getenv("DB_CONFIG_DBNAME"),
        "user": os.getenv("DB_CONFIG_USER"),
        "password": os.getenv("DB_CONFIG_PASSWORD"),
        "host": os.getenv("DB_CONFIG_HOST"),
        "port": int(os.getenv("DB_CONFIG_PORT"))
    }

    # Cria uma nova cópia do db_config
    config_copy = {}
    for k, v in _db_config_raw.items():
        if v is not None:
            if k == "port":
                try:
                    config_copy[k] = int(v)
                except (ValueError, TypeError):
                    print(f"{libs.horaagora()} - ⚠️  Aviso: Porta inválida '{v}', ignorando...")
            else:
                config_copy[k] = v

    # Validação final
    if 'host' not in config_copy or not config_copy.get('host') or config_copy.get('host').strip() == '':
        raise ValueError("❌ DB_CONFIG_HOST não está definido ou está vazio!")

    host_val = str(config_copy.get('host', '')).strip()
    if host_val.lower() == 'localhost':
        raise ValueError(f"❌ Host não pode ser 'localhost'. DB_CONFIG_HOST deve ser um IP ou hostname válido. Recebido: '{host_val}'")

    return config_copy.copy()  # Retorna uma cópia para evitar modificações acidentais

db_url = {
    "urlpg": os.getenv("DATABASE_URL")
}

app_shortname=os.getenv("SHORTNAME")
app_title=os.getenv("APP_TITLE")
