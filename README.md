# WhatsApp Business API Server

Servidor Flask para WhatsApp Business API que permite:
- 📤 Enviar mensajes de WhatsApp
- 📥 Recibir mensajes via webhook
- 🔗 Integración completa con Meta Business API

## 🚀 Deploy en Render.com

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## 📋 Configuración

1. Configura tus tokens de Meta en las variables de entorno:
   - `ACCESS_TOKEN`: Tu token de WhatsApp Business API
   - `VERIFY_TOKEN`: Token para verificación de webhook
   - `PHONE_NUMBER_ID`: ID de tu número de WhatsApp Business

## 🔧 Endpoints

- `POST /send-message` - Enviar mensajes
- `POST /webhook` - Recibir eventos de WhatsApp
- `GET /test-config` - Verificar configuración

## 🏗️ Estructura

```
├── wsp_server.py       # Servidor principal
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración para deployment
└── README.md          # Esta documentación
```

## 💡 Uso

```bash
# Enviar mensaje
curl -X POST https://tu-app.onrender.com/send-message \
  -H "Content-Type: application/json" \
  -d '{"to": "5491234567890", "message": "Hola!"}'
```

## 🔐 Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `ACCESS_TOKEN` | Token de WhatsApp Business API |
| `VERIFY_TOKEN` | Token de verificación del webhook |
| `PHONE_NUMBER_ID` | ID del número de WhatsApp Business |
