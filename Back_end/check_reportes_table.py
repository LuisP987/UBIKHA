import asyncio
from app.db.database import engine
from sqlalchemy import text

async def check_reportes_table():
    async with engine.connect() as conn:
        try:
            print("🔍 Verificando estructura de la tabla 'reportes'...")
            
            # Describir la estructura de la tabla reportes
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'reportes' 
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            print("\n📋 Columnas en la tabla reportes:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
                
            # Verificar si existe la columna motivo específicamente
            motivo_check = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reportes' AND column_name = 'motivo'
            """))
            motivo_exists = motivo_check.fetchone()
            
            print(f"\n❓ ¿Existe la columna 'motivo'? {motivo_exists is not None}")
            
            if not motivo_exists:
                print("\n⚠️  PROBLEMA ENCONTRADO: La columna 'motivo' NO existe en la tabla 'reportes'")
                print("💡 Esto explica el error al eliminar usuarios")
            
        except Exception as e:
            print(f"❌ Error al verificar la tabla reportes: {e}")

if __name__ == "__main__":
    asyncio.run(check_reportes_table())
