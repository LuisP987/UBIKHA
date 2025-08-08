#!/usr/bin/env python3
"""
Script de prueba para verificar que el servidor puede iniciarse correctamente
"""
import sys
import os

# Agregar el directorio actual al path para importar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    print("🔍 Verificando importaciones...")
    
    # Probar importar la aplicación principal
    from main import app
    print("✅ Importación de main.py exitosa")
    
    # Probar importar los módulos de autenticación
    from api.auth import router
    print("✅ Importación de auth.py exitosa")
    
    # Probar importar servicios
    from services.user import buscar_usuario_por_email, crear_usuario, actualizar_usuario
    print("✅ Importación de servicios de usuario exitosa")
    
    # Probar importar esquemas
    from schemas.user import UsuarioActualizar, UsuarioMostrar
    print("✅ Importación de esquemas exitosa")
    
    # Probar importar utilidades de seguridad
    from utils.security.jwt import crear_token, obtener_usuario_actual
    print("✅ Importación de JWT exitosa")
    
    from utils.security.error_messages import AuthErrorMessages
    print("✅ Importación de mensajes de error exitosa")
    
    print("\n🎉 ¡Todas las importaciones exitosas!")
    print("El servidor debería poder iniciarse sin problemas de importación.")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Revisa las dependencias y rutas de importación.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1)
