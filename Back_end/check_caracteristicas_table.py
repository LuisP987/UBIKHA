import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import re

async def check_caracteristicas_table():
    load_dotenv()
    
    # Parsear DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No se encontró DATABASE_URL en .env")
        return
    
    # Extraer componentes de la URL
    # postgresql+asyncpg://admin-a:alexander123@26.196.154.46:5432/ubikha_db
    pattern = r'postgresql\+asyncpg://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, database_url)
    
    if not match:
        print("❌ Formato de DATABASE_URL inválido")
        return
    
    user, password, host, port, database = match.groups()
    
    print(f"🔗 Conectando a: {host}:{port}/{database} como {user}")
    
    # Conexión a la base de datos
    conn = await asyncpg.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database
    )
    
    try:
        print("🔍 VERIFICANDO TABLA: caracteristicas_inmueble")
        print("=" * 50)
        
        # Verificar si la tabla existe
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'caracteristicas_inmueble'
            );
        """)
        
        if table_exists:
            print("✅ La tabla 'caracteristicas_inmueble' existe")
            
            # Obtener estructura de la tabla
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'caracteristicas_inmueble'
                ORDER BY ordinal_position;
            """)
            
            print("\n📋 COLUMNAS EN LA TABLA:")
            print("-" * 50)
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT: {col['column_default']}" if col['column_default'] else ""
                print(f"• {col['column_name']} ({col['data_type']}) {nullable}{default}")
            
            # Verificar datos de ejemplo
            sample_data = await conn.fetch("""
                SELECT * FROM caracteristicas_inmueble LIMIT 3;
            """)
            
            if sample_data:
                print(f"\n📊 DATOS DE EJEMPLO ({len(sample_data)} registros):")
                print("-" * 50)
                for i, row in enumerate(sample_data, 1):
                    print(f"Registro {i}: {dict(row)}")
            else:
                print("\n⚠️  No hay datos en la tabla caracteristicas_inmueble")
                
        else:
            print("❌ La tabla 'caracteristicas_inmueble' NO existe")
            
            # Verificar qué tablas relacionadas existen
            related_tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%inmueble%'
                ORDER BY table_name;
            """)
            
            print("\n🔍 TABLAS RELACIONADAS CON 'inmueble':")
            for table in related_tables:
                print(f"• {table['table_name']}")
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_caracteristicas_table())
