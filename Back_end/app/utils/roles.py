"""
Utilidades para manejo de roles múltiples en UBIKHA
"""

def tiene_rol(usuario, rol_buscado: str) -> bool:
    """
    Verifica si un usuario tiene un rol específico.
    Maneja tanto roles simples como múltiples (separados por coma).
    
    Args:
        usuario: Objeto usuario con campo tipo_usuario
        rol_buscado: Rol a verificar (ej: "arrendatario", "arrendador")
        
    Returns:
        bool: True si el usuario tiene el rol, False en caso contrario
    """
    if not usuario or not usuario.tipo_usuario:
        return False
    
    roles = [rol.strip() for rol in usuario.tipo_usuario.split(',')]
    return rol_buscado in roles

def obtener_roles(usuario) -> list[str]:
    """
    Obtiene todos los roles de un usuario como una lista.
    
    Args:
        usuario: Objeto usuario con campo tipo_usuario
        
    Returns:
        list[str]: Lista de roles del usuario
    """
    if not usuario or not usuario.tipo_usuario:
        return []
    
    return [rol.strip() for rol in usuario.tipo_usuario.split(',') if rol.strip()]

def es_arrendatario(usuario) -> bool:
    """Verifica si el usuario tiene rol de arrendatario"""
    return tiene_rol(usuario, "arrendatario")

def es_arrendador(usuario) -> bool:
    """Verifica si el usuario tiene rol de arrendador"""
    return tiene_rol(usuario, "arrendador")

def agregar_rol(tipo_usuario_actual: str, nuevo_rol: str) -> str:
    """
    Agrega un nuevo rol a los roles existentes sin duplicar.
    
    Args:
        tipo_usuario_actual: String actual de roles
        nuevo_rol: Nuevo rol a agregar
        
    Returns:
        str: String de roles actualizado
    """
    if not tipo_usuario_actual:
        return nuevo_rol
    
    roles_actuales = [rol.strip() for rol in tipo_usuario_actual.split(',') if rol.strip()]
    
    if nuevo_rol not in roles_actuales:
        roles_actuales.append(nuevo_rol)
    
    return ','.join(roles_actuales)

def remover_rol(tipo_usuario_actual: str, rol_a_remover: str) -> str:
    """
    Remueve un rol específico de los roles existentes.
    
    Args:
        tipo_usuario_actual: String actual de roles
        rol_a_remover: Rol a remover
        
    Returns:
        str: String de roles actualizado
    """
    if not tipo_usuario_actual:
        return ""
    
    roles_actuales = [rol.strip() for rol in tipo_usuario_actual.split(',') if rol.strip()]
    roles_filtrados = [rol for rol in roles_actuales if rol != rol_a_remover]
    
    return ','.join(roles_filtrados) if roles_filtrados else "arrendatario"  # Por defecto arrendatario
