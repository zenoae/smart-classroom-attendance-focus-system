from __future__ import annotations

import pickle
from typing import List, Optional, Tuple

import cv2
import numpy as np

from app.extensions import db
from app.models import FaceEmbedding, Student


def _detect_faces(frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    return list(faces)


def _compute_embedding(face_img: np.ndarray) -> np.ndarray:
    resized = cv2.resize(face_img, (64, 64))
    normalized = resized.astype("float32") / 255.0
    return normalized.flatten()


def enroll_student_face(student: Student, frame: np.ndarray) -> None:
    faces = _detect_faces(frame)
    if not faces:
        return
    x, y, w, h = faces[0]
    face_img = frame[y : y + h, x : x + w]
    embedding = _compute_embedding(face_img)
    data = pickle.dumps(embedding)
    record = FaceEmbedding(student_id=student.id, embedding=data)
    db.session.add(record)
    db.session.commit()


def _load_all_embeddings() -> List[Tuple[Student, np.ndarray]]:
    results: List[Tuple[Student, np.ndarray]] = []
    embeddings = FaceEmbedding.query.all()
    for item in embeddings:
        embedding = pickle.loads(item.embedding)
        results.append((item.student, embedding))
    return results


def recognize_student(frame: np.ndarray, threshold: float = 0.6) -> Optional[Student]:
    faces = _detect_faces(frame)
    if not faces:
        return None
    x, y, w, h = faces[0]
    face_img = frame[y : y + h, x : x + w]
    query_embedding = _compute_embedding(face_img)

    candidates = _load_all_embeddings()
    if not candidates:
        return None

    best_student: Optional[Student] = None
    best_distance = float("inf")

    for student, embedding in candidates:
        dist = float(np.linalg.norm(query_embedding - embedding))
        if dist < best_distance:
            best_distance = dist
            best_student = student

    if best_student is None:
        return None

    max_distance = np.sqrt(len(query_embedding))
    score = best_distance / max_distance
    if score > threshold:
        return None

    return best_student

