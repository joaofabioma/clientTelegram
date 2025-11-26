# ./main.py
import asyncio
from telethon import TelegramClient
from config import config, db_config, app_shortname
from config.postgres_session import PostgresSession
from telethon.errors import RPCError

async def main():
    session = PostgresSession(config["session"], db_config)
    client = TelegramClient(session, config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"], password=config["phpass"])


    await client.send_message('me', f"Logado como: {app_shortname}")
    print("Iniciado e aguardando mensagens...")

    await client.run_until_disconnected()

try:
    asyncio.run(main())
except RPCError as e:
    print(f"Erro na conexão com o Telegram: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")

