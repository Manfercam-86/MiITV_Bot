import os
import re
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Token de tu bot de Telegram ya configurado
TOKEN = '8817627494:AAH2zf8J9YepY2kRDtRnJl54SOK7g5c6AVQ'

def calcular_equivalencia(medida_original, medida_nueva):
    try:
        orig_clean = re.sub(r'[-_\s/rR]', '', medida_original)
        nuev_clean = re.sub(r'[-_\s/rR]', '', medida_nueva)
        patron = r"^(\d{3})(\d{2})(\d{2})$"
        orig = re.match(patron, orig_clean)
        nuev = re.match(patron, nuev_clean)
        if not orig or not nuev: return "💡 Formato no reconocido. Ej: `205/55R16`"
        w1, p1, r1 = map(float, orig.groups())
        w2, p2, r2 = map(float, nuev.groups())
        d1 = (r1 * 25.4) + (2 * w1 * p1 / 100)
        d2 = (r2 * 25.4) + (2 * w2 * p2 / 100)
        dif = ((d2 - d1) / d1) * 100
        res = f"📊 **CÁLCULO DE EQUIVALENCIA**\n▪️ Original: {medida_original.upper()} ({d1:.2f} mm)\n▪️ Nueva: {medida_nueva.upper()} ({d2:.2f} mm)\n▪️ Dif: {dif:+.2f}%\n\n"
        if abs(dif) <= 3.0: res += "✅ **ES EQUIVALENTE**"
        else: res += "❌ **NO ES EQUIVALENTE**"
        return res
    except Exception as e: return f"❌ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 **Sistema ITV Online Activo**\n\n• Envíame la contraseña de homologación directamente.\n• Usa `/neumatico original nueva` para gomas.")

async def neumaticos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2: return
    await update.message.reply_text(calcular_equivalencia(context.args[0], context.args[1]))

async def procesar_mensajes_y_fichas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    if query.lower().startswith(('/neu', '/nea', '/nau', '/naú', '/neú')):
        partes = query.split()
        if len(partes) >= 3: await update.message.reply_text(calcular_equivalencia(partes[1], partes[2]))
        return

    if not re.match(r'^[eE]\d*\*?\d*', query):
        await update.message.reply_text("Formato de contraseña no válido.")
        return
        
    await update.message.reply_text(f"🌐 Servidor Online conectando con el Ministerio para: {query}...")
    
    op = Options()
    op.add_argument('--headless')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')
    
    directorio_descargas = os.getcwd()
    prefs = {"download.default_directory": directorio_descargas, "plugins.always_open_pdf_externally": True}
    op.add_experimental_option("prefs", prefs)
    
    dr = None
    try:
        url_raiz = "https://industria.serviciosmin.gob.es/FichasReducidasv2/"
        dr = webdriver.Chrome(options=op)
        dr.get(url_raiz)
        
        wait = WebDriverWait(dr, 35)
        
        # 1. Clic en Consulta de fichas reducidas
        link_consulta = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Consulta de fichas reducidas')]")))
        dr.execute_script("arguments[0].click();", link_consulta)
        time.sleep(5)
        
        # 2. Desplegar la pestaña Filtros
        filtros_header = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ui-accordion-header') or contains(text(), 'Filtros')]")))
        dr.execute_script("arguments[0].click();", filtros_header)
        time.sleep(2)
        
        # 3. Rellenar la contraseña
        input_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'txtContrasenaHomologacion')]")))
        input_box.clear()
        input_box.send_keys(query)
        
        # 4. Clic en Buscar
        btn_buscar = dr.find_element(By.XPATH, "//input[contains(@id, 'btnBuscar')]")
        dr.execute_script("arguments[0].click();", btn_buscar)
        time.sleep(8)
        
        if "gvdFichasReducidas" in dr.page_source:
            enlaces = dr.find_elements(By.XPATH, "//a[contains(@href, 'gvdFichasReducidas') or contains(@href, 'Select')]")
            if enlaces:
                dr.execute_script("arguments[0].click();", enlaces[0])
                time.sleep(5)
                
                enlaces_pdf = dr.find_elements(By.XPATH, "//a[contains(@href, 'gvdDocumentos') or contains(@href, 'Select')]")
                if enlaces_pdf:
                    archivos_antes = os.listdir(directorio_descargas)
                    dr.execute_script("arguments[0].click();", enlaces_pdf[0])
                    time.sleep(12)
                    
                    archivo_descargado = None
                    for f in os.listdir(directorio_descargas):
                        if f.lower().endswith('.pdf') and f not in archivos_antes:
                            archivo_descargado = f
                            break
                            
                    if archivo_descargado:
                        nombre_itv = f"Ficha_{query.replace('/', '_').replace('*', '_')}.pdf"
                        os.rename(archivo_descargado, nombre_itv)
                        with open(nombre_itv, 'rb') as doc:
                            await update.message.reply_document(document=doc, filename=nombre_itv, caption=f"✅ Ficha para: `{query}`")
                        os.remove(nombre_itv)
                    else:
                        await update.message.reply_text("❌ El expediente se abrió bien, pero el PDF tardó demasiado en responder.")
                else:
                    await update.message.reply_text("❌ No se encontró el botón físico para bajar el PDF.")
            else:
                await update.message.reply_text("❌ No se pudo expandir la fila del Ministerio.")
        else:
            await update.message.reply_text("❌ Sin resultados en el Ministerio para esta contraseña.")
    except Exception as e:
        await update.message.reply_text(f"❌ Fallo en el servidor: {str(e)}")
    finally:
        if dr: dr.quit()

if __name__ == '__main__':
    print("Bot Servidor Online Iniciado.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('neumatico', neumaticos_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensajes_y_fichas))

    from flask import Flask
import threading
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot vivo"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Esto arranca el servidor falso en segundo plano para engañar a Render
threading.Thread(target=run).start()
app.run_polling()
