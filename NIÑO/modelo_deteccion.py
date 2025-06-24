import cv2
import mediapipe as mp
from scipy.spatial import distance as dist
from threading import Event
import time
import os
from datetime import datetime

# Parámetros
EYE_AR_THRESH = 0.20
EYE_AR_CONSEC_FRAMES = 48
DISTRACC_CONSEC_FRAMES = 48

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS = [469, 470, 471, 472]
RIGHT_IRIS = [474, 475, 476, 477]

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

stop_event = Event()
deteccion_finalizada = Event()
resultado_final = {}

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def get_iris_position(iris_points, eye_points):
    iris_center_x = sum([p[0] for p in iris_points]) / len(iris_points)
    eye_left = eye_points[0][0]
    eye_right = eye_points[3][0]
    pos = (iris_center_x - eye_left) / (eye_right - eye_left)

    if pos < 0.35:
        return "derecha"
    elif pos > 0.65:
        return "izquierda"
    else:
        return "centro"

def gen_frames(nino_id, nuevo_id):
    STATIC_CAPTURE_DIR = os.path.join('musica', 'capturas', str(nino_id), str(nuevo_id))
    os.makedirs(STATIC_CAPTURE_DIR, exist_ok=True)

    # Contadores y banderas
    COUNTER = 0
    COUNTERDISTRACC = 0
    conteo_somnolencia = 0
    conteo_distraccion = 0
    tiempos_somnolencia = []
    tiempos_distraccion = []
    rutas_frames_somnolencia = []
    rutas_frames_distraccion = []
    inicio_somnolencia = None
    inicio_distraccion = None
    somnolencia_en_progreso = False
    distraccion_en_progreso = False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {
            "somnolencias": 0,
            "distracciones": 0,
            "tiempos_somnolencia": [],
            "tiempos_distraccion": [],
            "frames_somnolencia": [],
            "frames_distraccion": [],
        }

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        now = time.time()

        if results.multi_face_landmarks:
            mesh = results.multi_face_landmarks[0].landmark

            left_eye = [(int(mesh[i].x * w), int(mesh[i].y * h)) for i in LEFT_EYE]
            right_eye = [(int(mesh[i].x * w), int(mesh[i].y * h)) for i in RIGHT_EYE]
            left_iris = [(int(mesh[i].x * w), int(mesh[i].y * h)) for i in LEFT_IRIS]
            right_iris = [(int(mesh[i].x * w), int(mesh[i].y * h)) for i in RIGHT_IRIS]

            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            mirada_izq = get_iris_position(left_iris, left_eye)
            mirada_der = get_iris_position(right_iris, right_eye)
            mirando_frente = mirada_izq == "centro" and mirada_der == "centro"

            # ---------- DISTRACTION ----------
            if not mirando_frente:
                if not distraccion_en_progreso:
                    COUNTERDISTRACC += 1
                    if COUNTERDISTRACC >= DISTRACC_CONSEC_FRAMES:
                        conteo_distraccion += 1
                        distraccion_en_progreso = True
                        inicio_distraccion = now

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre = f"distraccion_{conteo_distraccion}_{nino_id}_{timestamp}.jpg"
                        abs_path = os.path.join(STATIC_CAPTURE_DIR, nombre)
                        rel_path = f"capturas/{nino_id}/{nuevo_id}/{nombre}"

                        cv2.imwrite(abs_path, frame)
                        rutas_frames_distraccion.append(rel_path)
                        COUNTERDISTRACC = 0
            else:
                if distraccion_en_progreso and inicio_distraccion:
                    duracion = round(now - inicio_distraccion, 2)
                    tiempos_distraccion.append(duracion)
                    inicio_distraccion = None
                distraccion_en_progreso = False
                COUNTERDISTRACC = 0

            # ---------- SOMNOLENCIA ----------
            if ear < EYE_AR_THRESH:
                if not somnolencia_en_progreso:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        conteo_somnolencia += 1
                        somnolencia_en_progreso = True
                        inicio_somnolencia = now

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre = f"somnolencia_{conteo_somnolencia}_{nino_id}_{timestamp}.jpg"
                        abs_path = os.path.join(STATIC_CAPTURE_DIR, nombre)
                        rel_path = f"capturas/{nino_id}/{nuevo_id}/{nombre}"

                        cv2.imwrite(abs_path, frame)
                        rutas_frames_somnolencia.append(rel_path)
                        COUNTER = 0
            else:
                if somnolencia_en_progreso and inicio_somnolencia:
                    duracion = round(now - inicio_somnolencia, 2)
                    tiempos_somnolencia.append(duracion)
                    inicio_somnolencia = None
                somnolencia_en_progreso = False
                COUNTER = 0

    cap.release()

    if inicio_somnolencia:
        tiempos_somnolencia.append(round(time.time() - inicio_somnolencia, 2))
    if inicio_distraccion:
        tiempos_distraccion.append(round(time.time() - inicio_distraccion, 2))

    return {
        "somnolencias": conteo_somnolencia,
        "distracciones": conteo_distraccion,
        "tiempos_somnolencia": tiempos_somnolencia,
        "tiempos_distraccion": tiempos_distraccion,
        "frames_somnolencia": rutas_frames_somnolencia,
        "frames_distraccion": rutas_frames_distraccion,
    }


def gen_frames_background(nino_id,nuevo_id):
    global resultado_final
    stop_event.clear()
    deteccion_finalizada.clear()
    resultado = gen_frames(nino_id,nuevo_id)
    resultado_final.clear()
    resultado_final.update(resultado)
    deteccion_finalizada.set()
