@echo off
:: 1. Entramos a la carpeta del proyecto
cd /d "C:\HMEDINAS\PERSONAL\03- GITHUB\Dev-Project-Hub"

:: 2. Activamos el entorno (Asegúrate de que la carpeta se llame venv o .venv)
:: Si la creaste como venv (sin punto), usa esta línea:
call venv\Scripts\activate.bat

:: 3. Ejecutamos el script
:: Usamos python.exe (con ventana) para ver si hay errores, o pythonw.exe (sin ventana)
start /b venv\Scripts\pythonw.exe main.py

exit