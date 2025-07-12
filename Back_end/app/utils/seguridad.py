import bcrypt

def verificar_password(password_plana: str, password_hashed: str) -> bool:
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hashed.encode('utf-8'))
