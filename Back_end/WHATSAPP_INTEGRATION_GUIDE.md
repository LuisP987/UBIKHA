# 📱 INTEGRACIÓN WHATSAPP - API UBIKHA

## 🎯 FLUJO COMPLETO DE REGISTRO CON WHATSAPP

### ARQUITECTURA
```
┌─────────────────┐    HTTP REST API    ┌──────────────────┐
│                 │ ← Token Security → │                  │
│   UBIKHA        │                    │  WhatsApp API    │
│   (Python)      │ ← JSON Messages → │  (Node.js)       │
│   Puerto 8000   │                    │  Puerto 3000     │
└─────────────────┘                    └──────────────────┘
```

### 🔐 CONFIGURACIÓN DE SEGURIDAD

**Token de Autenticación:**
```
Header: x-system-token: ubikha_whatsapp_2024_secure_token_123
```

**Variables de Entorno (.env):**
```
WHATSAPP_API_URL=http://localhost:3000
WHATSAPP_API_TOKEN=ubikha_whatsapp_2024_secure_token_123
```

---

## 📋 ENDPOINTS DISPONIBLES

### 1. 🔍 Verificar Estado del Servicio WhatsApp
```http
GET http://localhost:8000/whatsapp-auth/service/status
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Servicio WhatsApp conectado exitosamente",
    "data": {"conectado": true}
}
```

### 2. 📱 PASO 1: Enviar Código de Verificación
```http
POST http://localhost:8000/whatsapp-auth/enviar-codigo-registro
Content-Type: application/json

{
    "phone_number": "950205006"
}
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Código de verificación enviado exitosamente",
    "data": {
        "telefono": "950205006"
    }
}
```

### 3. ✅ PASO 2: Verificar Código
```http
POST http://localhost:8000/whatsapp-auth/verificar-codigo-registro
Content-Type: application/json

{
    "phone_number": "950205006",
    "code": "123456"
}
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Número de teléfono verificado exitosamente",
    "verified": true,
    "data": {
        "telefono": "950205006",
        "verificado": true,
        "siguiente_paso": "completar_registro"
    }
}
```

### 4. 📝 PASO 3: Completar Registro
```http
POST http://localhost:8000/whatsapp-auth/completar-registro
Content-Type: application/json

{
    "nombres": "Alexander",
    "apellidos": "Suni",
    "email": "alexander@example.com",
    "num_celular": "950205006",
    "password": "mi_password_seguro",
    "tipo_usuario": "inquilino"
}
```

**Respuesta:**
```json
{
    "mensaje": "Usuario registrado exitosamente",
    "usuario": {
        "id": 123,
        "nombres": "Alexander",
        "apellidos": "Suni",
        "email": "alexander@example.com",
        "num_celular": "950205006",
        "tipo_usuario": "inquilino",
        "telefono_verificado": true
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

---

## 🔄 INTEGRACIÓN CON WHATSAPP API (Node.js)

### Endpoint para Verificar Estado
```http
GET http://localhost:3000/api/service/status
Headers: x-system-token: ubikha_whatsapp_2024_secure_token_123
```

### Endpoint para Enviar Mensajes
```http
POST http://localhost:3000/api/service/send-text
Headers: x-system-token: ubikha_whatsapp_2024_secure_token_123
Content-Type: application/json

{
    "telefono": "51987654321",
    "mensaje": "Tu código UBIKHA es: 123456"
}
```

---

## 📊 EJEMPLOS DE USO COMPLETO

### Ejemplo 1: Registro Completo Exitoso
```javascript
// 1. Verificar servicio WhatsApp
const statusResponse = await fetch('http://localhost:8000/whatsapp-auth/service/status');

// 2. Enviar código
const sendCodeResponse = await fetch('http://localhost:8000/whatsapp-auth/enviar-codigo-registro', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({phone_number: "950205006"})
});

// 3. Verificar código (usuario ingresa código recibido por WhatsApp)
const verifyResponse = await fetch('http://localhost:8000/whatsapp-auth/verificar-codigo-registro', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        phone_number: "950205006",
        code: "123456"
    })
});

// 4. Completar registro
const registerResponse = await fetch('http://localhost:8000/whatsapp-auth/completar-registro', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        nombres: "Alexander",
        apellidos: "Suni",
        email: "alexander@example.com",
        num_celular: "950205006",
        password: "mi_password_seguro",
        tipo_usuario: "inquilino"
    })
});
```

---

## 🚨 MANEJO DE ERRORES

### Errores Comunes:

**Servicio WhatsApp no disponible:**
```json
{
    "detail": "El servicio de WhatsApp no está disponible en este momento"
}
```

**Número ya registrado:**
```json
{
    "detail": "Este número de teléfono ya está registrado. Usa el login en su lugar."
}
```

**Código inválido:**
```json
{
    "detail": "Código de verificación inválido o expirado"
}
```

**Email ya existe:**
```json
{
    "detail": "Este email ya está registrado"
}
```

---

## ⚡ CARACTERÍSTICAS AVANZADAS

### Validación de Números Telefónicos
- Formato aceptado: **Solo 9 dígitos** (ejemplo: `950205006`)
- Debe empezar con **9** (números móviles peruanos)
- Automáticamente agrega código de país +51 para WhatsApp
- Validación estricta: exactamente 9 dígitos numéricos

### Expiración de Códigos
- Los códigos expiran después de 5 minutos
- Limpieza automática de códigos expirados

### Mensajes Automáticos
- Código de verificación: "Tu código UBIKHA es: 123456"
- Mensaje de bienvenida: "¡Bienvenido a UBIKHA, {nombre}! Tu registro se completó exitosamente..."

### Logging y Monitoreo
- Logs detallados de todas las operaciones
- Estadísticas de verificaciones pendientes
- Monitoreo del estado del servicio WhatsApp

---

## 🔧 CONFIGURACIÓN PARA DESARROLLO

### 1. Iniciar WhatsApp API (Node.js)
```bash
cd whatsapp-api
npm start # Puerto 3000
```

### 2. Iniciar UBIKHA API (Python)
```bash
cd Back_end/app
python main.py # Puerto 8000
```

### 3. Probar Integración
```bash
# Verificar estado
curl http://localhost:8000/whatsapp-auth/service/status

# Enviar código
curl -X POST http://localhost:8000/whatsapp-auth/enviar-codigo-registro \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "950205006"}'
```

¡La integración está lista para uso! 🚀
