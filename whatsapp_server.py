from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Token de verificación para el webhook (usando el mismo token de acceso)
VERIFY_TOKEN = "EAAHrpGZBTFTABPWTdO4ntNzYJ9ip6F9ZA4J8ZAjJyUX5XnbZA7PIuK27ALwZCcQF86STCHS9AD523eyWxaWj0pgLYldXD9SnNxszTSTqipeTnoKjvEIb8AWtiOanmLM9PAzgUUB1Lky7BEOmaxGiiUZBtUukDfTkfPKRv7N54JQaORsDPj3xkp83CPzUZCesLcXHZAOqCXxANb0GZB5UPbsFL78McZCBN3r21GDEtiggKBipEFiDJIWaZCTExwxOgZDZD"

# Token de acceso real de WhatsApp Business API
ACCESS_TOKEN = "EAAHrpGZBTFTABPWTdO4ntNzYJ9ip6F9ZA4J8ZAjJyUX5XnbZA7PIuK27ALwZCcQF86STCHS9AD523eyWxaWj0pgLYldXD9SnNxszTSTqipeTnoKjvEIb8AWtiOanmLM9PAzgUUB1Lky7BEOmaxGiiUZBtUukDfTkfPKRv7N54JQaORsDPj3xkp83CPzUZCesLcXHZAOqCXxANb0GZB5UPbsFL78McZCBN3r21GDEtiggKBipEFiDJIWaZCTExwxOgZDZD"

# ID del número de teléfono de WhatsApp Business
PHONE_NUMBER_ID = "629824623553106"

# ID de la cuenta de WhatsApp Business  
BUSINESS_ACCOUNT_ID = "715070248001249"

# URL base de la API de WhatsApp Business
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
    print(f"📱 Webhook URL: http://localhost:5000/webhook")
    print(f"💬 Send Message URL: http://localhost:5000/send-message")
    print(f"🔑 Verify Token: {VERIFY_TOKEN[:20]}...")
    print("\n⚠️  IMPORTANTE:")
    print("1. Configura PHONE_NUMBER_ID con tu ID real de WhatsApp Business")
    print("2. Para producción, usa HTTPS (ngrok, servidor web, etc.)")
    print("3. El ACCESS_TOKEN debe ser válido y tener permisos de WhatsApp Business")
    
    app.run(port=5000, debug=True)
