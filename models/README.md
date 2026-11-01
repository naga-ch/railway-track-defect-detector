# Model package

`railway_pi_deployment.zip` is the training export currently used by the Pi prototype. It contains `best.pt`, the NCNN model directory, class names, validation plots, and the Ultralytics training log.

Unpack it into `~/railway_detector` on the Pi. For retraining, use the Google Colab notebook in `training/` and download the new deployment archive from Colab. Do not commit new weights or checkpoints as loose files; use a versioned GitHub Release asset or Git LFS for future model versions.

The model was trained using the Roboflow dataset described in the main README. Preserve dataset attribution and report the split used for every performance metric.
