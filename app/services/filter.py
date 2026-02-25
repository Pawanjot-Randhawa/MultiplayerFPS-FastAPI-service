import cv2
import numpy as np


def decode_image_bytes(image_bytes: bytes):
    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Invalid image bytes: unable to decode image")
    return frame


def filter_image(frame):
    height, width = frame.shape[:2]
    image_area = height * width

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, 60, 150)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    white_mask = cv2.inRange(
        hsv,
        np.array([0, 0, 150], dtype=np.uint8),
        np.array([179, 70, 255], dtype=np.uint8),
    )

    min_area = max(180, int(image_area * 0.00012))
    hits = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(c)
        if w < 8 or h < 16:
            continue

        aspect = h / (w + 1e-5)
        if aspect < 1.2 or aspect > 4.8:
            continue

        rect_area = (w * h) + 1e-5
        fill = area / rect_area
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull) + 1e-5
        solidity = area / hull_area

        perimeter = cv2.arcLength(c, True) + 1e-5
        circularity = (4.0 * np.pi * area) / (perimeter * perimeter)

        white_ratio = 0.0
        roi = white_mask[y : y + h, x : x + w]
        if roi.size > 0:
            white_ratio = float(cv2.countNonZero(roi)) / float(roi.size)

        score = 0
        if 0.28 < fill < 0.90:
            score += 1
        if solidity > 0.80:
            score += 1
        if 0.22 < circularity < 0.90:
            score += 1
        if white_ratio > 0.20:
            score += 1

        if score >= 3:
            hits.append((x, y, w, h))


    return hits


def filter_image_bytes(image_bytes: bytes) -> str:
    frame = decode_image_bytes(image_bytes)
    hits = filter_image(frame)
    return "suspected" if len(hits) > 0 else "fair"