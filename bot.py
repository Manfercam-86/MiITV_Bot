import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

TOKEN = '8817627494:AAGqttSmzfzMaGP9TSHrVB4W-d_cOhHCYd4'

async def buscar_ficha_en_web(homologacion):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Navegamos a la web
        await page.goto("https://industria.serviciosmin.gob.es/FichasReducidasv2/UI/Solicitudes/Extranet/ConsultaFichasReducidas")
        
        # Escribir el número en el campo de búsqueda (ajusta el selector si es necesario)
        await page.fill("input[name='numHomologacion']", homologacion) # Esto es un ejemplo de selector
        await page.click("button[type='submit']")
        
        # Esperar a que aparezca el enlace de descarga
        await page.wait_for_selector("a.download-link") # Selector del botón de descarga
        link = await page.get_attribute("a.download-link", "href")
        
        await browser.close()
        return link

async def procesar_mensajes_y_fichas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buscando en el Ministerio, espera un momento...")
    try:
        url_pdf = await buscar_ficha_en_web(update.message.text.strip())
        await update.message.reply_document(document=url_pdf)
    except Exception as e:
        await update.message.reply_text(f"No he podido descargarla automáticamente: {str(e)}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensajes_y_fichas))
    app.run_polling()
