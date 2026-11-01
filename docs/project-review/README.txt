Railway Track Defect Detection — Project Review Files

Use these files in a report or presentation:
- model_architecture_diagram.png: architecture overview, exported from the editable architecture diagram in the PowerPoint.
- validation_training_curve.png: validation metrics and training curve slide.
- confusion_matrix.png, PR_curve.png, F1_curve.png: original YOLO validation plots.
- validation_metrics.csv: precision, recall, mAP50 and mAP50-95 at epoch 86.
- training_curve_data.csv: per-epoch validation mAP values for Excel/Sheets or plotting.
- results.csv: complete training log exported by Ultralytics.
- project_review_findings.md: summarized findings and caveats.
- slide_assets/: PNG exports of the six review slides.

Important: the reported scores are validation results. The supplied deployment package does not include separate held-out test evaluation output, so no test score is claimed. Raspberry Pi timing is a single still-image measurement, not a sustained live-video benchmark.
