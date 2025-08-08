import os

def get_current_branch():
    branches = os.popen('git branch').read().splitlines()
    for branch in branches:
        if branch.startswith('*'):
            return branch.replace('*', '').strip()
    return 'main'

def main():
    rama = get_current_branch()
    print(f"Trayendo cambios de la rama: {rama}")
    os.system(f"git pull origin {rama}")
    print("¡Cambios actualizados correctamente!")

if __name__ == "__main__":
    main()
