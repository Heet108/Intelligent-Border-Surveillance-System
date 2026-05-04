import os
import cv2
import numpy as np
from ultralytics import YOLO

# ================= CONFIG =================
MODEL_PATH = "yolov8m.pt"
CONF_THRESHOLD = 0.1
IMG_SIZE = 832

BASE_DIR = r"C:\Heet\Projects\Border_intrusion_system\dataset\images"
BASE_DEBUG = r"C:\Heet\Projects\Border_intrusion_system\debug"
BASE_LABELS = r"C:\Heet\Projects\Border_intrusion_system\dataset\labels"
SPLITS = ["train", "val", "test"]
# ==========================================

model = YOLO(MODEL_PATH)

print("Starting auto-labeling...\n")

for split in SPLITS:

    IMAGE_DIR = os.path.join(BASE_DIR, split)
    LABEL_DIR = os.path.join(BASE_LABELS, split)  # ✅ includes split
    DEBUG_DIR = os.path.join(BASE_DEBUG, split)    # ✅ includes split

    os.makedirs(LABEL_DIR, exist_ok=True)
    os.makedirs(DEBUG_DIR, exist_ok=True)

    print(f"\n=== Processing {split.upper()} ===")

    for img_name in os.listdir(IMAGE_DIR):

        if not img_name.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        img_path = os.path.join(IMAGE_DIR, img_name)

        img = cv2.imread(img_path)
        if img is None:
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            print(f"[SKIP] Cannot read {img_name}")
            continue

        h, w, _ = img.shape

        r = model(img_path, conf=CONF_THRESHOLD, imgsz=IMG_SIZE)[0]

        name = os.path.splitext(img_name)[0]
        label_file = os.path.join(LABEL_DIR, name + ".txt")

        debug_img = img.copy()
        total_boxes = 0

        with open(label_file, "w") as f:

            if r.boxes is not None and len(r.boxes.xyxy) > 0:

                xyxy = r.boxes.xyxy.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy()

                for i, box in enumerate(xyxy):

                    x1, y1, x2, y2 = box
                    cls_id = int(classes[i])
                    conf = float(confs[i])

                    x_center = ((x1 + x2) / 2) / w
                    y_center = ((y1 + y2) / 2) / h
                    bw = (x2 - x1) / w
                    bh = (y2 - y1) / h

                    f.write(f"{cls_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")
                    total_boxes += 1

                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    label = f"{model.names[cls_id]} {conf:.2f}"
                    cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(debug_img, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            else:
                print(f"  {img_name} -> NO detections")

        cv2.imwrite(os.path.join(DEBUG_DIR, img_name), debug_img)
        print(f"  {img_name} -> {total_boxes} boxes written")

print("\n✅ All splits labeled successfully")


# import os
# import cv2
# import numpy as np
# from ultralytics import YOLO

# model = YOLO("yolov8m.pt")

# # Test on a VID image specifically
# img_path = "dataset/images/train/VID20260413134238_000002.jpg"

# img = cv2.imread(img_path)
# print(f"Image shape: {img.shape}")

# r = model(img_path, conf=0.25, imgsz=832)[0]

# if r.boxes is not None and len(r.boxes.xyxy) > 0:
#     print(f"✅ Detections: {len(r.boxes.xyxy)}")
#     for i, box in enumerate(r.boxes.xyxy):
#         cls_id = int(r.boxes.cls[i].item())
#         conf = float(r.boxes.conf[i].item())
#         print(f"   {model.names[cls_id]} conf={conf:.2f}")
# else:
#     print("❌ No detections — try lowering conf to 0.1")





# import os

# folders = [
#     "dataset/images/train",
#     "dataset/images/val", 
#     "dataset/images/test"
# ]

# for folder in folders:
#     renamed = 0
#     for filename in os.listdir(folder):
#         if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
#             continue
        
#         # Replace spaces, special characters
#         new_name = filename.replace(" ", "_")
#         new_name = new_name.replace("-", "_")
#         new_name = new_name.replace(".", "_", new_name.count(".") - 1)  # keep last dot for extension
        
#         if new_name != filename:
#             os.rename(
#                 os.path.join(folder, filename),
#                 os.path.join(folder, new_name)
#             )
#             renamed += 1
#             print(f"  Renamed: {filename} -> {new_name}")
    
#     print(f"✅ {folder}: {renamed} files renamed")