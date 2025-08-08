# 📋 EJEMPLO DE REGISTRO CON FECHA DE NACIMIENTO

## 🔧 Campos del Registro Mejorado

Ahora el endpoint `/auth/registro` acepta y valida los siguientes campos:

### ✅ Campos Obligatorios:
- `email`: Dirección de correo electrónico válida
- `nombres`: Nombres (mínimo 2 caracteres, máximo 100)
- `apellido_paterno`: Apellido paterno (mínimo 2 caracteres, máximo 50)
- `password`: Contraseña (mínimo 8 caracteres)

### ✅ Campos Opcionales:
- `apellido_materno`: Apellido materno (máximo 50 caracteres)
- `num_celular`: Número de celular (formato internacional válido)
- `fecha_nacimiento`: Fecha de nacimiento (formato ISO: YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)

## 📝 Ejemplo de Registro Completo

```json
{
  "email": "usuario@ejemplo.com",
  "nombres": "Juan Carlos",
  "apellido_paterno": "García",
  "apellido_materno": "López",
  "num_celular": "+51987654321",
  "fecha_nacimiento": "1990-05-15T00:00:00",
  "password": "MiPassword123"
}
```

## 📝 Ejemplo de Registro Mínimo

```json
{
  "email": "usuario@ejemplo.com",
  "nombres": "María",
  "apellido_paterno": "Rodríguez",
  "password": "MiPassword123"
}
```

## 🛡️ Validaciones Implementadas

### Fecha de Nacimiento:
- ✅ No puede ser futura
- ✅ Usuario debe tener al menos 13 años
- ✅ No puede ser mayor a 120 años

### Nombres y Apellidos:
- ✅ Solo letras, espacios, apostrofes y guiones
- ✅ Se capitalizan automáticamente
- ✅ Se eliminan espacios extra

### Número de Celular:
- ✅ Formato internacional válido
- ✅ Puede incluir código de país (+51, +1, etc.)

### Contraseña:
- ✅ Mínimo 8 caracteres
- ✅ Al menos una mayúscula
- ✅ Al menos una minúscula  
- ✅ Al menos un número

## 🚀 Cómo Probar

```bash
curl -X 'POST' \
  'http://26.196.154.46:8000/auth/registro' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@ubikha.pe",
    "nombres": "Alexander",
    "apellido_paterno": "Suni",
    "apellido_materno": "García",
    "num_celular": "+51987123456",
    "fecha_nacimiento": "1995-03-20T00:00:00",
    "password": "MiPassword123"
  }'
```

## 📊 Respuesta Esperada

```json
{
  "mensaje": "Usuario registrado exitosamente",
  "usuario_id": 12,
  "rol": "arrendatario"
}
```

Ahora los usuarios podrán registrarse con su fecha de nacimiento y toda la información será validada correctamente! 🎉
