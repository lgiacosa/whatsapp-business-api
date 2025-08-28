# Guía para Usar Postman con WhatsApp Business API

## ✅ El problema estaba resuelto
El error "Method Not Allowed" que veías era porque posiblemente estabas usando GET en lugar de POST. Los endpoints están funcionando correctamente.

## 📋 Configuración de Postman

### 1. Endpoint para Enviar Mensajes
**URL**: `https://whatsapp-business-api-wexa.onrender.com/send-message`
**Método**: `POST`
**Headers**:
```
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
    "to": "+549XXXXXXXXX",
    "message": "Hola, este es un mensaje de prueba desde la API",
    "type": "text"
}
```

### 2. Endpoint de Prueba Rápida
**URL**: `https://whatsapp-business-api-wexa.onrender.com/test-send`
**Método**: `POST`
**Headers**:
```
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
    "to": "+549XXXXXXXXX"
}
```

### 3. Verificar Configuración
**URL**: `https://whatsapp-business-api-wexa.onrender.com/test-config`
**Método**: `GET`
(No necesita headers ni body)

## 🔧 Pasos en Postman

1. **Crear nueva petición**:
   - Abre Postman
   - Clic en "New" → "Request"

2. **Configurar método**:
   - Cambia de GET a POST en el dropdown

3. **Agregar URL**:
   - Pega la URL completa del endpoint

4. **Configurar Headers**:
   - Ve a la pestaña "Headers"
   - Agrega: `Content-Type` con valor `application/json`

5. **Configurar Body**:
   - Ve a la pestaña "Body"
   - Selecciona "raw"
   - En el dropdown de la derecha selecciona "JSON"
   - Pega el JSON del ejemplo

6. **Enviar petición**:
   - Clic en "Send"

## 📱 Números de Teléfono

**IMPORTANTE**: El número debe estar en formato internacional:
- ✅ Correcto: `+5491133334444`
- ❌ Incorrecto: `11-3333-4444`
- ❌ Incorrecto: `1133334444`

**Para Argentina**: `+549` + código de área sin 0 + número

Ejemplos:
- Buenos Aires: `+5491133334444`
- Córdoba: `+5493514444555`
- Rosario: `+5493414444555`

## 🔍 Respuestas Esperadas

### Éxito (200):
```json
{
    "success": true,
    "message": "Mensaje enviado correctamente",
    "message_id": "wamid.HBgLNTQ5...",
    "to": "+549XXXXXXXXX"
}
```

### Error de formato (400):
```json
{
    "success": false,
    "error": "Faltan campos 'to' y/o 'message'"
}
```

### Error de API de WhatsApp (400):
```json
{
    "success": false,
    "error": "Error en API de WhatsApp",
    "details": {
        "error": {
            "message": "Invalid parameter",
            "code": 100
        }
    }
}
```

## 🐛 Troubleshooting

1. **"Method Not Allowed"**:
   - Verifica que estés usando POST, no GET

2. **"Cannot resolve hostname"**:
   - Verifica la URL completa
   - Verifica tu conexión a internet

3. **Error 400 con número válido**:
   - El número debe estar registrado en WhatsApp
   - Debe aceptar mensajes de empresas
   - Debe estar en formato internacional correcto

4. **Error 401**:
   - Token expirado (verificar en `/test-config`)

## 🧪 Prueba con PowerShell

También puedes probar desde PowerShell:

```powershell
$headers = @{'Content-Type' = 'application/json'}
$body = '{"to": "+549XXXXXXXXX", "message": "Prueba desde PowerShell"}'
Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-message" -Method POST -Headers $headers -Body $body
```
