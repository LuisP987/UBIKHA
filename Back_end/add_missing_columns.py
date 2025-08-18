"""
Script para agregar las columnas faltantes a la tabla caracteristicas_inmueble
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def add_missing_columns():
    try:
        # Conectar a la base de datos
        database_url = os.getenv("DATABASE_URL")
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        print("\n" + "="*60)
        
        # Lista de columnas a agregar
        columns_to_add = [
            ("referencias", "VARCHAR(255)", "Referencias adicionales de ubicación"),
            ("television", "BOOLEAN DEFAULT FALSE", "¿Tiene televisión?"),
            ("aire_acondicionado", "BOOLEAN DEFAULT FALSE", "¿Tiene aire acondicionado?"),
            ("servicio_lavanderia", "BOOLEAN DEFAULT FALSE", "¿Tiene servicio de lavandería?")
        ]
        
        print("🔧 Agregando columnas faltantes a 'caracteristicas_inmueble':")
        print("-" * 60)
        
        for column_name, column_type, description in columns_to_add:
            try:
                # Verificar si la columna ya existe
                check_query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'caracteristicas_inmueble'
                    AND column_name = $1
                );
                """
                
                exists = await conn.fetchval(check_query, column_name)
                
                if exists:
                    print(f"⚠️  {column_name:<20}: YA EXISTE - omitiendo")
                else:
                    # Agregar la columna
                    alter_query = f"""
                    ALTER TABLE caracteristicas_inmueble 
                    ADD COLUMN {column_name} {column_type};
                    """
                    
                    await conn.execute(alter_query)
                    print(f"✅ {column_name:<20}: AGREGADA - {description}")
                    
            except Exception as e:
                print(f"❌ {column_name:<20}: ERROR - {str(e)}")
        
        print("\n🔍 Verificando estructura final de la tabla:")
        print("-" * 60)
        
        # Verificar la estructura final
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
        
        print(f"{'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 80)
        
        for col in columns:
            print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")
        
        await conn.close()
        print("\n✅ Proceso completado exitosamente!")
        print("\n💡 Ahora puedes:")
        print("   1. Restaurar los campos en el modelo CaracteristicasInmueble")
        print("   2. Restaurar los campos en los schemas")
        print("   3. Restaurar los campos en el endpoint de creación")
        print("   4. Reiniciar el servidor FastAPI")
        
    except Exception as e:
        print(f"❌ Error al agregar columnas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_missing_columns())
