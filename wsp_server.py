from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Token de verificación para el webhook
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# Token de acceso real de WhatsApp Business API
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')

# ID del número de teléfono de WhatsApp Business
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')

# ID de la cuenta de WhatsApp Business  
BUSINESS_ACCOUNT_ID = "715070248001249"

# URL base de la API de WhatsApp Business
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# Lista para almacenar mensajes (en producción usar base de datos)
received_messages = []

# Validar que TODAS las variables de entorno estén configuradas
missing_vars = []
if not ACCESS_TOKEN or ACCESS_TOKEN.strip() == '':
    print("❌ ERROR: ACCESS_TOKEN no está configurado en las variables de entorno")
    missing_vars.append('ACCESS_TOKEN')
if not VERIFY_TOKEN or VERIFY_TOKEN.strip() == '':
    print("❌ ERROR: VERIFY_TOKEN no está configurado en las variables de entorno")
    missing_vars.append('VERIFY_TOKEN')
if not PHONE_NUMBER_ID or PHONE_NUMBER_ID.strip() == '':
    print("❌ ERROR: PHONE_NUMBER_ID no está configurado en las variables de entorno")
    missing_vars.append('PHONE_NUMBER_ID')

# Evitar que el servidor inicie si faltan variables críticas
if missing_vars:
    print(f"\n🚨 FALLO CRÍTICO: Faltan {len(missing_vars)} variables de entorno obligatorias")
    print("💡 Configura estas variables en Render.com → Environment:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n⚠️  El servidor NO PUEDE INICIAR sin estas configuraciones")
    exit(1)

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
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"📩 Mensaje de {sender} (ID: {message_id}, Tipo: {message_type})")
                
                # Crear objeto de mensaje para almacenar
                message_obj = {
                    "id": message_id,
                    "from": sender,
                    "type": message_type,
                    "time": timestamp,
                    "content": ""
                }
                
                if message_type == "text":
                    text_content = message["text"]["body"]
                    message_obj["content"] = text_content
                    print(f"💬 Contenido: {text_content}")
                    
                    # Aquí puedes agregar lógica para responder automáticamente
                    # send_message(sender, f"Recibido: {text_content}")
                
                elif message_type == "image":
                    message_obj["content"] = "🖼️ Imagen recibida"
                    print("🖼️ Imagen recibida")
                elif message_type == "document":
                    message_obj["content"] = "📄 Documento recibido"
                    print("📄 Documento recibido")
                else:
                    message_obj["content"] = f"📱 Mensaje tipo: {message_type}"
                    print(f"📱 Mensaje tipo: {message_type}")
                
                # Guardar mensaje en la lista (en producción usar base de datos)
                received_messages.insert(0, message_obj)  # Más recientes primero
                
                # Mantener solo los últimos 100 mensajes
                if len(received_messages) > 100:
                    received_messages.pop()
    
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")

