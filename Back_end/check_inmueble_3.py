import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def check_inmueble_3():
    try:
        # Conectar a la base de datos
        database_url = os.getenv("DATABASE_URL")
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        print("\n" + "="*60)
        
        # Verificar si existe el inmueble con ID 3
        query_inmueble = """
        SELECT * FROM inmuebles WHERE id_inmueble = $1;
        """
        
        inmueble = await conn.fetchrow(query_inmueble, 3)
        
        if inmueble:
            print("✅ INMUEBLE ID 3 ENCONTRADO:")
            print("-" * 40)
            for key, value in inmueble.items():
                print(f"   {key}: {value}")
            
            # Verificar si tiene características
            query_caracteristicas = """
            SELECT * FROM caracteristicas_inmueble WHERE id_inmueble = $1;
            """
            
            caracteristicas = await conn.fetchrow(query_caracteristicas, 3)
            
            if caracteristicas:
                print("\n✅ CARACTERÍSTICAS ENCONTRADAS:")
                print("-" * 40)
                for key, value in caracteristicas.items():
                    print(f"   {key}: {value}")
            else:
                print("\n❌ NO HAY CARACTERÍSTICAS para inmueble ID 3")
                print("   Esto puede causar problemas en el endpoint")
                
        else:
            print("❌ INMUEBLE ID 3 NO ENCONTRADO")
            
            # Mostrar inmuebles disponibles
            query_all = "SELECT id_inmueble, titulo FROM inmuebles ORDER BY id_inmueble;"
            inmuebles = await conn.fetch(query_all)
            
            if inmuebles:
                print("\n📋 INMUEBLES DISPONIBLES:")
                print("-" * 40)
                for inmueble in inmuebles:
                    print(f"   ID {inmueble['id_inmueble']}: {inmueble['titulo']}")
            else:
                print("\n❌ NO HAY INMUEBLES EN LA BASE DE DATOS")
        
        await conn.close()
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error al verificar inmueble: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_inmueble_3())
