import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def check_caracteristicas_inmueble_table():
    try:
        # Conectar a la base de datos
        database_url = os.getenv("DATABASE_URL")
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        print("\n" + "="*60)
        
        # Verificar si la tabla caracteristicas_inmueble existe
        query_table_exists = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'caracteristicas_inmueble'
        );
        """
        
        table_exists = await conn.fetchval(query_table_exists)
        print(f"📋 Tabla 'caracteristicas_inmueble' existe: {table_exists}")
        
        if table_exists:
            # Obtener la estructura de la tabla caracteristicas_inmueble
            query_columns = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'caracteristicas_inmueble'
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(query_columns)
            
            print("\n📊 Estructura actual de la tabla 'caracteristicas_inmueble':")
            print("-" * 80)
            print(f"{'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'Default':<20}")
            print("-" * 80)
            
            column_names = []
            for col in columns:
                column_names.append(col['column_name'])
                print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")
            
            # Verificar qué campos están faltando en el modelo
            campos_modelo = [
                'id_caracteristica', 'id_inmueble', 'direccion', 'referencias',
                'habitaciones', 'camas', 'banos', 'capacidad', 'wifi', 'cocina',
                'estacionamiento', 'mascotas_permitidas', 'camaras_seguridad',
                'television', 'aire_acondicionado', 'servicio_lavanderia'
            ]
            
            print("\n🔍 Verificando campos del modelo vs BD:")
            print("-" * 60)
            for campo in campos_modelo:
                existe = campo in column_names
                status = "✅" if existe else "❌"
                print(f"{status} {campo:<25}: {'EXISTS' if existe else 'MISSING'}")
            
            # Mostrar campos adicionales en la BD que no están en el modelo
            campos_extra = [col for col in column_names if col not in campos_modelo]
            if campos_extra:
                print("\n📝 Campos adicionales en la BD (no en el modelo):")
                for campo in campos_extra:
                    print(f"  + {campo}")
            
            # Contar registros
            count_query = "SELECT COUNT(*) FROM caracteristicas_inmueble;"
            count = await conn.fetchval(count_query)
            print(f"\n📈 Total de registros en caracteristicas_inmueble: {count}")
            
            # Si hay registros, mostrar algunos ejemplos
            if count > 0:
                sample_query = "SELECT * FROM caracteristicas_inmueble LIMIT 2;"
                samples = await conn.fetch(sample_query)
                print(f"\n📝 Primeros {len(samples)} registros:")
                for i, record in enumerate(samples, 1):
                    print(f"  {i}. {dict(record)}")
        
        else:
            print("❌ La tabla 'caracteristicas_inmueble' no existe en la base de datos")
        
        await conn.close()
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error al verificar la tabla caracteristicas_inmueble: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_caracteristicas_inmueble_table())
