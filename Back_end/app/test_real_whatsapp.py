"""
🧪 Script de prueba interactivo para WhatsApp
"""

import asyncio
import httpx

async def test_with_real_number():
    """Probar con número real del usuario"""
    
    print("🚀 PRUEBA CON TU NÚMERO REAL DE WHATSAPP")
    print("=" * 50)
    print("⚠️  IMPORTANTE: Usa tu número real de WhatsApp")
    print("📱 Formato: Solo los 9 dígitos (ej: 987654321)")
    print()
    
    # Solicitar número real
    phone_number = input("Ingresa tu número de WhatsApp: ").strip()
    
    if not phone_number or len(phone_number) != 9 or not phone_number.isdigit():
        print("❌ Número inválido. Debe ser 9 dígitos")
        return
    
    # Formatear número
    formatted_phone = f"51{phone_number}"
    
    print(f"\n📱 Probando con: {formatted_phone}")
    print("🔄 Enviando mensaje de prueba...")
    
    # Mensaje de prueba
    payload = {
        "phone": formatted_phone,
        "message": f"""🧪 PRUEBA DE INTEGRACIÓN UBIKHA

¡Hola! Este es un mensaje de prueba.

Tu código de verificación es: *123456*

Si recibes este mensaje, ¡la integración funciona perfectamente! ✅

🚀 UBIKHA + WhatsApp"""
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:3000/api/whatsapp/send-message",
                json=payload
            )
            
            print(f"\n📊 Resultado:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ ¡MENSAJE ENVIADO EXITOSAMENTE!")
                    print("📱 Revisa tu WhatsApp para ver el mensaje")
                    print("\n🎉 ¡Tu integración WhatsApp + UBIKHA funciona perfectamente!")
                else:
                    print(f"❌ Error en respuesta: {result}")
            else:
                error_text = response.text
                print(f"❌ Error: {error_text}")
                
                if "no encontrado en WhatsApp" in error_text:
                    print("\n💡 POSIBLES SOLUCIONES:")
                    print("   1. Verifica que el número esté correcto")
                    print("   2. Asegúrate de que WhatsApp esté instalado en ese número")
                    print("   3. El número debe tener WhatsApp activo")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_real_number())
