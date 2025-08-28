# WhatsApp Business API Server

Servidor Flask para WhatsApp Business API con soporte para:

- ✅ Envío de mensajes de texto
- ✅ Envío de plantillas pre-aprobadas  
- ✅ Recepción de webhooks
- ✅ Dashboard web interactivo
- ✅ API REST completa

## Endpoints Disponibles

- `GET /` - Información del servicio
- `GET /dashboard` - Dashboard web
- `GET /templates` - Lista plantillas disponibles
- `POST /send-message` - Enviar mensajes (texto/plantilla)
- `POST /send-template` - Enviar plantillas específicas
- `GET /api/messages` - Mensajes recibidos
- `POST /webhook` - Webhook WhatsApp
- `GET /test-config` - Verificar configuración

## Variables de Entorno

- `ACCESS_TOKEN` - Token de acceso WhatsApp Business API
- `VERIFY_TOKEN` - Token de verificación webhook
- `PHONE_NUMBER_ID` - ID del número de teléfono
- `PORT` - Puerto del servidor (Render lo asigna automáticamente)

## Plantillas Disponibles

1. **hello_world** - Saludo básico sin parámetros
2. **tarjeta_credito** - Información de tarjeta con parámetros (nombre, límite)

## Deployment en Render.com

1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Deploy automático desde main branch
