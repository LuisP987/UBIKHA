import asyncio
import asyncpg
import json
from datetime import date
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_user_creation():
    try:
        # Conectar a la base de datos
        database_url = os.getenv("DATABASE_URL")
        asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        
        print("✅ Conexión exitosa a la base de datos")
        
        # Verificar la estructura de la tabla usuarios
        query_columns = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'usuarios'
        ORDER BY ordinal_position;
        """
        
        columns = await conn.fetch(query_columns)
        
        print("\n📊 Estructura actual de la tabla 'usuarios':")
        print("-" * 80)
        print(f"{'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 80)
        
        column_names = []
        for col in columns:
            column_names.append(col['column_name'])
            print(f"{col['column_name']:<25} {col['data_type']:<20} {col['is_nullable']:<10} {str(col['column_default'] or ''):<20}")
        
        # Verificar qué campos están faltando
        campos_codigo = [
            'telefono_verificado', 'celular_verificado', 'codigo_verificacion',
            'fecha_registro', 'fecha_actualizacion', 'tipo_usuario', 'activo'
        ]
        
        print(f"\n🔍 Verificando campos del código:")
        for campo in campos_codigo:
            existe = campo in column_names
            status = "✅" if existe else "❌"
            print(f"{status} {campo}: {'EXISTS' if existe else 'MISSING'}")
        
        # Simular inserción de datos como en el endpoint
        print(f"\n🧪 Simulando inserción de datos...")
        datos_usuario = {
            'email': 'test@example.com',
            'nombres': 'Test',
            'apellido_paterno': 'User',
            'apellido_materno': 'Example',
            'num_celular': '950205006',
            'fecha_nacimiento': date(2004, 8, 17),
            'password': 'hashed_password_example',
            'telefono_verificado': True,  # Este campo puede no existir
            'celular_verificado': True,
            'tipo_usuario': 'arrendatario'
        }
        
        # Filtrar solo los campos que existen en la BD
        campos_validos = {k: v for k, v in datos_usuario.items() if k in column_names}
        campos_faltantes = {k: v for k, v in datos_usuario.items() if k not in column_names}
        
        print(f"\n✅ Campos válidos para insertar:")
        for k, v in campos_validos.items():
            print(f"  - {k}: {v}")
            
        print(f"\n❌ Campos que faltan en la BD:")
        for k, v in campos_faltantes.items():
            print(f"  - {k}: {v}")
        
        await conn.close()
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_creation())
