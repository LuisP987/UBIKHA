from Back_end.app.db.database import motor
import asyncio
print("aaaaaa")
async def probar_conexion():
    print("aaaaaa2")
    try:
        async with motor.connect() as conexion:
            print("CONEXION REALIZADA CON ÉXITO")
    except Exception as errores:
        print("CONEXION FALLIDA")
        print(errores)

if __name__ == "__main__":
    asyncio.run(probar_conexion())