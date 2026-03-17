import cv2
from fer import FER
import csv
from datetime import datetime
import time
import zmq
import base64

# ---- COMUNICACIÓN ZMQ ----
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5555")

# ---- DETECTOR ----
detector = FER()

traduccion = {
    "angry": "enojado",
    "disgust": "disgusto",
    "fear": "miedo",
    "happy": "feliz",
    "sad": "triste",
    "surprise": "sorpresa",
    "neutral": "neutral"
}

nombre_csv = f"emociones_{datetime.now().strftime('%d%m_%H%M')}.csv"

with open(nombre_csv, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "contador","timestamp","emocion_principal","confianza",
        "segunda_emocion","confianza_segunda"
    ])

cap = cv2.VideoCapture(0)

ultimo = time.time()
contador = 1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---- ENVIAR FRAME A EYE TRACKING ----
    _, buffer = cv2.imencode(".jpg", frame)
    frame_b64 = base64.b64encode(buffer)
    socket.send(frame_b64)

    # ---- SOLO 1 VEZ POR SEGUNDO ----
    ahora = time.time()
    if ahora - ultimo < 1:
        continue
    ultimo = ahora

    emociones = detector.detect_emotions(frame)
    timestamp = datetime.now().strftime("%d-%m-%y.%H.%M.%S")

    # ==========================================
    #   SI NO DETECTA ROSTRO
    # ==========================================
    if not emociones:
        with open(nombre_csv, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                contador,
                timestamp,
                "No detectado",
                0,
                "No detectado",
                0
            ])
        contador += 1
        continue  # <-- este solo salta esta iteración, NO bloquea código

    # ==========================================
    #   PROCESO NORMAL DE EMOCIONES
    # ==========================================
    data = emociones[0]["emotions"]
    orden = sorted(data.items(), key=lambda x: x[1], reverse=True)

    emocion1_en, conf1 = orden[0]
    emocion2_en, conf2 = orden[1]

    emocion1 = traduccion.get(emocion1_en, emocion1_en)
    emocion2 = traduccion.get(emocion2_en, emocion2_en)

    with open(nombre_csv, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            contador,
            timestamp,
            emocion1,
            conf1,
            emocion2,
            conf2
        ])

    contador += 1

cap.release()
cv2.destroyAllWindows()