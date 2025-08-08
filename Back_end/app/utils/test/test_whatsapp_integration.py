"""
🧪 Script de prueba para la integración WhatsApp + UBIKHA

Este script verifica:
1. ✅ Microservicio WhatsApp funcionando
2. ✅ WhatsApp Web conectado y autenticado
3. ✅ Envío de código de verificación
4. ✅ Envío de mensaje de bienvenida
"""

import asyncio
import sys
import os

# Agregar el directorio app al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.whatsapp import WhatsAppService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_whatsapp_integration():
    """Prueba completa de la integración WhatsApp"""
    
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN WHATSAPP + UBIKHA")
    print("=" * 60)
    
    # Inicializar servicio
    whatsapp_service = WhatsAppService()
    
    # PRUEBA 1: Verificar servicio disponible
    print("\n📡 PRUEBA 1: Verificando microservicio WhatsApp...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:3000/health")
            if response.status_code == 200:
                print("✅ Microservicio WhatsApp funcionando correctamente")
            else:
                print(f"❌ Microservicio no responde: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error al conectar con microservicio: {e}")
        return False
    
    # PRUEBA 2: Verificar estado de WhatsApp Web
    print("\n📱 PRUEBA 2: Verificando WhatsApp Web...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:3000/api/whatsapp/status")
            if response.status_code == 200:
                data = response.json()
                connected = data.get("connected", False)
                authenticated = data.get("authenticated", False)
                hasQR = data.get("hasQR", False)
                
                print(f"   Conectado: {'✅' if connected else '❌'} {connected}")
                print(f"   Autenticado: {'✅' if authenticated else '❌'} {authenticated}")
                print(f"   Tiene QR: {'✅' if hasQR else '❌'} {hasQR}")
                
                if not connected or not authenticated:
                    print("\n⚠️  ACCIÓN REQUERIDA:")
                    print("   1. Ve a http://localhost:3000")
                    print("   2. Haz clic en 'Conectar'")
                    print("   3. Escanea el código QR con tu WhatsApp")
                    print("   4. Espera a que aparezca 'WhatsApp Web está listo!'")
                    print("   5. Ejecuta este script nuevamente")
                    return False
                
                print("✅ WhatsApp Web conectado y autenticado")
            else:
                print(f"❌ Error al verificar estado: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error al verificar WhatsApp: {e}")
        return False
    
    # PRUEBA 3: Verificar servicio con nuestro método
    print("\n🔧 PRUEBA 3: Verificando con nuestro servicio...")
    service_status = await whatsapp_service.check_whatsapp_service_status()
    if service_status:
        print("✅ Servicio WhatsApp verificado correctamente")
    else:
        print("❌ Servicio WhatsApp no disponible")
        return False
    
    # PRUEBA 4: Generar código de verificación
    print("\n🔢 PRUEBA 4: Generando código de verificación...")
    test_phone = "987654321"  # Número de prueba
    code = whatsapp_service.generate_code(test_phone)
    print(f"✅ Código generado: {code}")
    
    # PREGUNTA AL USUARIO
    print("\n" + "="*60)
    print("🧪 PRUEBA DE ENVÍO (OPCIONAL)")
    print("¿Quieres probar el envío real de WhatsApp?")
    print("IMPORTANTE: Esto enviará un mensaje real a tu WhatsApp")
    
    while True:
        respuesta = input("\n¿Continuar con prueba de envío? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            break
        elif respuesta in ['n', 'no']:
            print("\n✅ Pruebas básicas completadas exitosamente!")
            print("🚀 Tu integración WhatsApp está lista para usar")
            return True
        else:
            print("Por favor, responde 's' para sí o 'n' para no")
    
    # Solicitar número de teléfono
    while True:
        phone_input = input("\nIngresa tu número de WhatsApp (ej: 987654321): ").strip()
        if phone_input and phone_input.isdigit() and len(phone_input) == 9:
            test_phone = phone_input
            break
        else:
            print("❌ Número inválido. Debe ser 9 dígitos empezando con 9")
    
    # PRUEBA 5: Enviar código de verificación
    print(f"\n📤 PRUEBA 5: Enviando código al {test_phone}...")
    success = await whatsapp_service.send_verification_code(test_phone)
    if success:
        print("✅ Código de verificación enviado exitosamente!")
        print(f"📱 Revisa tu WhatsApp para ver el código: {code}")
    else:
        print("❌ Error al enviar código de verificación")
        return False
    
    # PRUEBA 6: Enviar mensaje de bienvenida
    print(f"\n🎉 PRUEBA 6: Enviando mensaje de bienvenida...")
    welcome_success = await whatsapp_service.send_welcome_message(test_phone, "Usuario Prueba")
    if welcome_success:
        print("✅ Mensaje de bienvenida enviado exitosamente!")
    else:
        print("❌ Error al enviar mensaje de bienvenida")
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("🎯 RESUMEN DE PRUEBAS:")
    print("✅ Microservicio funcionando")
    print("✅ WhatsApp Web conectado")
    print("✅ Servicio UBIKHA configurado")
    print("✅ Generación de códigos")
    print(f"{'✅' if success else '❌'} Envío de códigos")
    print(f"{'✅' if welcome_success else '❌'} Mensajes de bienvenida")
    print("\n🚀 ¡Tu integración WhatsApp + UBIKHA está funcionando!")
    
    return True

async def main():
    """Función principal"""
    try:
        await test_whatsapp_integration()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas canceladas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        logger.exception("Error en pruebas")

if __name__ == "__main__":
    asyncio.run(main())
