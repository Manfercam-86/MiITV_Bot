 

// --- CONFIGURACIÓN ---
var TOKEN = "8817627494:AAG3kIpEX56BzCrokIOYFovY3Zk2V2yiW4M"; 
var URL_TELEGRAM = "https://api.telegram.org/bot" + TOKEN;

function doPost(e) {
  var contents = JSON.parse(e.postData.contents);
  if (!contents.message || !contents.message.text) return;
  
  var chatId = contents.message.chat.id;
  var text = contents.message.text.trim();
  
  // 1. Lógica de Homologación (Empieza por 'e')
  if (text.toLowerCase().startsWith('e')) {
    var enlace = "https://industria.serviciosmin.gob.es/FichasReducidasv2/UI/Solicitudes/Extranet/ConsultaFichasReducidas";
    var respuesta = "✅ Solicitud recibida.\n\n🔗 Acceso directo: " + enlace + "\n\n📄 Código para copiar: `" + text + "`\n\n_Descarga tu ficha y súbela a Drive para procesarla._";
    
    enviarMensaje(chatId, respuesta);
  } 
  
  // 2. Lógica de Neumáticos (ej: 205/55R16 225/45R17)
  else if (text.includes('/')) {
    var partes = text.split(/[\s,]+/);
    if (partes.length >= 2) {
      enviarMensaje(chatId, calcularEquivalencia(partes[0], partes[1]));
    }
  }
  
  // 3. Comandos base
  else {
    enviarMensaje(chatId, "🤖 *Asistente Activo*\n\nComandos:\n- `e...`: Ficha reducida\n- `205/55R16 225/45R17`: Equivalencia");
  }
}

// --- MÓDULO DE CÁLCULO ---
function calcularEquivalencia(m1, m2) {
  function getDiametro(m) {
    var p = m.match(/(\d+)\/(\d+)R(\d+)/);
    if (!p) return 0;
    return (parseInt(p[1]) * (parseInt(p[2]) / 100) * 2) + (parseInt(p[3]) * 25.4);
  }
  var d1 = getDiametro(m1), d2 = getDiametro(m2);
  if (d1 === 0 || d2 === 0) return "❌ Formato incorrecto.";
  var dif = ((d2 - d1) / d1) * 100;
  return "📏 *Resultado:*\n" + (Math.abs(dif) <= 3 ? "✅ ES EQUIVALENTE" : "❌ NO ES EQUIVALENTE") + 
         "\n(Diferencia: " + dif.toFixed(2) + "%)";
}

// --- MÓDULO DE COMUNICACIÓN ---
function enviarMensaje(chatId, texto) {
  UrlFetchApp.fetch(URL_TELEGRAM + "/sendMessage?chat_id=" + chatId + "&parse_mode=Markdown&text=" + encodeURIComponent(texto));
}
