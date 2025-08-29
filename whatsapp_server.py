from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Token de verificación para el webhook - DESDE VARIABLES DE ENTORNO
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# Token de acceso real de WhatsApp Business API - DESDE VARIABLES DE ENTORNO
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

# ID del número de teléfono de WhatsApp Business - DESDE VARIABLES DE ENTORNO
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')

# ID de la cuenta de WhatsApp Business  
BUSINESS_ACCOUNT_ID = "715070248001249"

# Validar que TODAS las variables de entorno estén configuradas
missing_vars = []
if not ACCESS_TOKEN:
    print("❌ ERROR: ACCESS_TOKEN no está configurado en las variables de entorno")
    print("💡 Configura ACCESS_TOKEN en Render.com → Environment")
    missing_vars.append('ACCESS_TOKEN')
    
if not VERIFY_TOKEN:
    print("❌ ERROR: VERIFY_TOKEN no está configurado en las variables de entorno")
    print("💡 Configura VERIFY_TOKEN en Render.com → Environment")
    missing_vars.append('VERIFY_TOKEN')
    
if not PHONE_NUMBER_ID:
    print("❌ ERROR: PHONE_NUMBER_ID no está configurado en las variables de entorno")
    print("💡 Configura PHONE_NUMBER_ID en Render.com → Environment")
    missing_vars.append('PHONE_NUMBER_ID')

# Evitar que el servidor inicie si faltan variables críticas
if missing_vars:
    print(f"\n🚨 FALLO CRÍTICO: Faltan {len(missing_vars)} variables de entorno obligatorias")
    print("💡 Configura estas variables en Render.com → Environment:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n⚠️  El servidor NO PUEDE INICIAR sin estas configuraciones")
    exit(1)

# URL base de la API de WhatsApp Business (construida después de validar variables)
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """
    Webhook para recibir eventos de WhatsApp Business API
    """
    if request.method == "GET":
        # Verificación del webhook por parte de Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        print(f"🔍 Verificación webhook: mode={mode}, token={token}")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verificado correctamente")
            return challenge, 200
        else:
            print("❌ Error de verificación del webhook")
            return "Error de verificación", 403
    
    if request.method == "POST":
        # Recibir eventos de WhatsApp
        data = request.json
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n📱 [{timestamp}] Evento WhatsApp recibido:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Procesar mensajes entrantes
        try:
            if "entry" in data:
                for entry in data["entry"]:
                    if "changes" in entry:
                        for change in entry["changes"]:
                            if change.get("field") == "messages":
                                process_message(change["value"])
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
        
        return "Evento recibido", 200

def process_message(message_data):
    """
    Procesa mensajes entrantes de WhatsApp
    """
    try:
        if "messages" in message_data:
            for message in message_data["messages"]:
                sender = message.get("from")
                message_type = message.get("type")
                message_id = message.get("id")
                
                print(f"📩 Mensaje de {sender} (ID: {message_id}, Tipo: {message_type})")
                
                if message_type == "text":
                    text_content = message["text"]["body"]
                    print(f"💬 Contenido: {text_content}")
                    
                    # Aquí puedes agregar lógica para responder automáticamente
                    # send_message(sender, f"Recibido: {text_content}")
                
                elif message_type == "image":
                    print("🖼️ Imagen recibida")
                elif message_type == "document":
                    print("📄 Documento recibido")
                else:
                    print(f"📱 Mensaje tipo: {message_type}")
    
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

