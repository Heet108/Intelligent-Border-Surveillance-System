from ultralytics import YOLO

# Load your trained model (IMPORTANT)
model = YOLO(r"C:\Heet\Projects\Border_intrusion_system\runs\detect\train2\weights\best.pt")

# Export to TFLite (best for Raspberry Pi)  Using tflite16
model.export(format="tflite", imgsz=640, half=True)  # int8=True  

print("YOLOv8 exported to TFLite successfully!")







