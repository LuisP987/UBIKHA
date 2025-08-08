# utils/red.py

import socket
import requests
import os

def obtener_ip_local():
    """Obtiene la IP local de la máquina"""
    try:
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        return ip_local
    except:
        return "127.0.0.1"

def obtener_ip_publica():
    """Obtiene la IP pública (opcional)"""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=3)
        return response.json()["ip"]
    except:
        return "No disponible"

def imprimir_info_servidor():
    """Imprime las direcciones del servidor"""
    ip_local = obtener_ip_local()
    ip_publica = obtener_ip_publica()

    print("INFORMACIÓN DEL SERVIDOR:")
    print(f"IP Local: {ip_local}")
    print(f"IP Pública: {ip_publica}")
    print(f"URL Local: http://localhost:8000")
    print(f"URL Red: http://{ip_local}:8000")
    print(f"Swagger UI: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
