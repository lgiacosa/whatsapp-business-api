import requests
import json

# Datos para enviar mensaje
url = "http://localhost:5000/send-message"
data = {
    "to": "5493425211865",
    "message": "Hola Lucas",
    "type": "text"
}

print("📤 Enviando mensaje a WhatsApp...")
print(f"Número: {data['to']}")
print(f"Mensaje: {data['message']}")

try:
    response = requests.post(url, json=data)
    print(f"\n📊 Respuesta del servidor:")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ ¡Mensaje enviado exitosamente!")
        print(f"Message ID: {result.get('message_id', 'N/A')}")
    else:
        print(f"\n❌ Error enviando mensaje")
        
except Exception as e:
    print(f"❌ Error: {e}")