@app.route("/send-message", methods=["POST"])
def send_message_endpoint():
    """
    Endpoint para enviar mensajes de WhatsApp
    
    Body JSON esperado:
    {
        "to": "5491234567890",
        "message": "Hola, este es un mensaje de prueba",
        "type": "text"
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionó data JSON"}), 400
        
        to = data.get("to")
        message = data.get("message") 
        message_type = data.get("type", "text")
        
        if not to or not message:
            return jsonify({"error": "Faltan campos 'to' y/o 'message'"}), 400
        
        # Enviar mensaje
        result = send_message(to, message, message_type)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Mensaje enviado correctamente",
                "message_id": result.get("message_id"),
                "to": to
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error"),
                "details": result.get("details")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

def send_message(to, message, message_type="text"):
    """
    Envía un mensaje de WhatsApp usando la API de Meta
    
    Args:
        to (str): Número de teléfono con código de país (ej: "5491234567890")
        message (str): Contenido del mensaje
        message_type (str): Tipo de mensaje ("text", "template", etc.)
    
    Returns:
        dict: Resultado de la operación
    """
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        if message_type == "text":
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
        else:
            return {"success": False, "error": f"Tipo de mensaje '{message_type}' no soportado"}
        
        print(f"📤 Enviando mensaje a {to}: {message}")
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        print(f"📊 Respuesta API: {response.status_code}")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            message_id = response_data.get("messages", [{}])[0].get("id")
            return {
                "success": True,
                "message_id": message_id,
                "response": response_data
            }
        else:
            return {
                "success": False,
                "error": "Error en API de WhatsApp",
                "details": response_data,
                "status_code": response.status_code
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Error enviando mensaje",
            "details": str(e)
        }

@app.route("/", methods=["GET"])
def home():
    """
    Página de inicio con información del servidor
    """
    info = {
        "service": "WhatsApp Business API Webhook",
        "status": "active",
        "endpoints": {
            "webhook": "/webhook (GET/POST)",
            "send_message": "/send-message (POST)",
            "health": "/health (GET)"
        },
        "webhook_verification": {
            "url": request.url_root + "webhook",
            "verify_token": VERIFY_TOKEN[:20] + "..."
        },
        "usage": {
            "send_message": {
                "method": "POST",
                "url": request.url_root + "send-message",
                "body": {
                    "to": "5491234567890",
                    "message": "Hola mundo",
                    "type": "text"
                }
            }
        }
    }
    return jsonify(info)

@app.route("/health", methods=["GET"])
def health():
    """
    Endpoint de salud del servicio
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WhatsApp Webhook"
    })

@app.route("/test-config", methods=["GET"])
def test_config():
    """
    Endpoint para verificar la configuración de WhatsApp Business API
    """
    config_info = {
        "status": "configured",
        "phone_number_id": PHONE_NUMBER_ID,
        "business_account_id": BUSINESS_ACCOUNT_ID,
        "access_token_preview": ACCESS_TOKEN[:20] + "...",
        "verify_token_preview": VERIFY_TOKEN[:20] + "...",
        "api_url": WHATSAPP_API_URL,
        "ready_to_send": True,
        "test_instructions": {
            "1": "Usa POST /send-message para enviar un mensaje",
            "2": "Formato: {\"to\": \"549XXXXXXXXX\", \"message\": \"Hola desde API\"}",
            "3": "El número debe incluir código de país (549 para Argentina)"
        }
    }
    return jsonify(config_info)

@app.route("/test-send", methods=["POST"])
def test_send():
    """
    Endpoint de prueba para enviar un mensaje de test
    
    Body JSON:
    {
        "to": "5491234567890"
    }
    """
    try:
        data = request.json
        to = data.get("to") if data else None
        
        if not to:
            return jsonify({
                "error": "Proporciona el número en el body JSON: {\"to\": \"549XXXXXXXXX\"}"
            }), 400
        
        test_message = f"🧪 Mensaje de prueba desde WhatsApp Business API\n⏰ Enviado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n✅ Tu configuración está funcionando correctamente!"
        
        result = send_message(to, test_message)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "¡Mensaje de prueba enviado exitosamente!",
                "to": to,
                "message_id": result.get("message_id"),
                "sent_at": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Error enviando mensaje de prueba",
                "details": result.get("details"),
                "to": to
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Error en test de envío",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Iniciando servidor WhatsApp Business API")
    print("="*50)
    print("🔐 VALIDACIÓN DE SEGURIDAD:")
    print(f"📱 Phone ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Access Token: {'✅ Configurado' if ACCESS_TOKEN and len(ACCESS_TOKEN) > 50 else '❌ Falta configurar'}")
    print(f"🔐 Verify Token: {'✅ Configurado' if VERIFY_TOKEN and len(VERIFY_TOKEN) > 20 else '❌ Falta configurar'}")
    print("="*50)
    
    if not ACCESS_TOKEN or not VERIFY_TOKEN:
        print("❌ ADVERTENCIA: Variables de entorno faltantes!")
        print("💡 Para usar en Render.com:")
        print("   1. Ir a tu servicio en Render → Environment")
        print("   2. Agregar ACCESS_TOKEN con tu token de Meta")
        print("   3. Agregar VERIFY_TOKEN con tu token de verificación")
        print("   4. Agregar PHONE_NUMBER_ID si es diferente al default")
        print("="*50)
    
    print(f"📱 Webhook URL: http://localhost:5000/webhook")
    print(f"💬 Send Message URL: http://localhost:5000/send-message")
    print("\n⚠️  IMPORTANTE:")
    print("1. Todas las credenciales se obtienen de variables de entorno")
    print("2. Para producción, usa HTTPS (Render, Heroku, etc.)")
    print("3. Nunca hardcodees tokens en el código")
    
    # Puerto desde variable de entorno (Render usa PORT)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
