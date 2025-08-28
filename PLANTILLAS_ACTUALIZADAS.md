# 🎯 PLANTILLAS ACTUALIZADAS CON INFORMACIÓN REAL

## ✅ Plantillas disponibles en tu cuenta:

### 1. **hello_world**
- **Idioma**: `en_US` (Inglés)
- **Parámetros**: Ninguno
- **Uso en Postman/PowerShell**:
```json
{
    "to": "+5493425211865",
    "type": "template",
    "template_name": "hello_world",
    "template_language": "en_US"
}
```

### 2. **tarjeta_credito**
- **Idioma**: `es` (Español)
- **Parámetros**: 3 parámetros requeridos
  1. Nombre de la tarjeta (ej: "CS Mutual Credit Plus")
  2. Últimos dígitos (ej: "1234")
  3. Fecha de vencimiento (ej: "22 de marzo de 2024")

- **Uso en Postman/PowerShell**:
```json
{
    "to": "+5493425211865",
    "type": "template",
    "template_name": "tarjeta_credito",
    "template_language": "es",
    "template_parameters": [
        "CS Mutual Credit Plus",
        "1234", 
        "22 de marzo de 2024"
    ]
}
```

### 3. **otp_transacciones** 🆕
- **Idioma**: `es` (Español)
- **Parámetros**: 2 parámetros requeridos
  1. Código OTP (ej: "123456")
  2. Parámetro URL del botón (ej: "codigo123" o valor dinámico)

- **Uso en Postman/PowerShell**:
```json
{
    "to": "+5493425211865",
    "type": "template",
    "template_name": "otp_transacciones",
    "template_language": "es",
    "template_parameters": [
        "123456",
        "codigo123"
    ]
}
```

## 🚀 Próximos pasos:

1. **Hacer commit y push** de los cambios
2. **Redesplegar** en Render
3. **Probar las plantillas** con los parámetros correctos

## 📱 Prueba inmediata:

### Hello World (sin parámetros):
```powershell
$body = @{
    to = "+5493425211865"
    type = "template"
    template_name = "hello_world"
    template_language = "en_US"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-message" -Method POST -Body $body -ContentType "application/json"
$response
```

### Tarjeta de Crédito (con 3 parámetros):
```powershell
$body = @{
    to = "+5493425211865"
    type = "template"
    template_name = "tarjeta_credito"
    template_language = "es"
    template_parameters = @("CS Mutual Credit Plus", "1234", "22 de marzo de 2024")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-message" -Method POST -Body $body -ContentType "application/json"
$response
```

### OTP Transacciones (con 2 parámetros) 🆕:
```powershell
$body = @{
    to = "+5493425211865"
    type = "template"
    template_name = "otp_transacciones"
    template_language = "es"
    template_parameters = @("123456", "codigo123")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://whatsapp-business-api-wexa.onrender.com/send-message" -Method POST -Body $body -ContentType "application/json"
$response
```
