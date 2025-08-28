# 📧 GUÍA COMPLETA: PLANTILLAS DE WHATSAPP

## 🎯 NUEVAS FUNCIONALIDADES AGREGADAS

### ✅ ENDPOINTS NUEVOS

1. **`GET /templates`** - Lista plantillas disponibles
2. **`POST /send-template`** - Envío específico de plantillas  
3. **`POST /send-message`** - Ahora soporta plantillas y texto

### ✅ DASHBOARD ACTUALIZADO

- Selector de tipo de mensaje (Texto/Plantilla)
- Vista previa de plantillas
- Campos dinámicos para parámetros
- Interfaz intuitiva para envío

## 📋 PLANTILLAS DISPONIBLES

### 1. **hello_world**
- **Nombre**: Hola Mundo
- **Parámetros**: Ninguno
- **Ejemplo**: "Hola, este es un mensaje de WhatsApp Business."

### 2. **tarjeta_credito**
- **Nombre**: Tarjeta de Crédito  
- **Parámetros**: 
  - `nombre_cliente` (texto)
  - `limite_credito` (texto)
- **Ejemplo**: "Hola {{1}}, tu tarjeta de crédito tiene un límite de {{2}}."

## 🔧 USO CON POSTMAN

### Enviar Plantilla Sin Parámetros (hello_world)

**URL**: `POST https://whatsapp-business-api-wexa.onrender.com/send-template`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "to": "+54934263115888",
    "template_name": "hello_world",
    "template_language": "es"
}
```

### Enviar Plantilla Con Parámetros (tarjeta_credito)

**URL**: `POST https://whatsapp-business-api-wexa.onrender.com/send-template`
**Headers**: `Content-Type: application/json`
**Body**:
```json
{
    "to": "+54934263115888",
    "template_name": "tarjeta_credito", 
    "template_language": "es",
    "template_parameters": ["Juan Pérez", "$50,000"]
}
```

### Listar Plantillas Disponibles

**URL**: `GET https://whatsapp-business-api-wexa.onrender.com/templates`
**Respuesta**:
```json
{
    "templates": [
        {
            "name": "hello_world",
            "display_name": "Hola Mundo",
            "description": "Plantilla de saludo básica",
            "language": "es",
            "parameters": [],
            "example": "Hola, este es un mensaje de WhatsApp Business."
        },
        {
            "name": "tarjeta_credito",
            "display_name": "Tarjeta de Crédito",
            "description": "Información sobre tarjeta de crédito",
            "language": "es", 
            "parameters": ["nombre_cliente", "limite_credito"],
            "example": "Hola {{1}}, tu tarjeta de crédito tiene un límite de {{2}}."
        }
    ],
    "count": 2
}
```

## 🧪 PRUEBAS CON POWERSHELL

### Plantilla Simple (hello_world)
```powershell
$headers = @{'Content-Type' = 'application/json'}
$body = @{
    to = "+54934263115888"
    template_name = "hello_world"
    template_language = "es"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-template" -Method POST -Headers $headers -Body $body
```

### Plantilla con Parámetros (tarjeta_credito)
```powershell
$headers = @{'Content-Type' = 'application/json'}
$body = @{
    to = "+54934263115888"
    template_name = "tarjeta_credito"
    template_language = "es"
    template_parameters = @("Juan Pérez", "$50,000")
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-template" -Method POST -Headers $headers -Body $body
```

### Listar Plantillas
```powershell
Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/templates"
```

## 🎯 USO DEL DASHBOARD WEB

1. **Acceder**: https://whatsapp-business-api-wexa.onrender.com/dashboard
2. **Seleccionar**: "📧 Plantilla" en el dropdown
3. **Elegir plantilla**: hello_world o tarjeta_credito
4. **Completar parámetros**: Si la plantilla los requiere
5. **Enviar**: Clic en "📤 Enviar Mensaje"

## ✅ VENTAJAS DE LAS PLANTILLAS

### 🚀 **Mejor Deliverability**
- Pre-aprobadas por Meta
- Mayor tasa de entrega
- Menos probabilidad de ser marcadas como spam

### ⚡ **Más Rápidas**
- Procesamiento optimizado
- Envío inmediato
- Menos restricciones de rate limiting

### 📊 **Mejor Tracking**
- Métricas detalladas en Meta
- Estado de entrega más preciso
- Analytics avanzados

## 🔄 FLUJO DE DEPLOYMENT

Para activar estas funcionalidades en producción:

1. **Subir código** actualizado a GitHub
2. **Redesplegar** en Render.com
3. **Verificar** nuevos endpoints
4. **Probar** dashboard actualizado

## 📱 ENDPOINTS ACTUALIZADOS

Después del deployment:

- `GET /` - Info del servicio
- `GET /templates` - Lista plantillas 🆕
- `POST /send-template` - Enviar plantillas 🆕
- `POST /send-message` - Envío unificado (texto/plantilla) 🔄
- `GET /dashboard` - Dashboard con plantillas 🔄
- `GET /api/messages` - Mensajes recibidos
- `GET /test-config` - Verificar configuración
- `POST /test-send` - Prueba rápida
- `POST /webhook` - Webhook WhatsApp

## 🚨 IMPORTANTE

- **Token de producción** debe estar activo
- **Plantillas** deben estar aprobadas en Meta
- **Parámetros** son obligatorios si la plantilla los requiere
- **Formato** de número internacional (+54...)

---

## 🎯 PASOS INMEDIATOS

1. ✅ **Código actualizado** en workspace
2. 🔄 **Pendiente**: Subir a GitHub y redesplegar
3. 🧪 **Después**: Probar plantillas en dashboard

**¿Quieres que procedamos con el deployment a Render?**
