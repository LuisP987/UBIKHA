import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def check_reportes_table():
    try:
        # Obtener la URL de la base de datos del .env
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            print("❌ No se encontró DATABASE_URL en el archivo .env")
            return
            
        # Convertir la URL para asyncpg (quitar +asyncpg)
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        print(f"🔗 Conectando a: {asyncpg_url.replace('alexander123', '****')}")
        
        # Conectar usando la URL directamente
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        print("\n" + "="*60)
        
        # Verificar si la tabla reportes existe
        query_table_exists = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'reportes'
        );
        """
        
        table_exists = await conn.fetchval(query_table_exists)
        print(f"📋 Tabla 'reportes' existe: {table_exists}")
        
        if table_exists:
            # Obtener la estructura de la tabla reportes
            query_columns = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'reportes'
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(query_columns)
            
            print("\n📊 Estructura actual de la tabla 'reportes':")
            print("-" * 80)
            print(f"{'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'Default':<20}")
            print("-" * 80)
            
            for col in columns:
                print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")
            
            # Verificar específicamente la columna comentario_admin
            column_exists = any(col['column_name'] == 'comentario_admin' for col in columns)
            print(f"\n🔍 Columna 'comentario_admin' existe: {column_exists}")
            
            # Contar registros
            count_query = "SELECT COUNT(*) FROM reportes;"
            count = await conn.fetchval(count_query)
            print(f"📈 Total de registros en reportes: {count}")
            
            # Si hay registros, mostrar algunos ejemplos
            if count > 0:
                sample_query = "SELECT * FROM reportes LIMIT 3;"
                samples = await conn.fetch(sample_query)
                print(f"\n📝 Primeros {len(samples)} registros:")
                for i, record in enumerate(samples, 1):
                    print(f"  {i}. {dict(record)}")
        
        else:
            print("❌ La tabla 'reportes' no existe en la base de datos")
            
            # Mostrar todas las tablas existentes
            query_all_tables = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
            """
            
            tables = await conn.fetch(query_all_tables)
            print("\n📋 Tablas existentes en la base de datos:")
            for table in tables:
                print(f"  - {table['table_name']}")
        
        await conn.close()
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error al verificar la tabla reportes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_reportes_table())
