# Railway track defect detector — review findings

## Model and data
- Model: YOLOv8n object detector, fine-tuned for `defective` and `non-defective`.
- Training: 100 epochs, 640 × 640 model input, batch 16, Ultralytics 8.3.40.
- Dataset split: 1,198 train, 101 validation, 54 held-out test images (1,353 total).
- Deployment: exported NCNN model running on Raspberry Pi 4 Model B (4 GB) with Camera Module 1.3.

## Validation results
Values below are from the row with the highest saved validation mAP50–95 (epoch 86) in `results.csv`:
- Precision: 92.0%
- Recall: 89.4%
- mAP50: 92.7%
- mAP50–95: 62.7%

`mAP50` uses IoU 0.50. `mAP50–95` averages AP over IoU 0.50 through 0.95. These values describe the validation split, not the held-out test split. The deployment ZIP does not contain the separate test-evaluation output, so test performance is not reported here.

## Raspberry Pi timing
One still-image inference log measured 64.0 ms preprocessing, 754.7 ms model inference, and 9.0 ms postprocessing (about 827.7 ms total, or approximately 1.2 frames per second). This is one still-image measurement, not a sustained live-video benchmark.

## Source files
- `results.csv`: epoch-by-epoch training and validation metrics.
- `confusion_matrix.png`, `PR_curve.png`, `F1_curve.png`: validation diagnostics from the provided deployment package.
