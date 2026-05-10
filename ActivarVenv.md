## creando enlaces sinbolicos
```powershell
New-Item -ItemType SymbolicLink -Path "C:\Python311\python311.exe" -Value "C:\Python311\python.exe"
New-Item -ItemType SymbolicLink -Path "C:\Python313\python3.exe" -Value "C:\Python313\python.exe"

```

## configrar los alisas en winwod
Esto solo se hace desde la version 3 en adelante 

asi puedo configrurar los alias



```powershell
$ Set-Alias -Name python3 -Value C:\Python313\python3.exe

$ Set-Alias -Name python311 -Value C:\Python313\python311.exe

```


## para activar en windows en venv

```python
python3 -m venv venv
# activar el enviromen si no deja hacer esto 
.\venv\Scripts\activate

# si no te dejea cativar en woindows 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# le das si a todo 
.\venv\Scripts\activate

# saber que version de python tengo y si esta activado 
which python
# o
Get-Command python | Select-Object -ExpandProperty Source

# despues insyalar los paquetes 
pip list 

pip install -r requirements.txt

```

## despues si lo quieres enviar como un bat


```bat
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

```