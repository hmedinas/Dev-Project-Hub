"""
migrate_db.py  —  Dev Project Hub
Script de migración para actualizar la estructura de la base de datos y preservar los datos existentes.
"""

import os
import sqlite3
import shutil
from datetime import datetime

# Ruta de la base de datos
DB_PATH = "projects.db"
BACKUP_PATH = f"projects_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def migrate_database():
    """
    Migra la base de datos a la nueva estructura:
    1. Crea una copia de seguridad
    2. Altera la tabla proyectos para añadir nuevas columnas
    3. Migra los datos de las columnas antiguas a las nuevas
    """
    # Crear backup
    print(f"Creando copia de seguridad en {BACKUP_PATH}...")
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"Backup creado en {BACKUP_PATH}")
    else:
        print("No se encontró la base de datos. Se creará una nueva.")
        return

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Iniciando migración de la base de datos...")
        
        # Comprobar si la tabla tiene el nuevo esquema (verificar si ya se migró)
        cursor.execute("PRAGMA table_info(proyectos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Verificar si ya se ha migrado
        if "ruta_front" in columns:
            print("La base de datos ya tiene la nueva estructura. No se requiere migración.")
            return
        
        # Añadir nuevas columnas para las URLs de GitHub
        print("Añadiendo columnas para URLs de GitHub...")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN url_github_front TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN url_github_back TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN url_github_global TEXT")
        
        # Añadir nuevas columnas para los tipos de proyecto
        print("Añadiendo columnas para rutas y descripciones por tipo de proyecto...")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN ruta_front TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN ruta_back TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN ruta_global TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN desc_front TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN desc_back TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN desc_global TEXT")
        
        # Añadir columnas para lenguajes por repositorio
        print("Añadiendo columnas para lenguajes específicos por repositorio...")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN lenguaje_front TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN lenguaje_back TEXT")
        cursor.execute("ALTER TABLE proyectos ADD COLUMN lenguaje_global TEXT")
        
        # Migrar datos de las columnas antiguas a las nuevas
        print("Migrando datos existentes al nuevo esquema...")
        cursor.execute("""
            UPDATE proyectos 
            SET 
                url_github_front = url_github,
                ruta_front = ruta_dev, 
                ruta_back = ruta_test,
                ruta_global = ruta_pro,
                desc_front = desc_dev,
                desc_back = desc_test,
                desc_global = desc_pro,
                lenguaje_front = lenguaje,
                lenguaje_back = lenguaje,
                lenguaje_global = lenguaje
        """)
        
        # Guardar cambios
        conn.commit()
        print("Migración completada con éxito.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error durante la migración: {e}")
        print(f"Se restaurará la base de datos desde el backup {BACKUP_PATH}...")
        conn.close()
        if os.path.exists(BACKUP_PATH):
            shutil.copy2(BACKUP_PATH, DB_PATH)
            print("Restauración completada.")
        else:
            print("¡ALERTA! No se pudo encontrar el archivo de backup para restaurar.")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== MIGRACIÓN DE LA BASE DE DATOS DEV PROJECT HUB ===")
    print("Este script actualizará la estructura de la base de datos para soportar:")
    print("- URLs de GitHub independientes para FRONT, BACK y GLOBAL")
    print("- Cambio de rutas DEV/TEST/PRO a FRONT/BACK/GLOBAL")
    print()
    print("Se creará una copia de seguridad antes de realizar cualquier cambio.")
    print()
    
    respuesta = input("¿Desea continuar con la migración? (s/N): ").strip().lower()
    
    if respuesta == 's':
        migrate_database()
        print()
        print("Proceso de migración finalizado.")
    else:
        print("Migración cancelada.")