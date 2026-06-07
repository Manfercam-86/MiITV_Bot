import os
from flask import Flask
from threading import Thread
from telegram.ext import Application, MessageHandler, filters
import asyncio

app = Flask(__name__)

# Servidor web mínimo para que Render no dé error de puerto
@app.route('/')
def home():
    return "Bot activo"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Aquí iría toda tu lógica del bot (la de Playwright o la que prefieras)
# ... (tu código del bot aquí) ...

if __name__ == '__main__':
    # Arranca el servidor web en segundo plano
    t = Thread(target=run_web)
    t.start()
    
    # Arranca el bot
    # (aquí tu código para iniciar el bot de Telegram)
    
