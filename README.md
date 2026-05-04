\# Intelligent Border Surveillance System (Work in Progress)



An AI-powered real-time border intrusion detection and surveillance system currently under active development using computer vision, object detection, tracking, and behavioral analysis.



\---



\## Project Status



⚠️ This project is currently under development.



Some modules are experimental and additional features, optimizations, and architectural improvements are being continuously added.



\---



\## Current Features



\- Real-time person detection using YOLO

\- Multi-object tracking

\- Restricted zone intrusion detection

\- Polygon-based surveillance zones

\- Threat scoring system

\- Behavioral analysis

\- Alert generation system

\- Video stream processing

\- Event logging



\---



\## Technologies Used



\- Python

\- OpenCV

\- Ultralytics YOLO

\- NumPy

\- Shapely



\---



\## Project Structure



```bash

core/

utils/

config/

memory/

logs/

alerts/

tools/

zone\_config/



main.py

surveillance\_engine.py

```



\---



\## Core Components



\### Person Detection

Real-time human detection using YOLO-based object detection.



\### Tracking System

Tracks detected individuals across video frames.



\### Zone Logic

Handles intrusion detection using polygon-based restricted zones.



\### Threat Engine

Analyzes dwell time, movement behavior, and intrusion severity.



\### Alert Manager

Generates alerts and stores intrusion snapshots.



\---



\## Installation



Clone repository:



```bash

git clone https://github.com/Heet108/Intelligent-Border-Surveillance-System.git

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Run the system:



```bash

python main.py

```



\---



\## Planned Improvements



\- Kalman Filter integration

\- Advanced threat classification

\- Thermal camera support

\- Drone surveillance integration

\- Multi-camera synchronization

\- Edge deployment optimization

\- Weapon detection

\- Cloud dashboard support

\- Real-time analytics



\---



\## Research Direction



This project is being developed as a research-oriented intelligent surveillance framework focused on:



\- Border security

\- Edge AI surveillance

\- Real-time threat detection

\- Smart defense systems

\- Computer vision-based monitoring



\---



\## Author



Heet

