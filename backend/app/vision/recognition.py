from __future__ import annotations

import base64
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np

from backend.app.scenes.figure1 import build_figure1_scene, simulate_figure1_scene


def _to_png_data_url(image: np.ndarray) -> str:
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Failed to encode preview image")
    return "data:image/png;base64," + base64.b64encode(encoded.tobytes()).decode("ascii")


def _threshold_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    binary = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        np.ones((3, 3), dtype=np.uint8),
        iterations=1,
    )
    return binary


def _detect_circles(gray: np.ndarray) -> List[Tuple[int, int, int]]:
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=90,
        param1=120,
        param2=22,
        minRadius=18,
        maxRadius=120,
    )
    if circles is None:
        return []
    rounded = np.round(circles[0]).astype(int)
    return [(int(x), int(y), int(r)) for x, y, r in rounded]


def _detect_rectangles(binary: np.ndarray) -> List[Tuple[int, int, int, int]]:
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rectangles: List[Tuple[int, int, int, int]] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < 8000:
            continue
        aspect = w / max(h, 1)
        if 1.4 <= aspect <= 6.0 and 20 <= h <= 160:
            rectangles.append((x, y, w, h))
    rectangles.sort(key=lambda item: (item[1], item[0]))
    return rectangles


def _detect_vertical_lines(binary: np.ndarray) -> List[Tuple[int, int, int, int]]:
    lines = cv2.HoughLinesP(
        binary,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=40,
        maxLineGap=10,
    )
    if lines is None:
        return []
    result: List[Tuple[int, int, int, int]] = []
    for line in lines[:, 0]:
        x1, y1, x2, y2 = map(int, line)
        if abs(x1 - x2) <= 8 and abs(y1 - y2) >= 50:
            result.append((x1, y1, x2, y2))
    return result


