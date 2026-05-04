from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data = r"C:\Heet\Projects\Border_intrusion_system\dataset.yaml",
    epochs=50,
    imgsz=320,
    batch=8,
    lr0=0.01,
    augment=True,
    patience=0,
    workers=0,
    close_mosaic=10,
    verbose=True
)
