"""
reset_database.py — Dev Project Hub
Script para eliminar la base de datos actual y crear una nueva con la estructura correcta.
"""

import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, Proyecto

def reset_database():
    """
    Elimina la base de datos existente y crea una nueva con la estructura actualizada.
    """
    db_path = "projects.db"
    
    # Eliminar la base de datos si existe
    if os.path.exists(db_path):
        print(f"Eliminando base de datos existente: {db_path}")
        os.remove(db_path)
    
    # Crear una nueva base de datos con la estructura actualizada
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    
    print(f"Nueva base de datos creada con éxito: {db_path}")
    
    # Verificar la estructura de la tabla proyectos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(proyectos)")
    columns = cursor.fetchall()
    
    print("\nEstructura de la tabla proyectos:")
    for column in columns:
        print(f"  {column[1]} ({column[2]})")
    
    conn.close()

if __name__ == "__main__":
    print("=== REINICIO DE LA BASE DE DATOS DEV PROJECT HUB ===")
    print("Este script eliminará la base de datos actual y creará una nueva con la estructura correcta.")
    print("ADVERTENCIA: Todos los datos existentes se perderán.")
    
    respuesta = input("¿Desea continuar? (s/N): ").strip().lower()
    
    if respuesta == 's':
        reset_database()
        print("\nBase de datos reiniciada con éxito.")
    else:
        print("Operación cancelada. No se ha realizado ningún cambio.")