def _choose_battery_lines(lines: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
    candidates = []
    for left in lines:
        for right in lines:
            if right[0] <= left[0]:
                continue
            distance = right[0] - left[0]
            left_length = abs(left[1] - left[3])
            right_length = abs(right[1] - right[3])
            if 20 <= distance <= 80 and abs(left_length - right_length) >= 20:
                candidates.append((left, right))
    if not candidates:
        raise ValueError("Could not detect battery plates")
    left, right = sorted(candidates, key=lambda pair: pair[0][0])[0]
    return left[0], min(left[1], left[3]), right[0], max(right[1], right[3])


def _detect_diagonal_switch(binary: np.ndarray, around: Tuple[int, int]) -> Tuple[int, int]:
    x_center, y_center = around
    roi = binary[max(y_center - 80, 0): y_center + 200, max(x_center - 140, 0): x_center + 20]
    lines = cv2.HoughLinesP(
        roi,
        rho=1,
        theta=np.pi / 180,
        threshold=20,
        minLineLength=50,
        maxLineGap=10,
    )
    if lines is None:
        return x_center - 60, y_center + 110
    best = None
    for line in lines[:, 0]:
        x1, y1, x2, y2 = map(int, line)
        if abs(x1 - x2) < 20:
            continue
        slope = (y2 - y1) / (x2 - x1)
        if -5.0 <= slope <= -0.3:
            best = (min(x1, x2), max(y1, y2))
            break
    if best is None:
        return x_center - 60, y_center + 110
    return best[0] + max(x_center - 140, 0), best[1] + max(y_center - 80, 0)


def recognize_clean_circuit(file_bytes: bytes) -> Dict[str, Any]:
    array = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unsupported image data")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = _threshold_image(image)
    circles = _detect_circles(gray)
    rectangles = _detect_rectangles(binary)
    verticals = _detect_vertical_lines(binary)

    base = build_figure1_scene()
    scene = base["scene"]
    state = {**base["state"], "switch_closed": True}
    components = {component["id"]: component for component in scene["components"]}
    large_circles = sorted([circle for circle in circles if circle[2] >= 50], key=lambda item: item[1])
    can_full_reconstruct = len(large_circles) >= 2 and len(rectangles) >= 2 and len(verticals) >= 2

    if can_full_reconstruct:
        voltmeter_circle = min(large_circles, key=lambda item: item[1])
        ammeter_circle = max(large_circles, key=lambda item: item[0])
        small_circles = [circle for circle in circles if circle[2] < 40]
        switch_circle = (
            min(small_circles, key=lambda item: item[0]) if small_circles else (92, 360, 22)
        )

        top_rect, bottom_rect = sorted(rectangles[:2], key=lambda item: item[1])
        battery_left_x, battery_top_y, battery_right_x, battery_bottom_y = _choose_battery_lines(verticals)
        switch_open_x, switch_open_y = _detect_diagonal_switch(binary, (switch_circle[0], switch_circle[1]))

        components["switch"]["x"] = float(switch_circle[0] - 54)
        components["switch"]["y"] = float(switch_circle[1] - 108)
        for port in components["switch"]["ports"]:
            if port["id"] == "top":
                port["x"], port["y"] = float(switch_circle[0]), float(top_rect[1] + top_rect[3] // 2)
            elif port["id"] == "bottom":
                port["x"], port["y"] = float(switch_circle[0]), float(battery_top_y + (battery_bottom_y - battery_top_y) / 2)
            elif port["id"] == "pivot":
                port["x"], port["y"] = float(switch_circle[0]), float(switch_circle[1])
            elif port["id"] == "open_contact":
                port["x"], port["y"] = float(switch_open_x), float(switch_open_y)
            elif port["id"] == "closed_contact":
                port["x"], port["y"] = float(switch_circle[0]), float(switch_circle[1] + 110)

        components["battery"]["x"] = float(battery_left_x - 30)
        components["battery"]["y"] = float(battery_top_y)
        components["battery"]["width"] = float((battery_right_x - battery_left_x) + 120)
        components["battery"]["height"] = float(battery_bottom_y - battery_top_y)
        for port in components["battery"]["ports"]:
            if port["id"] == "left":
                port["x"], port["y"] = float(switch_circle[0]), float(battery_top_y + (battery_bottom_y - battery_top_y) / 2)
            elif port["id"] == "right":
                port["x"], port["y"] = float(bottom_rect[0]), float(bottom_rect[1] + bottom_rect[3] / 2)

        components["resistor"]["x"], components["resistor"]["y"], components["resistor"]["width"], components["resistor"]["height"] = map(float, top_rect)
        for port in components["resistor"]["ports"]:
            if port["id"] == "left":
                port["x"], port["y"] = float(top_rect[0]), float(top_rect[1] + top_rect[3] / 2)
            elif port["id"] == "right":
                port["x"], port["y"] = float(top_rect[0] + top_rect[2]), float(top_rect[1] + top_rect[3] / 2)

        components["rheostat"]["x"], components["rheostat"]["y"], components["rheostat"]["width"], components["rheostat"]["height"] = map(float, bottom_rect)
        slider_center_x = bottom_rect[0] + bottom_rect[2] * state["rheostat_ratio"]
        for port in components["rheostat"]["ports"]:
            if port["id"] == "left":
                port["x"], port["y"] = float(bottom_rect[0]), float(bottom_rect[1] + bottom_rect[3] / 2)
            elif port["id"] == "right":
                port["x"], port["y"] = float(bottom_rect[0] + bottom_rect[2]), float(bottom_rect[1] + bottom_rect[3] / 2)
            elif port["id"] == "slider_contact":
                port["x"], port["y"] = float(slider_center_x), float(bottom_rect[1])

        for meter_id, circle in (("voltmeter", voltmeter_circle), ("ammeter", ammeter_circle)):
            component = components[meter_id]
            component["x"] = float(circle[0] - circle[2])
            component["y"] = float(circle[1] - circle[2])
            component["width"] = float(circle[2] * 2)
            component["height"] = float(circle[2] * 2)
            for port in component["ports"]:
                if meter_id == "voltmeter":
                    if port["id"] == "left":
                        port["x"], port["y"] = float(circle[0] - circle[2]), float(circle[1])
                    elif port["id"] == "right":
                        port["x"], port["y"] = float(circle[0] + circle[2]), float(circle[1])
                else:
                    if port["id"] == "top":
                        port["x"], port["y"] = float(circle[0]), float(circle[1] - circle[2])
                    elif port["id"] == "bottom":
                        port["x"], port["y"] = float(circle[0]), float(circle[1] + circle[2])

        components["junction_left"]["x"] = float(top_rect[0] - 35)
        components["junction_left"]["y"] = float(top_rect[1] + top_rect[3] / 2)
        components["junction_right"]["x"] = float(top_rect[0] + top_rect[2] + 35)
        components["junction_right"]["y"] = float(top_rect[1] + top_rect[3] / 2)
        components["junction_bottom"]["x"] = float(bottom_rect[0] + bottom_rect[2])
        components["junction_bottom"]["y"] = float(bottom_rect[1] + bottom_rect[3] / 2)
        components["ammeter_top_node"]["x"] = float(ammeter_circle[0])
        components["ammeter_top_node"]["y"] = float(top_rect[1] + top_rect[3] / 2)
        components["ammeter_bottom_node"]["x"] = float(ammeter_circle[0])
        components["ammeter_bottom_node"]["y"] = float(bottom_rect[1] + bottom_rect[3] / 2)
        confidence = round(
            min(
                0.99,
                0.55 + 0.06 * len(large_circles) + 0.05 * len(rectangles) + 0.02 * len(verticals),
            ),
            2,
        )
    else:
        confidence = 0.45
    detections = {
        "circles": [
            {"center_x": int(x), "center_y": int(y), "radius": int(r)} for x, y, r in circles
        ],
        "rectangles": [
            {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
            for x, y, w, h in rectangles
        ],
        "vertical_lines": [
            {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)}
            for x1, y1, x2, y2 in verticals
        ],
        "confidence": confidence,
    }
    simulation = simulate_figure1_scene(scene, state)
    return {
        "reference_image": {"id": "uploaded-clean-circuit", "data_url": _to_png_data_url(image)},
        "scene": {**scene, "id": "recognized-clean-circuit"},
        "state": state,
        "simulation": simulation,
        "detections": detections,
        "needs_confirmation": confidence < 0.9,
    }
