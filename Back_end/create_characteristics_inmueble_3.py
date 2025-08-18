import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def create_characteristics_for_inmueble_3():
    try:
        # Conectar a la base de datos
        database_url = os.getenv("DATABASE_URL")
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        print("\n" + "="*60)
        
        # Verificar si ya existen características para el inmueble ID 3
        check_query = """
        SELECT EXISTS(
            SELECT 1 FROM caracteristicas_inmueble WHERE id_inmueble = $1
        );
        """
        
        exists = await conn.fetchval(check_query, 3)
        
        if exists:
            print("⚠️  Ya existen características para el inmueble ID 3")
        else:
            print("🔧 Creando características para inmueble ID 3...")
            
            # Insertar características por defecto
            insert_query = """
            INSERT INTO caracteristicas_inmueble (
                id_inmueble, direccion, referencias, habitaciones, camas, banos, capacidad,
                wifi, cocina, estacionamiento, mascotas_permitidas, camaras_seguridad,
                television, aire_acondicionado, servicio_lavanderia
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
            );
            """
            
            await conn.execute(
                insert_query,
                3,  # id_inmueble
                "Puerto Maldonado, Madre de Dios",  # direccion
                "Cerca del malecón, vista al río",  # referencias
                2,  # habitaciones
                2,  # camas
                1,  # banos
                4,  # capacidad
                True,  # wifi
                True,  # cocina
                False,  # estacionamiento
                True,  # mascotas_permitidas
                False,  # camaras_seguridad
                True,  # television
                False,  # aire_acondicionado
                False   # servicio_lavanderia
            )
            
            print("✅ Características creadas exitosamente!")
            
            # Verificar los datos insertados
            verify_query = """
            SELECT * FROM caracteristicas_inmueble WHERE id_inmueble = $1;
            """
            
            resultado = await conn.fetchrow(verify_query, 3)
            
            print("\n📋 Características creadas:")
            print("-" * 40)
            for key, value in resultado.items():
                print(f"   {key}: {value}")
        
        await conn.close()
        print("\n✅ Proceso completado")
        print("\n💡 Ahora puedes probar GET /inmuebles/3 en Swagger")
        
    except Exception as e:
        print(f"❌ Error al crear características: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_characteristics_for_inmueble_3())
