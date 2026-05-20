# import cv2
# import os
# import random
# import shutil
# import numpy as np

# # ================= CONFIG =================
# CAMERA_VIDEO_DIR = "data/test_videos_main"
# PHONE_VIDEO_DIR  = "data/test_videos"

# TEMP_DIR   = "temp_frames"
# OUTPUT_DIR = "dataset"

# IMG_SIZE = 416
# TARGET_FPS = 3   # IMPORTANT: reduce duplicates

# TRAIN_SPLIT = 0.7
# VAL_SPLIT   = 0.2
# TEST_SPLIT  = 0.1
# PHONE_RATIO = 0.3

# threshold = 1
# # ==========================================


# # ---------- FRAME EXTRACTION ----------
# def extract_frames(video_path, output_dir, target_fps):
#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         print(f"[ERROR] Cannot open: {video_path}")
#         return

#     video_fps = cap.get(cv2.CAP_PROP_FPS)

#     if video_fps <= 0 or video_fps > 120:
#         video_fps = 30

#     interval = max(int(video_fps / target_fps), 1)

#     print(f"[INFO] {video_path} | FPS={video_fps:.2f} | interval={interval}")

#     count, saved = 0, 0
#     base = os.path.splitext(os.path.basename(video_path))[0]

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         if count % interval == 0:
#             filename = f"{base}_{saved:06d}.jpg"
#             cv2.imwrite(os.path.join(output_dir, filename), frame)
#             saved += 1

#         count += 1

#     cap.release()


# def extract_all():
#     cam_out   = f"{TEMP_DIR}/camera"
#     phone_out = f"{TEMP_DIR}/phone"

#     os.makedirs(cam_out, exist_ok=True)
#     os.makedirs(phone_out, exist_ok=True)

#     for vid in os.listdir(CAMERA_VIDEO_DIR):
#         extract_frames(os.path.join(CAMERA_VIDEO_DIR, vid), cam_out, TARGET_FPS)

#     for vid in os.listdir(PHONE_VIDEO_DIR):
#         extract_frames(os.path.join(PHONE_VIDEO_DIR, vid), phone_out, TARGET_FPS)


# # ---------- PREPROCESS ----------
# def preprocess_camera(img):
#     return cv2.resize(img, (IMG_SIZE, IMG_SIZE))


# def preprocess_phone(img):
#     return cv2.resize(img, (IMG_SIZE, IMG_SIZE))


# def preprocess_all():
#     cam_in   = f"{TEMP_DIR}/camera"
#     phone_in = f"{TEMP_DIR}/phone"

#     cam_out   = f"{TEMP_DIR}/processed_camera"
#     phone_out = f"{TEMP_DIR}/processed_phone"

#     os.makedirs(cam_out, exist_ok=True)
#     os.makedirs(phone_out, exist_ok=True)

#     for f in os.listdir(cam_in):
#         img = cv2.imread(os.path.join(cam_in, f))
#         if img is None: continue
#         img = preprocess_camera(img)
#         cv2.imwrite(os.path.join(cam_out, f), img)

#     for f in os.listdir(phone_in):
#         img = cv2.imread(os.path.join(phone_in, f))
#         if img is None: continue
#         img = preprocess_phone(img)
#         cv2.imwrite(os.path.join(phone_out, f), img)


# # ---------- REMOVE DUPLICATES ----------
# def remove_similar_images(folder, threshold=5):
#     files = sorted(os.listdir(folder))
#     prev_img = None
#     kept = 0

#     for f in files:
#         path = os.path.join(folder, f)
#         img = cv2.imread(path)

#         if img is None:
#             continue

#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#         if prev_img is None:
#             prev_img = gray
#             kept += 1
#             continue

#         diff = np.mean(cv2.absdiff(prev_img, gray))

#         if diff < threshold:
#             os.remove(path)
#         else:
#             prev_img = gray
#             kept += 1

#     print(f"[INFO] {folder} → kept {kept} images")


# # ---------- MERGE + SPLIT ----------
# def create_dataset():
#     cam_dir   = f"{TEMP_DIR}/processed_camera"
#     phone_dir = f"{TEMP_DIR}/processed_phone"

#     cam_images   = [os.path.join(cam_dir, f) for f in os.listdir(cam_dir)]
#     phone_images = [os.path.join(phone_dir, f) for f in os.listdir(phone_dir)]

#     max_phone = int(len(cam_images) * PHONE_RATIO)
#     phone_images = random.sample(phone_images, min(len(phone_images), max_phone))

#     all_images = cam_images + phone_images
#     random.shuffle(all_images)

#     total = len(all_images)
#     train_end = int(total * TRAIN_SPLIT)
#     val_end   = int(total * (TRAIN_SPLIT + VAL_SPLIT))

