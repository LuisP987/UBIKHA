"""
🚀 Script simple para probar WhatsApp Integration
"""

import asyncio
import httpx
import json

async def test_send_code():
    """Probar envío de código de verificación"""
    
    print("🧪 Probando envío de código de verificación...")
    
    # Datos de prueba
    phone_data = {"phone_number": "987654321"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/whatsapp-auth/enviar-codigo-registro",
                json=phone_data
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Código enviado exitosamente!")
                print(f"📱 Revisa tu WhatsApp para el código")
            else:
                print("❌ Error al enviar código")
                
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_whatsapp_direct():
    """Probar envío directo a WhatsApp API"""
    
    print("\n🧪 Probando envío directo a WhatsApp API...")
    
    # Mensaje de prueba
    payload = {
        "phone": "51987654321",
        "message": "🧪 Mensaje de prueba desde UBIKHA\n\nTu código de verificación es: *123456*\n\n¡Prueba exitosa! 🚀"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:3000/api/whatsapp/send-message",
                json=payload
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Mensaje enviado directamente a WhatsApp!")
                else:
                    print(f"❌ Error en respuesta: {result}")
            else:
                print("❌ Error en la petición")
                
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Función principal"""
    print("🚀 PRUEBAS DE INTEGRACIÓN WHATSAPP")
    print("=" * 50)
    
    # Primero probar directo a WhatsApp
    await test_whatsapp_direct()
    
    # Luego probar a través de UBIKHA
    await test_send_code()

if __name__ == "__main__":
    asyncio.run(main())
