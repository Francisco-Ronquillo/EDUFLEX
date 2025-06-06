import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist

# Umbrales
EYE_AR_THRESH = 0.20
EYE_AR_CONSEC_FRAMES = 48
DISTRACC_CONSEC_FRAMES = 48

COUNTER = 0
COUNTERDISTRACC = 0

# Variables globales para el estado de alerta
alarmaSomnolencia = False
alarmaDistraccion = False

# Inicializar MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Esta función es la que usarás en StreamingHttpResponse
def gen_frames():
    global COUNTER, COUNTERDISTRACC, alarmaSomnolencia, alarmaDistraccion

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            COUNTERDISTRACC = 0
            alarmaDistraccion = False
            cv2.putText(frame, "Rostro detectado", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "No hay distracción", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            mesh_points = results.multi_face_landmarks[0].landmark
            left_eye = [(int(mesh_points[p].x * w), int(mesh_points[p].y * h)) for p in LEFT_EYE]
            right_eye = [(int(mesh_points[p].x * w), int(mesh_points[p].y * h)) for p in RIGHT_EYE]

            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                if COUNTER < EYE_AR_CONSEC_FRAMES // 2:
                    cv2.putText(frame, "Somnolencia mínima", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    alarmaSomnolencia = False
                elif COUNTER < EYE_AR_CONSEC_FRAMES:
                    cv2.putText(frame, "Peligro de somnolencia", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 191, 255), 2)
                    alarmaSomnolencia = False
                else:
                    cv2.putText(frame, "Somnolencia detectada", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    alarmaSomnolencia = True
            else:
                COUNTER = 0
                alarmaSomnolencia = False
                cv2.putText(frame, "No hay somnolencia", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        else:
            COUNTERDISTRACC += 1
            cv2.putText(frame, "Rostro no detectado", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            if COUNTERDISTRACC < DISTRACC_CONSEC_FRAMES // 2:
                cv2.putText(frame, "Distracción mínima", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                alarmaDistraccion = False
            elif COUNTERDISTRACC < DISTRACC_CONSEC_FRAMES:
                cv2.putText(frame, "Peligro de distracción", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 191, 255), 2)
                alarmaDistraccion = False
            else:
                cv2.putText(frame, "Distracción detectada", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                alarmaDistraccion = True

        # Codificar y enviar el frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