#     splits = {
#         "train": all_images[:train_end],
#         "val":   all_images[train_end:val_end],
#         "test":  all_images[val_end:]
#     }

#     for split in splits:
#         os.makedirs(f"{OUTPUT_DIR}/images/{split}", exist_ok=True)
#         os.makedirs(f"{OUTPUT_DIR}/labels/{split}", exist_ok=True)

#         for img_path in splits[split]:
#             filename = os.path.basename(img_path)
#             shutil.copy(img_path, f"{OUTPUT_DIR}/images/{split}/{filename}")


# # ---------- YAML ----------
# def create_yaml():
#     yaml = f"""path: {OUTPUT_DIR}
# train: images/train
# val: images/val
# test: images/test

# names:
#   0: person
# """
#     with open(f"{OUTPUT_DIR}/data.yaml", "w") as f:
#         f.write(yaml)


# # ---------- MAIN ----------
# def main():
#     print("=== STEP 1: Extract Frames ===")
#     extract_all()

#     print("=== STEP 2: Preprocess ===")
#     preprocess_all()

#     print("=== STEP 3: Remove Duplicates ===")
#     remove_similar_images(f"{TEMP_DIR}/processed_camera")
#     remove_similar_images(f"{TEMP_DIR}/processed_phone")

#     print("=== STEP 4: Create Dataset ===")
#     create_dataset()

#     print("=== STEP 5: YAML ===")
#     create_yaml()

#     print("DONE — Ready for labeling & training")


# if __name__ == "__main__":
#     main()





# import os
# import glob
# import shutil

# BASE_IMG_DIR = r"dataset/images"
# BASE_LBL_DIR = r"dataset/labels"

# OUT_DIR = r"dataset_clean"

# splits = ["train", "val", "test"]

# for split in splits:
#     img_dir = os.path.join(BASE_IMG_DIR, split)
#     lbl_dir = os.path.join(BASE_LBL_DIR, split)

#     out_img_dir = os.path.join(OUT_DIR, "images", split)
#     out_lbl_dir = os.path.join(OUT_DIR, "labels", split)

#     os.makedirs(out_img_dir, exist_ok=True)
#     os.makedirs(out_lbl_dir, exist_ok=True)

#     image_files = glob.glob(os.path.join(img_dir, "*.jpg")) + \
#                   glob.glob(os.path.join(img_dir, "*.png"))

#     for img_path in image_files:
#         base = os.path.splitext(os.path.basename(img_path))[0]
#         label_path = os.path.join(lbl_dir, base + ".txt")

#         # copy image
#         shutil.copy(img_path, out_img_dir)

#         if not os.path.exists(label_path):
#             continue

#         with open(label_path, "r") as f:
#             lines = f.readlines()

#         new_lines = []

#         for line in lines:
#             parts = line.strip().split()

#             if len(parts) != 5:
#                 continue

#             x, y, w, h = parts[1], parts[2], parts[3], parts[4]

#             # binary conversion
#             new_lines.append(f"0 {x} {y} {w} {h}\n")

#         if len(new_lines) > 0:
#             out_label_path = os.path.join(out_lbl_dir, base + ".txt")
#             with open(out_label_path, "w") as f:
#                 f.writelines(new_lines)

# print("FULL DATASET CLEANING DONE")








import os
import glob
import shutil

# paths
IMG_DIR = r"dataset/images"
LBL_DIR = r"dataset/labels"

OUT_DIR = r"dataset_person"

splits = ["train", "val", "test"]

# IMPORTANT: set your PERSON class id here from original dataset
PERSON_CLASS_IDS = [0]  # change if person was different earlier

for split in splits:
    img_path = os.path.join(IMG_DIR, split)
    lbl_path = os.path.join(LBL_DIR, split)

    out_img = os.path.join(OUT_DIR, "images", split)
    out_lbl = os.path.join(OUT_DIR, "labels", split)

    os.makedirs(out_img, exist_ok=True)
    os.makedirs(out_lbl, exist_ok=True)

    images = glob.glob(os.path.join(img_path, "*.jpg")) + glob.glob(os.path.join(img_path, "*.png"))

    for img in images:
        base = os.path.splitext(os.path.basename(img))[0]
        label_file = os.path.join(lbl_path, base + ".txt")

        shutil.copy(img, out_img)

        if not os.path.exists(label_file):
            continue

        with open(label_file, "r") as f:
            lines = f.readlines()

        new_labels = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            cls = int(parts[0])

            # KEEP ONLY PERSON
            if cls in PERSON_CLASS_IDS:
                x, y, w, h = parts[1], parts[2], parts[3], parts[4]
                new_labels.append(f"0 {x} {y} {w} {h}\n")

        if len(new_labels) > 0:
            with open(os.path.join(out_lbl, base + ".txt"), "w") as f:
                f.writelines(new_labels)