@app.route("/send-message", methods=["POST"])
def send_message_endpoint():
    """
    Endpoint para enviar mensajes de WhatsApp (texto o plantillas)
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionó data JSON"}), 400
        
        to = data.get("to")
        message_type = data.get("type", "text")
        
        if not to:
            return jsonify({"error": "Campo 'to' requerido"}), 400
        
        # Verificar tipo de mensaje
        if message_type == "template":
            # Envío de plantilla
            template_name = data.get("template_name")
            template_parameters = data.get("template_parameters", [])
            
            if not template_name:
                return jsonify({"error": "Campo 'template_name' requerido para plantillas"}), 400
            
            # Mapeo correcto de idiomas por plantilla (SOLO PLANTILLAS REALES)
            template_languages = {
                "hello_world": "en_US",
                "otp": "es",
                "otp_transacciones": "es", 
                "tarjeta_credito": "es"
            }
            
            template_language = template_languages.get(template_name, "es")
            
            result = send_template(to, template_name, template_language, template_parameters)
        else:
            # Envío de mensaje de texto
            message = data.get("message")
            if not message:
                return jsonify({"error": "Campo 'message' requerido para mensajes de texto"}), 400
            
            result = send_message(to, message, message_type)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Mensaje enviado correctamente",
                "message_id": result.get("message_id"),
                "to": to,
                "type": message_type
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

def send_template(to, template_name, language="es", parameters=None):
    """
    Envía una plantilla de WhatsApp usando la API de Meta
    """
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Construcción del payload para plantilla
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language
                }
            }
        }
        
        # Agregar parámetros si existen
        if parameters and len(parameters) > 0:
            # Componentes para el cuerpo del mensaje
            components = []
            
            # Parámetros del cuerpo (primer parámetro)
            if len(parameters) >= 1:
                components.append({
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": str(parameters[0])
                        }
                    ]
                })
            
            # Parámetros de botones URL (parámetros adicionales)
            if len(parameters) > 1:
                # Agregar parámetros de botones
                button_parameters = []
                for i in range(1, len(parameters)):
                    button_parameters.append({
                        "type": "text",
                        "text": str(parameters[i])
                    })
                
                components.append({
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": button_parameters
                })
            
            payload["template"]["components"] = components
        
        print(f"📧 Enviando plantilla '{template_name}' a {to}")
        if parameters:
            print(f"📝 Parámetros: {parameters}")
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response_data = response.json()
        
        print(f"📊 Respuesta API: {response.status_code}")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            message_id = response_data.get("messages", [{}])[0].get("id")
            return {
                "success": True,
                "message_id": message_id,
                "response": response_data,
                "template_name": template_name
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
            "error": "Error enviando plantilla",
            "details": str(e)
        }

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "WhatsApp Business API",
        "status": "active",
        "endpoints": [
            "/webhook", 
            "/send-message", 
            "/send-template", 
            "/templates",
            "/test-config", 
            "/test-send", 
            "/dashboard",
            "/api/messages"
        ]
    })

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Servir el dashboard HTML
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), 'dashboard.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return jsonify({"error": "Dashboard no encontrado"}), 404

@app.route("/api/messages", methods=["GET"])
def get_messages():
    """
    API para obtener mensajes recibidos
    """
    return jsonify({
        "messages": received_messages,
        "count": len(received_messages)
    })

@app.route("/test-config", methods=["GET"])
def test_config():
    """
    Endpoint para verificar la configuración de variables de entorno
    """
    # Leer variables directamente desde os.environ para debugging
    access_token_env = os.environ.get('ACCESS_TOKEN', '')
    verify_token_env = os.environ.get('VERIFY_TOKEN', '')
    phone_id_env = os.environ.get('PHONE_NUMBER_ID', '')
    
    return jsonify({
        "phone_number_id": phone_id_env,
        "business_account_id": BUSINESS_ACCOUNT_ID,
        "token_ok": len(access_token_env) > 50,
        "verify_token_ok": len(verify_token_env) > 10,
        "ready": len(access_token_env) > 50 and len(verify_token_env) > 10 and len(phone_id_env) > 5,
        "debug": {
            "env_vars": {
                "ACCESS_TOKEN_length": len(access_token_env),
                "ACCESS_TOKEN_start": access_token_env[:20] if access_token_env else "EMPTY",  # Para debugging
                "ACCESS_TOKEN_end": access_token_env[-10:] if access_token_env else "EMPTY",  # Para debugging
                "VERIFY_TOKEN_length": len(verify_token_env),
                "PHONE_NUMBER_ID_length": len(phone_id_env),
                "PHONE_NUMBER_ID_value": phone_id_env  # Para debugging
            },
            "global_vars": {
                "ACCESS_TOKEN_length": len(ACCESS_TOKEN) if ACCESS_TOKEN else 0,
                "ACCESS_TOKEN_start": ACCESS_TOKEN[:20] if ACCESS_TOKEN else "EMPTY",  # Para debugging
                "ACCESS_TOKEN_end": ACCESS_TOKEN[-10:] if ACCESS_TOKEN else "EMPTY",  # Para debugging
                "VERIFY_TOKEN_length": len(VERIFY_TOKEN) if VERIFY_TOKEN else 0,
                "PHONE_NUMBER_ID_length": len(PHONE_NUMBER_ID) if PHONE_NUMBER_ID else 0,
                "PHONE_NUMBER_ID_value": PHONE_NUMBER_ID  # Para debugging
            }
        }
    })

@app.route("/test-send", methods=["POST"])
def test_send():
    try:
        data = request.json
        to = data.get("to") if data else None
        
        if not to:
            return jsonify({"error": "Necesitas 'to' en el JSON"}), 400
        
        test_message = f"🧪 Prueba WhatsApp API - {datetime.now().strftime('%H:%M:%S')}"
        result = send_message(to, test_message)
        
        return jsonify(result), 200 if result.get("success") else 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/templates", methods=["GET"])
def get_templates():
    """
    Endpoint para obtener las plantillas disponibles (consulta Meta en tiempo real)
    """
    try:
        # Consultar plantillas reales de Meta
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        meta_url = f"https://graph.facebook.com/v18.0/{BUSINESS_ACCOUNT_ID}/message_templates"
        response = requests.get(meta_url, headers=headers)
        
        # Información local de plantillas conocidas
        template_info = {
            "hello_world": {
                "display_name": "Hello World",
                "description": "Plantilla de saludo básica (en inglés)",
                "parameters": [],
                "example": "Welcome and congratulations!! This message demonstrates your ability to send a WhatsApp message notification from the Cloud API, hosted by Meta."
            },
            "otp": {
                "display_name": "Código OTP",
                "description": "Código de verificación de un solo uso",
                "parameters": ["codigo"],
                "example": "Tu código de verificación es: {{1}}. No compartas este código con nadie."
            },
            "tarjeta_credito": {
                "display_name": "Recordatorio Tarjeta de Crédito",
                "description": "Recordatorio de pago de tarjeta",
                "parameters": ["nombre_tarjeta", "ultimos_digitos", "fecha_vencimiento"],
                "example": "Recordatorio: El pago de tu tarjeta {{1}} que termina en {{2}} está programado para el {{3}}. Gracias."
            },
            "otp_transacciones": {
                "display_name": "Código OTP para Transacciones",
                "description": "Envío de código de verificación para transacciones",
                "parameters": ["codigo_otp"],
                "example": "Use el código *{{1}}* para autorizar su transacción. Por tu seguridad, no compartas este código."
            }
        }
        
        if response.status_code == 200:
            meta_data = response.json()
            templates = []
            
            # Procesar plantillas de Meta
            for template in meta_data.get("data", []):
                name = template.get("name")
                language = template.get("language")
                status = template.get("status")
                
                # Solo incluir plantillas aprobadas
                if status == "APPROVED":
                    # Combinar con información local si existe
                    local_info = template_info.get(name, {
                        "display_name": name.replace("_", " ").title(),
                        "description": f"Plantilla {name}",
                        "parameters": ["param1"],  # Por defecto
                        "example": f"Plantilla {name} con parámetros"
                    })
                    
                    templates.append({
                        "name": name,
                        "display_name": local_info["display_name"],
                        "description": local_info["description"],
                        "language": language,
                        "status": status,
                        "parameters": local_info["parameters"],
                        "example": local_info["example"]
                    })
            
            return jsonify({
                "templates": templates,
                "count": len(templates),
                "source": "Meta Business API (tiempo real)"
            })
        else:
            # Si falla la consulta a Meta, usar lista local como fallback
            fallback_templates = [
                {
                    "name": "otp",
                    "display_name": "Código OTP",
                    "description": "Código de verificación de un solo uso",
                    "language": "es",
                    "status": "LOCAL_FALLBACK",
                    "parameters": ["codigo"],
                    "example": "Tu código de verificación es: {{1}}. No compartas este código con nadie."
                }
            ]
            
            return jsonify({
                "templates": fallback_templates,
                "count": len(fallback_templates),
                "source": "Fallback local (Meta no disponible)",
                "meta_error": f"Error {response.status_code}: {response.text}"
            })
            
    except Exception as e:
        # Fallback en caso de error
        return jsonify({
            "templates": [
                {
                    "name": "otp",
                    "display_name": "Código OTP",
                    "description": "Código de verificación de un solo uso",
                    "language": "es",
                    "status": "LOCAL_FALLBACK",
                    "parameters": ["codigo"],
                    "example": "Tu código de verificación es: {{1}}. No compartas este código con nadie."
                }
            ],
            "count": 1,
            "source": "Fallback local (error de conexión)",
            "error": str(e)
        })

@app.route("/send-template", methods=["POST"])
def send_template_endpoint():
    """
    Endpoint específico para enviar plantillas
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionó data JSON"}), 400
        
        to = data.get("to")
        template_name = data.get("template_name")
        template_parameters = data.get("template_parameters", [])
        
        if not to or not template_name:
            return jsonify({"error": "Campos 'to' y 'template_name' requeridos"}), 400
        
        # Mapeo correcto de idiomas por plantilla (SOLO PLANTILLAS REALES)
        template_languages = {
            "hello_world": "en_US",
            "otp": "es",
            "otp_transacciones": "es", 
            "tarjeta_credito": "es"
        }
        
        template_language = template_languages.get(template_name, "es")
        
        result = send_template(to, template_name, template_language, template_parameters)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Plantilla enviada correctamente",
                "message_id": result.get("message_id"),
                "template_name": template_name,
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

