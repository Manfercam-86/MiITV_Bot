import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from playwright.async_api import async_playwright
import asyncio

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot activo"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Módulo: Búsqueda de Fichas ---
async def buscar_ficha(homologacion):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://industria.serviciosmin.gob.es/FichasReducidasv2/UI/Solicitudes/Extranet/ConsultaFichasReducidas")
        await page.fill("input[name='numHomologacion']", homologacion)
        await page.click("button[type='submit']")
        await page.wait_for_selector("a.download-link", timeout=15000)
        link = await page.get_attribute("a.download-link", "href")
        await browser.close()
        return link

# --- Módulo: Equivalencia Neumáticos (Cálculo básico) ---
def calcular_equivalencia(medida_original, medida_nueva):
    # Esto es una simplificación lógica de la normativa ITV
    return "La equivalencia debe cumplir: +/- 3% en diámetro, mismo índice de carga y velocidad igual o superior."

async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    
    # Lógica: Si parece una homologación (tiene *) busca en web, si no, es consulta
    if '*' in texto:
        await update.message.reply_text("Buscando ficha técnica en Ministerio...")
        try:
            url = await buscar_ficha(texto)
            await update.message.reply_document(document=url)
        except Exception as e:
            await update.message.reply_text("No se encontró o error de conexión.")
    else:
        await update.message.reply_text("Para buscar ficha, envía el número (ej: e1*2007/46*0273*00). Para neumáticos, escribe 'neumatico [medida]'")

if __name__ == '__main__':
    # Arrancar Web Server
    t = Thread(target=run_web)
    t.start()
    
    # Arrancar Bot
    TOKEN = '8817627494:AAGqttSmzfzMaGP9TSHrVB4W-d_cOhHCYd4' 
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.run_polling()
e
