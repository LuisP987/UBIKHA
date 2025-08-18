#!/usr/bin/env python3
"""
Script para verificar todas las dependencias de un usuario antes de eliminarlo
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def verificar_dependencias_usuario(email_usuario):
    """Verifica todas las dependencias de un usuario específico"""
    print(f"🔍 Verificando dependencias del usuario: {email_usuario}")
    
    try:
        # Obtener URL de la base de datos
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ No se encontró DATABASE_URL en .env")
            return
        
        # Convertir URL para asyncpg
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        # Conectar a la base de datos
        conn = await asyncpg.connect(asyncpg_url)
        print("✅ Conexión establecida con la base de datos")
        
        # Obtener el ID del usuario
        usuario = await conn.fetchrow("""
            SELECT id_usuario, nombres, apellido_paterno, email, tipo_usuario
            FROM usuarios 
            WHERE email = $1
        """, email_usuario)
        
        if not usuario:
            print(f"❌ Usuario con email '{email_usuario}' no encontrado")
            return
        
        user_id = usuario['id_usuario']
        print(f"\n👤 Usuario encontrado:")
        print(f"  ID: {user_id}")
        print(f"  Nombre: {usuario['nombres']} {usuario['apellido_paterno']}")
        print(f"  Email: {usuario['email']}")
        print(f"  Tipo: {usuario['tipo_usuario']}")
        
        # Verificar inmuebles del usuario
        print(f"\n🏠 Inmuebles del usuario:")
        inmuebles = await conn.fetch("""
            SELECT id_inmueble, titulo, estado 
            FROM inmuebles 
            WHERE id_propietario = $1
        """, user_id)
        
        inmuebles_ids = [inmueble['id_inmueble'] for inmueble in inmuebles]
        print(f"  Total inmuebles: {len(inmuebles)}")
        
        for inmueble in inmuebles:
            print(f"    🏠 ID: {inmueble['id_inmueble']} | {inmueble['titulo']} | Estado: {inmueble['estado']}")
        
        # Verificar dependencias una por una
        dependencias = {}
        
        # 1. Mensajes
        mensajes_enviados = await conn.fetchval("SELECT COUNT(*) FROM mensajes WHERE id_remitente = $1", user_id)
        mensajes_recibidos = await conn.fetchval("SELECT COUNT(*) FROM mensajes WHERE id_destinatario = $1", user_id)
        dependencias['mensajes'] = mensajes_enviados + mensajes_recibidos
        
        # 2. Características de inmuebles
        if inmuebles_ids:
            caracteristicas = await conn.fetchval("SELECT COUNT(*) FROM caracteristicas_inmueble WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            caracteristicas = 0
        dependencias['caracteristicas_inmueble'] = caracteristicas
        
        # 3. Reportes
        reportes_hechos = await conn.fetchval("SELECT COUNT(*) FROM reportes WHERE id_usuario = $1", user_id)
        if inmuebles_ids:
            reportes_recibidos = await conn.fetchval("SELECT COUNT(*) FROM reportes WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            reportes_recibidos = 0
        dependencias['reportes'] = reportes_hechos + reportes_recibidos
        
        # 4. Reservas
        reservas_hechas = await conn.fetchval("SELECT COUNT(*) FROM reservas WHERE id_usuario = $1", user_id)
        if inmuebles_ids:
            reservas_recibidas = await conn.fetchval("SELECT COUNT(*) FROM reservas WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            reservas_recibidas = 0
        dependencias['reservas'] = reservas_hechas + reservas_recibidas
        
        # 5. Reseñas
        resenas_hechas = await conn.fetchval("SELECT COUNT(*) FROM resenas WHERE id_usuario = $1", user_id)
        if inmuebles_ids:
            resenas_recibidas = await conn.fetchval("SELECT COUNT(*) FROM resenas WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            resenas_recibidas = 0
        dependencias['resenas'] = resenas_hechas + resenas_recibidas
        
        # 6. Imágenes de inmuebles
        if inmuebles_ids:
            imagenes = await conn.fetchval("SELECT COUNT(*) FROM imagen_inmueble WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            imagenes = 0
        dependencias['imagenes'] = imagenes
        
        # 7. Favoritos
        favoritos_hechos = await conn.fetchval("SELECT COUNT(*) FROM favoritos WHERE id_usuario = $1", user_id)
        if inmuebles_ids:
            favoritos_recibidos = await conn.fetchval("SELECT COUNT(*) FROM favoritos WHERE id_inmueble = ANY($1)", inmuebles_ids)
        else:
            favoritos_recibidos = 0
        dependencias['favoritos'] = favoritos_hechos + favoritos_recibidos
        
        # 8. Notificaciones
        notificaciones = await conn.fetchval("SELECT COUNT(*) FROM notificaciones WHERE id_usuario = $1", user_id)
        dependencias['notificaciones'] = notificaciones
        
        print(f"\n📊 Resumen de dependencias:")
        total_dependencias = 0
        for tabla, cantidad in dependencias.items():
            if cantidad > 0:
                print(f"  🔗 {tabla}: {cantidad} registros")
                total_dependencias += cantidad
            else:
                print(f"  ✅ {tabla}: 0 registros")
        
        print(f"\n📈 Total registros dependientes: {total_dependencias}")
        
        if total_dependencias > 0:
            print("\n⚠️  Este usuario tiene dependencias que deben eliminarse primero")
        else:
            print("\n✅ Este usuario no tiene dependencias y puede eliminarse directamente")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Ingresa el email del usuario a verificar: ")
    
    asyncio.run(verificar_dependencias_usuario(email))
