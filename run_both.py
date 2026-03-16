import subprocess

python_emociones = r"C:\Users\dulce\LECTURA\env_emociones\Scripts\python.exe"
python_eye = r"C:\Users\dulce\LECTURA\env_eye\Scripts\python.exe"

script_emociones = r"C:\Users\dulce\LECTURA\emociones.py"
script_eye = r"C:\Users\dulce\LECTURA\eyetracking.py"

proc_eye = subprocess.Popen([python_eye, script_eye])
proc_emociones = subprocess.Popen([python_emociones, script_emociones])

proc_emociones.wait()
proc_eye.wait()