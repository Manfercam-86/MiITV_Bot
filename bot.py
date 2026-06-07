import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '8817627494:AAH2zf8J9YepY2kRDtRnJl54SOK7g5c6AVQ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot operativo. Envíame el modelo y te buscaré la ficha.")

async def neumaticos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comando de neumáticos.")

# LÓGICA DE BÚSQUEDA CORREGIDA Y DEFINITIVA
async def procesar_mensajes_y_fichas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    ruta_carpeta = '.' 
    encontrado = False
    
    for archivo in os.listdir(ruta_carpeta):
        if archivo.lower().endswith('.pdf') and user_text in archivo.lower():
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            await update.message.reply_document(document=open(ruta_completa, 'rb'))
            encontrado = True
            break 
            
    if not encontrado:
        await update.message.reply_text(f"No encontré nada para '{user_text}'. Asegúrate de que el PDF está subido al repositorio.")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('neumatico', neumaticos_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensajes_y_fichas))
    
    flask_app = Flask('')
    @flask_app.route('/')
    def home():
        return "Bot vivo"

    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host='0.0.0.0', port=port)

    threading.Thread(target=run_flask).start()
    app.run_polling()
