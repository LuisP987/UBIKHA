import bcrypt

def verificar_password(password_plana: str, password_hashed: str) -> bool:
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hashed.encode('utf-8'))

def hashear_password(password_plano: str) -> str:
    return bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
