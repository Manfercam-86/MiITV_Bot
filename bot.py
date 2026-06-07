import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token de tu bot
TOKEN = '8817627494:AAH2zf8J9YepY2kRDtRnJl54SOK7g5c6AVQ'

# --- DEFINICIÓN DE FUNCIONES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot iniciado correctamente.")

async def neumaticos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comando de neumáticos.")

# Nombre exacto corregido para que coincida con el manejador
async def procesar_mensajes_y_fichas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    # Cambia 'fichas' por el nombre de tu carpeta si no están en la raíz
    ruta_carpeta = '.' 
    
    encontrado = False
    
    # Busca en todos los archivos de la carpeta
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith('.pdf') and user_text in archivo.lower():
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            await update.message.reply_document(document=open(ruta_completa, 'rb'))
            encontrado = True
            break # Sale al encontrar la primera coincidencia
            
    if not encontrado:
        await update.message.reply_text("No he encontrado ninguna ficha que coincida con ese nombre.")
    

# --- CONFIGURACIÓN PRINCIPAL ---
if __name__ == '__main__':
    print("Iniciando Bot...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('neumatico', neumaticos_command))
    
    # Aquí usamos el nombre exacto de la función definida arriba
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensajes_y_fichas))
    
    # Servidor falso para Render
    flask_app = Flask('')
    @flask_app.route('/')
    def home():
        return "Bot vivo"

    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host='0.0.0.0', port=port)

    threading.Thread(target=run_flask).start()

    # Arrancar Telegram
    app.run_polling()
