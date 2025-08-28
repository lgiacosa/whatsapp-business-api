"""
WhatsApp Business API - Servidor Flask para envío de mensajes

INSTALACIÓN DE DEPENDENCIAS:
pip install flask requests

EJECUCIÓN DEL SERVIDOR:
python app.py

EJEMPLO DE LLAMADA CON CURL:
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{"to": "5491234567890", "message": "Hola desde WhatsApp API"}'

CONFIGURACIÓN:
1. Actualiza PHONE_NUMBER_ID con tu ID de WhatsApp Business
2. Actualiza ACCESS_TOKEN con tu token válido de Meta
3. El token se obtiene desde Meta Developer Console
"""

from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# CONFIGURACIÓN - ACTUALIZAR CON TUS DATOS REALES
PHONE_NUMBER_ID = "629824623553106"  # Tu Phone Number ID de WhatsApp Business
ACCESS_TOKEN = "AQUI_PEGA_TU_NUEVO_TOKEN"  # ⚠️ ACTUALIZAR CON TOKEN VÁLIDO DE META

# URL base de la API de WhatsApp Business (v22.0)
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

@app.route("/send", methods=["POST"])
def send_message():
    """
    Endpoint para enviar mensajes de WhatsApp
    
    JSON esperado:
    {
        "to": "5491234567890",
        "message": "Texto del mensaje a enviar"
    }
    
    Retorna el JSON de respuesta de la API de Meta con el mismo status code
    """
    try:
        # Validar que se envió JSON
        if not request.json:
            return jsonify({"error": "Se requiere JSON en el body"}), 400
        
        # Obtener datos del request
        data = request.json
        to = data.get("to")
        message = data.get("message")
        
        # Validar campos obligatorios
        if not to:
            return jsonify({"error": "Campo 'to' es obligatorio"}), 400
        if not message:
            return jsonify({"error": "Campo 'message' es obligatorio"}), 400
        
        # Headers para la API de Meta
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Payload según especificación de WhatsApp Business API
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        print(f"📤 Enviando mensaje a {to}: {message}")
        print(f"🔗 URL: {WHATSAPP_API_URL}")
        
        # Llamada a la API de Meta
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Respuesta API:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # Retornar la respuesta de Meta con el mismo status code
        return jsonify(response_data), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Error de conexión con la API de WhatsApp",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    """
    Endpoint de información del servicio
    """
    return jsonify({
        "service": "WhatsApp Business API",
        "version": "1.0",
        "endpoints": {
            "send": {
                "method": "POST",
                "url": "/send",
                "description": "Enviar mensaje de WhatsApp",
                "body": {
                    "to": "5491234567890",
                    "message": "Texto del mensaje"
                }
            }
        },
        "config": {
            "phone_number_id": PHONE_NUMBER_ID,
            "api_version": "v22.0",
            "token_configured": len(ACCESS_TOKEN) > 10 and ACCESS_TOKEN != "TU_ACCESS_TOKEN_ACTUALIZADO"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    """
    Endpoint de salud del servicio
    """
    return jsonify({
        "status": "healthy",
        "timestamp": "2025-08-26",
        "service": "WhatsApp API Server"
    })

if __name__ == "__main__":
    print("🚀 Iniciando servidor WhatsApp Business API")
    print("📱 Endpoint: http://localhost:5000/send")
    print("📋 Info: http://localhost:5000/")
    print("🔧 Health: http://localhost:5000/health")
    print(f"📞 Phone ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Token configurado: {'✅ Sí' if len(ACCESS_TOKEN) > 10 and ACCESS_TOKEN != 'TU_ACCESS_TOKEN_ACTUALIZADO' else '❌ No - Actualizar ACCESS_TOKEN'}")
    print("\n" + "="*60)
    print("EJEMPLO DE USO:")
    print("curl -X POST http://localhost:5000/send \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"to\": \"5491234567890\", \"message\": \"Hola!\"}'")
    print("="*60)
    
    # Ejecutar servidor Flask
    app.run(host="0.0.0.0", port=5000, debug=True)
