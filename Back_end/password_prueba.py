import bcrypt

contraseña = "prueba321"
hash = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
print(hash.decode())