@app.route("/templates-meta", methods=["GET"])
def get_meta_templates():
    """
    Obtener plantillas reales desde la API de Meta
    """
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # URL para obtener plantillas de la API de Meta
        templates_url = f"https://graph.facebook.com/v18.0/{BUSINESS_ACCOUNT_ID}/message_templates"
        
        response = requests.get(templates_url, headers=headers)
        response_data = response.json()
        
        print(f"📋 Respuesta plantillas Meta: {response.status_code}")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            templates = response_data.get("data", [])
            
            # Formatear plantillas para nuestro uso
            formatted_templates = []
            for template in templates:
                if template.get("status") == "APPROVED":  # Solo plantillas aprobadas
                    formatted_templates.append({
                        "name": template.get("name"),
                        "language": template.get("language"),
                        "status": template.get("status"),
                        "category": template.get("category"),
                        "components": template.get("components", [])
                    })
            
            return jsonify({
                "success": True,
                "templates": formatted_templates,
                "count": len(formatted_templates),
                "raw_response": response_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Error obteniendo plantillas de Meta",
                "details": response_data,
                "status_code": response.status_code
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Error consultando plantillas",
            "details": str(e)
        }), 500

@app.route("/send-otp", methods=["POST"])
def send_otp():
    """
    Endpoint específico para enviar códigos OTP
    Simplifica el envío de la plantilla OTP con manejo inteligente de parámetros
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se proporcionó data JSON"}), 400
        
        to = data.get("to")
        codigo = data.get("codigo")
        url_parameter = data.get("url_parameter", "https://tu-app.com/verify")  # URL por defecto
        
        if not to:
            return jsonify({"error": "Campo 'to' (número de teléfono) requerido"}), 400
        
        if not codigo:
            return jsonify({"error": "Campo 'codigo' (código OTP) requerido"}), 400
        
        # Intentar con diferentes configuraciones de parámetros
        # 1. Solo código (plantilla simple)
        print(f"🔄 Intentando envío OTP simple: código={codigo}")
        result = send_template(to, "otp", "es", [codigo])
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Código OTP enviado correctamente",
                "message_id": result.get("message_id"),
                "to": to,
                "codigo": codigo,
                "method": "simple"
            }), 200
        
        # 2. Si falla, intentar con código + URL (plantilla con botón)
        print(f"🔄 Intentando envío OTP con botón: código={codigo}, url={url_parameter}")
        result = send_template(to, "otp", "es", [codigo, url_parameter])
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Código OTP enviado correctamente (con botón)",
                "message_id": result.get("message_id"),
                "to": to,
                "codigo": codigo,
                "url_parameter": url_parameter,
                "method": "with_button"
            }), 200
        
        # 3. Si ambos fallan, devolver error detallado
        return jsonify({
            "success": False,
            "error": "No se pudo enviar el OTP con ninguna configuración",
            "details": result.get("details"),
            "suggestions": [
                "Verifica que la plantilla 'otp' esté aprobada en Meta",
                "Revisa la estructura de la plantilla en Meta Business Manager",
                "Asegúrate de que el número esté en formato internacional (+país + número)"
            ]
        }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

@app.route("/template-info/<template_name>", methods=["GET"])
def get_template_info(template_name):
    """
    Endpoint para obtener información detallada de una plantilla específica
    """
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Consultar plantilla específica de Meta
        meta_url = f"https://graph.facebook.com/v18.0/{BUSINESS_ACCOUNT_ID}/message_templates"
        params = {"name": template_name}
        response = requests.get(meta_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get("data", [])
            
            if templates:
                template = templates[0]  # Tomar la primera coincidencia
                
                # Analizar componentes
                components_info = []
                components = template.get("components", [])
                
                for comp in components:
                    comp_type = comp.get("type")
                    comp_info = {"type": comp_type}
                    
                    if comp_type == "BODY":
                        # Contar parámetros en el texto
                        text = comp.get("text", "")
                        param_count = text.count("{{") 
                        comp_info["parameters_needed"] = param_count
                        comp_info["text"] = text
                    
                    elif comp_type == "BUTTONS":
                        buttons = comp.get("buttons", [])
                        comp_info["buttons"] = []
                        for btn in buttons:
                            btn_info = {
                                "type": btn.get("type"),
                                "text": btn.get("text")
                            }
                            if btn.get("type") == "URL":
                                btn_info["url"] = btn.get("url")
                                # Contar parámetros en la URL
                                url_params = btn.get("url", "").count("{{")
                                btn_info["parameters_needed"] = url_params
                            comp_info["buttons"].append(btn_info)
                    
                    components_info.append(comp_info)
                
                return jsonify({
                    "template_name": template_name,
                    "status": template.get("status"),
                    "language": template.get("language"),
                    "components": components_info,
                    "usage_tips": {
                        "body_parameters": sum(c.get("parameters_needed", 0) for c in components_info if c["type"] == "BODY"),
                        "button_parameters": sum(len(c.get("buttons", [])) for c in components_info if c["type"] == "BUTTONS"),
                        "total_parameters_needed": sum(c.get("parameters_needed", 0) for c in components_info)
                    }
                })
            else:
                return jsonify({
                    "error": f"Plantilla '{template_name}' no encontrada",
                    "available_templates": [t.get("name") for t in data.get("data", [])]
                }), 404
        
        else:
            return jsonify({
                "error": f"Error consultando Meta API: {response.status_code}",
                "details": response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "error": "Error consultando información de plantilla",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 WhatsApp Business API Server")
    print("="*50)
    print(f"📱 Phone ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Access Token: {'✅ Configurado' if len(ACCESS_TOKEN) > 50 else '❌ Falta configurar'}")
    print(f"🔐 Verify Token: {'✅ Configurado' if len(VERIFY_TOKEN) > 20 else '❌ Falta configurar'}")
    print("="*50)
    
    # Puerto desde variable de entorno (Render usa PORT)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
