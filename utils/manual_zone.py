import cv2
import numpy as np
import json
import os

# Global list to store clicked points
selected_points = []

# File path to save restricted zone
ZONE_FILE = "zone_config/restricted_zone.json"


def mouse_callback(event, x, y, flags, param):
    """
    Mouse callback to capture 4 polygon points.
    """
    global selected_points

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(selected_points) < 4:
            selected_points.append((x, y))
            print(f"[INFO] Point {len(selected_points)} selected: ({x}, {y})")


def save_zone(points):
    """
    Save selected polygon points to JSON file.
    """
    try:
        os.makedirs("zone_config", exist_ok=True)

        # Convert tuples to lists before saving
        points_to_save = [list(point) for point in points]

        with open(ZONE_FILE, "w") as f:
            json.dump(points_to_save, f, indent=4)

        print(f"[INFO] Restricted zone saved to: {ZONE_FILE}")

    except Exception as e:
        print(f"[ERROR] Failed to save restricted zone: {e}")


def load_zone():
    """
    Load restricted zone from JSON file safely.
    Returns:
        list of tuples if valid
        None if file missing / empty / corrupted / invalid
    """
    if not os.path.exists(ZONE_FILE):
        print("[INFO] No saved restricted zone file found.")
        return None

    try:
        with open(ZONE_FILE, "r") as f:
            content = f.read().strip()

            # Handle empty file
            if not content:
                print("[WARNING] Restricted zone file is empty.")
                return None

            points = json.loads(content)

        # Validate structure
        if not isinstance(points, list) or len(points) != 4:
            print("[WARNING] Restricted zone file format is invalid.")
            return None

        for point in points:
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                print("[WARNING] Invalid point format in restricted zone file.")
                return None

        # Convert list of lists -> list of tuples
        points = [tuple(map(int, point)) for point in points]

        print("[INFO] Restricted zone loaded successfully.")
        return points

    except json.JSONDecodeError:
        print("[WARNING] Restricted zone JSON is corrupted.")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load restricted zone: {e}")
        return None


def get_manual_zone(frame):
    """
    Manually select 4 points on frame for restricted zone.
    Controls:
        - Left click: select point
        - R: reset points
        - ENTER: save if exactly 4 points selected
        - ESC: cancel
    """
    global selected_points
    selected_points = []

    clone = frame.copy()
    window_name = "Select Restricted Zone - Click 4 Points"

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        temp = clone.copy()

        # Draw selected points
        for i, point in enumerate(selected_points):
            cv2.circle(temp, point, 6, (0, 0, 255), -1)
            cv2.putText(
                temp,
                f"P{i+1}",
                (point[0] + 10, point[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

        # Draw temporary connecting lines
        if len(selected_points) > 1:
            pts = np.array(selected_points, np.int32)
            cv2.polylines(temp, [pts], False, (255, 0, 0), 1)

        instructions = [
            "Click 4 points for RESTRICTED ZONE",
            "Order: Top-Left -> Top-Right -> Bottom-Right -> Bottom-Left",
            "Press R to reset | ENTER to save | ESC to cancel"
        ]

        for idx, text in enumerate(instructions):
            cv2.putText(
                temp,
                text,
                (20, 30 + idx * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # Draw closed polygon if 4 points selected
        if len(selected_points) == 4:
            pts = np.array(selected_points, np.int32)
            cv2.polylines(temp, [pts], True, (0, 0, 255), 2)

        cv2.imshow(window_name, temp)
        key = cv2.waitKey(1) & 0xFF

        # Reset selected points
        if key == ord('r'):
            selected_points = []
            print("[INFO] Points reset.")

        # Save selected zone
        elif key == 13:  # ENTER
            if len(selected_points) == 4:
                save_zone(selected_points)
                cv2.destroyWindow(window_name)
                return selected_points
            else:
                print("[WARNING] Please select exactly 4 points before saving.")

        # Cancel selection
        elif key == 27:  # ESC
            print("[INFO] Zone selection cancelled.")
            cv2.destroyWindow(window_name)
            return None


def get_or_create_zone(frame, force_reselect=False):
    """
    Load existing restricted zone if available.
    Otherwise, ask user to manually create one.

    Args:
        frame: First video frame
        force_reselect: If True, ignore saved zone and reselect manually

    Returns:
        list of 4 points or None
    """
    if not force_reselect:
        saved_zone = load_zone()
        if saved_zone is not None and len(saved_zone) == 4:
            print("[INFO] Loaded saved restricted zone.")
            return saved_zone

    print("[INFO] No valid saved zone found. Please select manually.")
    return get_manual_zone(frame)