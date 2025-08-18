#!/usr/bin/env python3
"""
Script para actualizar el sistema de roles múltiples en UBIKHA
- Modifica la columna tipo_usuario para soportar múltiples roles
- Actualiza usuarios existentes para mantener roles apropiados
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def actualizar_roles_multiples():
    """Actualiza el sistema para soportar roles múltiples"""
    print("🔧 Iniciando actualización del sistema de roles múltiples...")
    
    try:
        # Obtener URL de la base de datos
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ No se encontró DATABASE_URL en .env")
            return
        
        # Convertir URL para asyncpg
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        print(f"🔗 Conectando a: {asyncpg_url.replace('alexander123', '***')}")
        
        # Conectar a la base de datos
        conn = await asyncpg.connect(asyncpg_url)
        print("✅ Conexión establecida con la base de datos")
        
        # 1. Verificar usuarios actuales
        print("\n🔍 Verificando usuarios actuales:")
        usuarios = await conn.fetch("""
            SELECT id_usuario, nombres, apellido_paterno, tipo_usuario, email
            FROM usuarios 
            ORDER BY fecha_registro DESC 
            LIMIT 10
        """)
        
        for usuario in usuarios:
            print(f"  👤 ID: {usuario['id_usuario']} | {usuario['nombres']} {usuario['apellido_paterno']} | Rol: {usuario['tipo_usuario']}")
        
        # 2. Ampliar la columna tipo_usuario
        print("\n🔧 Ampliando columna tipo_usuario...")
        await conn.execute("""
            ALTER TABLE usuarios 
            ALTER COLUMN tipo_usuario TYPE VARCHAR(50);
        """)
        print("✅ Columna tipo_usuario ampliada a VARCHAR(50)")
        
        # 3. Verificar usuarios que tienen inmuebles
        print("\n🏠 Verificando usuarios con inmuebles:")
        usuarios_con_inmuebles = await conn.fetch("""
            SELECT DISTINCT u.id_usuario, u.nombres, u.apellido_paterno, u.tipo_usuario, COUNT(i.id_inmueble) as total_inmuebles
            FROM usuarios u
            INNER JOIN inmuebles i ON u.id_usuario = i.id_propietario
            GROUP BY u.id_usuario, u.nombres, u.apellido_paterno, u.tipo_usuario
            ORDER BY total_inmuebles DESC
        """)
        
        for usuario in usuarios_con_inmuebles:
            print(f"  🏠 {usuario['nombres']} {usuario['apellido_paterno']} | Rol actual: {usuario['tipo_usuario']} | Inmuebles: {usuario['total_inmuebles']}")
        
        # 4. Actualizar usuarios que son solo "arrendador" a "arrendatario,arrendador"
        print("\n🔄 Actualizando usuarios que son solo 'arrendador'...")
        resultado = await conn.execute("""
            UPDATE usuarios 
            SET tipo_usuario = 'arrendatario,arrendador'
            WHERE tipo_usuario = 'arrendador'
        """)
        print(f"✅ {resultado.split()[-1]} usuarios actualizados de 'arrendador' a 'arrendatario,arrendador'")
        
        # 5. Verificar el estado después de la actualización
        print("\n📊 Estado después de la actualización:")
        usuarios_actualizados = await conn.fetch("""
            SELECT tipo_usuario, COUNT(*) as cantidad
            FROM usuarios 
            GROUP BY tipo_usuario
            ORDER BY cantidad DESC
        """)
        
        for rol in usuarios_actualizados:
            print(f"  📈 Rol '{rol['tipo_usuario']}': {rol['cantidad']} usuarios")
        
        # 6. Verificar usuarios específicos
        print("\n🎯 Verificando usuario Alexander Suni (ID: 60):")
        alexander = await conn.fetchrow("""
            SELECT id_usuario, nombres, apellido_paterno, tipo_usuario, email
            FROM usuarios 
            WHERE id_usuario = 60
        """)
        
        if alexander:
            print(f"  👤 {alexander['nombres']} {alexander['apellido_paterno']} | Rol: {alexander['tipo_usuario']} | Email: {alexander['email']}")
            
            # Verificar si tiene inmuebles
            inmuebles_alexander = await conn.fetchval("""
                SELECT COUNT(*) FROM inmuebles WHERE id_propietario = 60
            """)
            print(f"  🏠 Inmuebles publicados: {inmuebles_alexander}")
        else:
            print("  ❌ Usuario Alexander Suni (ID: 60) no encontrado")
        
        await conn.close()
        print("\n🎉 ¡Actualización completada exitosamente!")
        print("\n📝 Resumen de cambios:")
        print("  ✅ Columna tipo_usuario ampliada a VARCHAR(50)")
        print("  ✅ Usuarios con rol 'arrendador' actualizados a 'arrendatario,arrendador'")
        print("  ✅ Sistema preparado para roles múltiples")
        
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(actualizar_roles_multiples())
