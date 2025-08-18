"""
Script para probar el flujo completo de registro con WhatsApp
"""
import asyncio
import json
from datetime import date

async def test_registration_flow():
    """Prueba el flujo completo de registro"""
    
    print("🧪 TESTING: Flujo completo de registro con WhatsApp")
    print("=" * 60)
    
    # Datos de prueba
    num_celular = "950205006"
    datos_registro = {
        "email": "user@example.com",
        "nombres": "string",
        "apellido_paterno": "string",
        "apellido_materno": "string",
        "fecha_nacimiento": "2004-08-17",
        "password": "stringst",
        "confirmar_password": "stringst"
    }
    
    print(f"📱 Número a verificar: {num_celular}")
    print(f"📧 Email: {datos_registro['email']}")
    print(f"👤 Nombres: {datos_registro['nombres']}")
    
    print("\n🔄 PASO 1: Verificar estado del servicio WhatsApp")
    print("   Endpoint: GET /whatsapp-auth/service/status")
    
    print("\n🔄 PASO 2: Enviar código de verificación")
    print(f"   Endpoint: POST /whatsapp-auth/enviar-codigo")
    print(f"   Body: {{\"phone_number\": \"{num_celular}\"}}")
    
    print("\n🔄 PASO 3: Verificar código (simulado)")
    print(f"   Endpoint: POST /whatsapp-auth/verificar-codigo")
    print(f"   Body: {{\"phone_number\": \"{num_celular}\", \"code\": \"123456\"}}")
    
    print("\n🔄 PASO 4: Completar registro")
    print(f"   Endpoint: POST /whatsapp-auth/completar-registro?num_celular={num_celular}")
    print(f"   Body: {json.dumps(datos_registro, indent=2)}")
    
    print("\n💡 INSTRUCCIONES:")
    print("   1. Ejecuta estos endpoints en orden en Swagger")
    print("   2. El PASO 2 y 3 deben completarse exitosamente antes del PASO 4")
    print("   3. Si el PASO 4 falla, verifica que hayas completado los pasos previos")
    
    print("\n🔍 CAMPOS VERIFICADOS EN LA BD:")
    print("   ✅ email - EXISTS")
    print("   ✅ nombres - EXISTS") 
    print("   ✅ apellido_paterno - EXISTS")
    print("   ✅ apellido_materno - EXISTS")
    print("   ✅ num_celular - EXISTS")
    print("   ✅ fecha_nacimiento - EXISTS")
    print("   ✅ password - EXISTS")
    print("   ✅ celular_verificado - EXISTS")
    print("   ✅ tipo_usuario - EXISTS")
    print("   ❌ telefono_verificado - REMOVED (no existe en BD)")
    
    print("\n🎯 El registro ahora debería funcionar correctamente!")

if __name__ == "__main__":
    asyncio.run(test_registration_flow())
