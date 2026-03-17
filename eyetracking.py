import cv2
import mediapipe as mp
import csv
from datetime import datetime
import time
import zmq
import base64
import numpy as np

# ---- RECIBIR FRAMES ----
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1)

# ---- ARCHIVO CSV ----
nombre_csv = f"eyetracking_{datetime.now().strftime('%d%m_%H%M')}.csv"
with open(nombre_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["contador","timestamp", "direccion", "retencion", "distraccion"])

ultimo = time.time()
contador = 1
retencion = 0
distraccion = 0

# ======== CALIBRACIÓN ========
calibrado = False
calib_samples = 0
CALIB_MAX = 30  # ~2 segundos a 15 fps

base_nose_x = 0
base_nose_y = 0
base_eye_top = 0
base_eye_bottom = 0


def obtener_direccion(landmarks):
    """
    Retorna: arriba / abajo / izquierda / derecha / frente
    con calibración automática.
    """

    global calibrado, calib_samples
    global base_nose_x, base_nose_y, base_eye_top, base_eye_bottom

    nose = landmarks[1]

    # puntos superiores e inferiores del párpado
    left_up = landmarks[159]
    left_down = landmarks[145]
    right_up = landmarks[386]
    right_down = landmarks[374]

    eye_top = (left_up.y + right_up.y) / 2
    eye_bottom = (left_down.y + right_down.y) / 2

    # ======== FASE DE CALIBRACIÓN ========
    if not calibrado:
        base_nose_x += nose.x
        base_nose_y += nose.y
        base_eye_top += eye_top
        base_eye_bottom += eye_bottom

        calib_samples += 1

        if calib_samples >= CALIB_MAX:
            base_nose_x /= calib_samples
            base_nose_y /= calib_samples
            base_eye_top /= calib_samples
            base_eye_bottom /= calib_samples
            calibrado = True
            print(">>> CALIBRACIÓN COMPLETA")

        return "frente"

    # ======== DETECCIÓN NORMAL ========
    umbral_v = 0.015
    umbral_h = 0.03

    # Horizontal
    if nose.x < base_nose_x - umbral_h:
        return "derecha"
    if nose.x > base_nose_x + umbral_h:
        return "izquierda"

    # Vertical
    if nose.y < base_nose_y - umbral_v:
        return "arriba"
    if nose.y > base_nose_y + umbral_v:
        return "abajo"

    return "frente"


# ==============================
# LOOP PRINCIPAL
# ==============================
while True:
    frame_b64 = socket.recv()
    img_bytes = base64.b64decode(frame_b64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = face_mesh.process(rgb)
    direccion = "desconocido"

    if res.multi_face_landmarks:
        direccion = obtener_direccion(res.multi_face_landmarks[0].landmark)

    ahora = time.time()

    if ahora - ultimo >= 1:
       
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if direccion == "frente":
            retencion += 1
        else:
            distraccion += 1

        with open(nombre_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                contador,
                timestamp,
                direccion,
                retencion,
                distraccion
            ])

        contador += 1
        ultimo = ahora