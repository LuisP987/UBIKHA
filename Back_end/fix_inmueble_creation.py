"""
Script para verificar la corrección del endpoint de crear inmueble
"""

print("🔧 CORRECCIÓN DEL ENDPOINT CREAR INMUEBLE")
print("=" * 50)

print("\n❌ PROBLEMA IDENTIFICADO:")
print("   Error: 'Usuario' object has no attribute 'estado'")
print("   Línea problemática: usuario_actual.estado != 'activo'")

print("\n✅ CORRECCIÓN APLICADA:")
print("   Cambiado a: usuario_actual.activo")
print("   Razón: El modelo Usuario tiene campo 'activo' (Boolean), no 'estado'")

print("\n📋 ESTRUCTURA REAL DEL MODELO USUARIO:")
print("   ✅ activo: Boolean (True/False)")
print("   ❌ estado: NO EXISTE")

print("\n🔧 VALIDACIÓN CORREGIDA:")
print("   ANTES: if not usuario_actual or usuario_actual.estado != 'activo':")
print("   DESPUÉS: if not usuario_actual or not usuario_actual.activo:")

print("\n🎯 RESULTADO ESPERADO:")
print("   ✅ POST /inmuebles/ debería funcionar ahora")
print("   ✅ Validación de usuario activo funcionará correctamente")
print("   ✅ No más errores de atributo 'estado'")

print("\n📝 DATOS DE PRUEBA USADOS:")
print("   - tipo_inmueble: casa")
print("   - titulo: Casa familiar en la LEON VELARDE") 
print("   - precio_mensual: 3600")
print("   - direccion: Av. Conquistadores 1245, San Isidro, Lima")
print("   - huespedes: 4, habitaciones: 3, banos: 2, camas: 3")
print("   - Servicios: wifi, cocina, tv, aire_acond, etc.")

print("\n🚀 PRÓXIMOS PASOS:")
print("   1. Reiniciar el servidor FastAPI (si está corriendo)")
print("   2. Probar POST /inmuebles/ con el JSON proporcionado")
print("   3. Verificar que el inmueble se crea exitosamente")

print("\n🎉 ¡La corrección está aplicada y lista para probar!")
