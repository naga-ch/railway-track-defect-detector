# YOLOv8 railway defect detector: Colab → Raspberry Pi 4

## Colab training

1. Open `train_yolov8_railway_defects_colab.ipynb` in Google Colab.
2. Select **Runtime → Change runtime type → T4 GPU** (or another GPU runtime).
3. Run the notebook from top to bottom. In the dataset cell, use either the upload option or the Google Drive option, not both. The ZIP in this project is `RSDD Split 4.v2-split-4-with-augment.yolov8.zip`.
4. The notebook trains YOLOv8n, evaluates on the existing held-out test split, exports NCNN, and downloads `railway_pi_deployment.zip`.
5. Keep the downloaded archive. It contains the trained `best.pt`, NCNN model directory, and available evaluation outputs.

The checked dataset contains 1,198 train, 101 validation, and 54 test images. The two classes are `defective` and `non-defective`. The notebook constructs a correct Colab-side YAML rather than relying on paths from the original export.

## First Pi prototype

1. Install 64-bit Raspberry Pi OS on the Pi 4 and connect the Camera Module 1.3.
2. Verify camera capture with `rpicam-hello`.
3. Install Picamera2 from Raspberry Pi OS packages (`sudo apt install -y python3-picamera2`).
4. Transfer and unzip `railway_pi_deployment.zip` onto the Pi.
5. Install the Ultralytics runtime and NCNN dependencies according to the current [Ultralytics Raspberry Pi guide](https://docs.ultralytics.com/guides/raspberry-pi/).
6. Load the exported NCNN model folder for inference. Start with saved images, then camera frames at a modest resolution and sparse rate; measure speed on the Pi before continuous video.

The camera-only prototype should save detections and annotated snapshots locally. Do not enable robot motion based on detections until stationary tests show acceptable miss/false-alarm behavior under the actual lighting and camera mounting conditions.

## Live camera detector

Copy `live_camera_detector.py` from this project to `~/railway_detector/` on the Pi. From the Pi terminal:

```bash
cd ~/railway_detector
source ~/railway-venv/bin/activate
python live_camera_detector.py
```

The annotated preview appears on the touchscreen. Press `q` while the preview window is focused to stop. Frames containing a `defective` class detection are saved under `captures/`. The default confidence threshold is 0.35; lower it with `--conf 0.20` if known defects are being missed, or raise it to reduce false alarms. The Pi 4 may process only about one frame per second, so start with a stationary camera and controlled lighting.

If the desktop preview is unavailable, use `python live_camera_detector.py --headless`; it continues to save detected-defect snapshots and can be stopped with Ctrl+C in Terminal.

## Dashboard and desktop launcher

From Mac Terminal, transfer the dashboard files into the Pi model folder:

```bash
scp pi/railway_dashboard.py pi/start_railway_dashboard.sh pi/install_railway_desktop_icon.sh PI_USER@PI_IP:~/railway_detector/
```

Replace `PI_IP` with the Pi's current address from `hostname -I`. In the Pi desktop Terminal, install Flask, then install the shortcut:

```bash
source ~/railway-venv/bin/activate
pip install --no-cache-dir flask
chmod +x ~/railway_detector/start_railway_dashboard.sh ~/railway_detector/install_railway_desktop_icon.sh
bash ~/railway_detector/install_railway_desktop_icon.sh
```

Double-click **Railway Track Inspector** on the Pi desktop. If prompted, choose **Allow Launching**. The dashboard starts with its detector stopped; tap **Start** for the annotated camera feed. The page shows inference time, latest-frame defect count, adjustable confidence, and recent defect snapshots. **Stop** ends inference and releases the camera while leaving the dashboard open; **Exit** closes the kiosk browser and returns to the Pi desktop. The dashboard binds to localhost only, so the camera feed is not exposed to other network devices.

The dashboard's **Project Review** tab reads `results.csv` and the saved plot images beside `best_ncnn_model`. It presents the validation metrics at the highest saved validation mAP50–95 row, the YOLOv8n pipeline, dataset split counts, and the confusion matrix, PR, F1, and mAP plots. The current ZIP does not record a separate test-set metric result; the page explicitly calls this out so validation values are not presented as test results.
