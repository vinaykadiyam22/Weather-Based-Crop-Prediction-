# Plant Disease Classification Model

Pre-trained MobileNetV2 for plant disease detection (38 classes).

**Source:** [Daksh159/plant-disease-mobilenetv2](https://huggingface.co/Daksh159/plant-disease-mobilenetv2)  
**License:** Apache 2.0

## Files

- `mobilenetv2_plant.pth` – PyTorch model weights
- `class_names.json` – 38 PlantVillage class names (Crop___Disease format)

## Usage

Loaded by `backend/services/disease_detection.py` for the disease detection API.
