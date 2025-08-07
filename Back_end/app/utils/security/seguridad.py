import bcrypt

def verificar_password(password_plana: str, password_hashed: str) -> bool:
    try:
        # Intentar verificar con bcrypt
        return bcrypt.checkpw(password_plana.encode('utf-8'), password_hashed.encode('utf-8'))
    except ValueError as e:
        # Si el hash no es válido (contraseña en texto plano o hash corrupto)
        if "Invalid salt" in str(e):
            # Verificar si la contraseña está en texto plano (comparación directa)
            return password_plana == password_hashed
        raise e  # Re-lanzar otros tipos de ValueError

def hashear_password(password_plano: str) -> str:
    return bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def es_password_hasheada(password: str) -> bool:
    """Verifica si una contraseña ya está hasheada con bcrypt"""
    try:
        # Los hashes de bcrypt empiezan con $2a$, $2b$, $2x$, o $2y$
        return password.startswith(('$2a$', '$2b$', '$2x$', '$2y$')) and len(password) == 60
    except Exception:
        return False
