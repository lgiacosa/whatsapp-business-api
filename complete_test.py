import requests
import json
import time

print("🔍 Verificando servidor...")

# Primero verificar si el servidor está corriendo
try:
    response = requests.get("http://localhost:5000/", timeout=5)
    print(f"✅ Servidor activo - Status: {response.status_code}")
except Exception as e:
    print(f"❌ Servidor no responde: {e}")
    print("💡 Asegúrate de que 'python wsp_server.py' esté ejecutándose")
    exit()

# Verificar configuración
try:
    response = requests.get("http://localhost:5000/test-config", timeout=5)
    config = response.json()
    print(f"📱 Config - Phone ID: {config.get('phone_number_id')}")
    print(f"🔑 Token OK: {config.get('token_ok')}")
    print(f"✅ Ready: {config.get('ready')}")
except Exception as e:
    print(f"❌ Error verificando config: {e}")

# Enviar mensaje
print(f"\n📤 Enviando mensaje a 5493425211865...")
data = {
    "to": "5493425211865",
    "message": "Hola Lucas - Mensaje desde WhatsApp Business API",
    "type": "text"
}

try:
    response = requests.post("http://localhost:5000/send-message", json=data, timeout=10)
    print(f"📊 Response Status: {response.status_code}")
    
    try:
        result = response.json()
        print(f"📋 Response JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("success"):
            print(f"\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
            print(f"📱 Destinatario: {result.get('to')}")
            print(f"🆔 Message ID: {result.get('message_id')}")
        else:
            print(f"\n❌ Error enviando:")
            print(f"Error: {result.get('error')}")
            print(f"Detalles: {result.get('details')}")
    except:
        print(f"📋 Response Text: {response.text}")
        
except Exception as e:
    print(f"❌ Error en petición: {e}")

print(f"\n📱 Revisa tu WhatsApp en el número 5493425211865")
print(f"🔗 Webhook URL para Meta: http://localhost:5000/webhook")
