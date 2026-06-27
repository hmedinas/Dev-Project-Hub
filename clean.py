"""
Script simple para eliminar la base de datos existente.
"""
import os
import sys

DB_PATH = "projects.db"

def main():
    if os.path.exists(DB_PATH):
        print(f"Eliminando base de datos existente: {DB_PATH}")
        try:
            os.remove(DB_PATH)
            print(f"¡Base de datos eliminada exitosamente!")
            print("Ahora puedes ejecutar 'python main.py' para iniciar con una BD limpia.")
        except Exception as e:
            print(f"Error al eliminar la base de datos: {e}")
            return 1
    else:
        print(f"No se encontró la base de datos en {DB_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())