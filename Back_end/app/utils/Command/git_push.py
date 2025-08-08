import os

def get_current_branch():
    branches = os.popen('git branch').read().splitlines()
    for branch in branches:
        if branch.startswith('*'):
            return branch.replace('*', '').strip()
    return 'main'

def main():
    mensaje = input("Escribe el mensaje de commit: ")
    os.system("git add .")
    os.system(f'git commit -m "{mensaje}"')
    rama = get_current_branch()
    print(f"Subiendo cambios a la rama: {rama}")
    os.system(f"git push origin {rama}")
    print("¡Cambios subidos correctamente!")

if __name__ == "__main__":
    main()
