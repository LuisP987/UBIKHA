#!/usr/bin/env python3
"""
Script para probar el servidor rápidamente
"""
import asyncio
import sys
import os

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_server():
    print("🚀 Iniciando pruebas del servidor...")
    
    try:
        # Importar la aplicación
        from main import app
        print("✅ Aplicación importada correctamente")
        
        # Verificar que los routers estén configurados
        routes = [route.path for route in app.routes]
        auth_routes = [route for route in routes if '/auth' in route]
        
        print(f"📋 Rutas de autenticación encontradas: {len(auth_routes)}")
        for route in auth_routes:
            print(f"   - {route}")
            
        # Verificar importaciones específicas
        from api.auth import router as auth_router
        from schemas.user import UsuarioPerfilCompleto, UsuarioMostrar, UsuarioActualizar
        from utils.security.error_messages import AuthErrorMessages
        
        print("✅ Todos los esquemas y clases importados correctamente")
        print("🎉 El servidor está listo para ser ejecutado!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    if not success:
        sys.exit(1)
    print("\n📝 Para iniciar el servidor, ejecuta:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
