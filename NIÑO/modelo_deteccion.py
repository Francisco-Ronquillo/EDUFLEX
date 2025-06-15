import cv2
import mediapipe as mp
from scipy.spatial import distance as dist
from threading import Event
import time

EYE_AR_THRESH = 0.20
EYE_AR_CONSEC_FRAMES = 48
DISTRACC_CONSEC_FRAMES = 48


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

stop_event = Event()
deteccion_finalizada = Event()
resultado_final = {}

# Cálculo de EAR (Eye Aspect Ratio)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def gen_frames():
    COUNTER = 0
    COUNTERDISTRACC = 0
    conteo_somnolencia = 0
    conteo_distraccion = 0
    tiempos_somnolencia = []
    tiempos_distraccion = []
    inicio_somnolencia = None
    inicio_distraccion = None

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return {
            "somnolencias": 0,
            "distracciones": 0,
            "tiempos_somnolencia": [],
            "tiempos_distraccion": [],
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
            # Si había distracción, finalízala
            if inicio_distraccion:
                duracion = round(now - inicio_distraccion, 2)
                tiempos_distraccion.append(duracion)
                inicio_distraccion = None

            COUNTERDISTRACC = 0
            mesh_points = results.multi_face_landmarks[0].landmark
            left_eye = [(int(p.x * w), int(p.y * h)) for p in [mesh_points[i] for i in LEFT_EYE]]
            right_eye = [(int(p.x * w), int(p.y * h)) for p in [mesh_points[i] for i in RIGHT_EYE]]

            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER == EYE_AR_CONSEC_FRAMES:
                    conteo_somnolencia += 1
                    inicio_somnolencia = now
            else:
                if inicio_somnolencia:
                    duracion = round(now - inicio_somnolencia, 2)
                    tiempos_somnolencia.append(duracion)
                    inicio_somnolencia = None
                COUNTER = 0
        else:
            COUNTERDISTRACC += 1
            if COUNTERDISTRACC == DISTRACC_CONSEC_FRAMES:
                conteo_distraccion += 1
                inicio_distraccion = now
            if inicio_somnolencia:
                duracion = round(now - inicio_somnolencia, 2)
                tiempos_somnolencia.append(duracion)
                inicio_somnolencia = None

    cap.release()

    now = time.time()
    if inicio_somnolencia:
        tiempos_somnolencia.append(round(now - inicio_somnolencia, 2))
    if inicio_distraccion:
        tiempos_distraccion.append(round(now - inicio_distraccion, 2))



    resultado = {
        "somnolencias": conteo_somnolencia or 0,
        "distracciones": conteo_distraccion or 0,
        "tiempos_somnolencia": tiempos_somnolencia or [],
        "tiempos_distraccion": tiempos_distraccion or [],
    }
    return resultado

# Ejecutar detección en segundo plano
def gen_frames_background():
    global resultado_final
    stop_event.clear()
    deteccion_finalizada.clear()
    resultado = gen_frames()
    resultado_final.clear()
    resultado_final.update(resultado)
    deteccion_finalizada.set()
