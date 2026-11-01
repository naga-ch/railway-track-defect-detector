#!/usr/bin/env python3
"""Run the railway defect NCNN model on Raspberry Pi camera frames."""

from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2
from picamera2 import Picamera2
from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        default=str(Path.home() / "railway_detector" / "best_ncnn_model"),
        help="Path to the exported Ultralytics NCNN model directory.",
    )
    parser.add_argument("--width", type=int, default=640, help="Camera capture width.")
    parser.add_argument("--height", type=int, default=480, help="Camera capture height.")
    parser.add_argument("--imgsz", type=int, default=640, help="Model inference size.")
    parser.add_argument("--conf", type=float, default=0.35, help="Detection confidence threshold.")
    parser.add_argument(
        "--interval",
        type=float,
        default=0.15,
        help="Seconds between camera captures; inference itself may take longer.",
    )
    parser.add_argument(
        "--save-dir",
        default=str(Path.home() / "railway_detector" / "captures"),
        help="Directory for snapshots saved when a defect is detected.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without opening a preview window (still saves detection snapshots).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_path = Path(args.model).expanduser()
    if not model_path.exists():
        raise SystemExit(f"Model not found: {model_path}")

    save_dir = Path(args.save_dir).expanduser()
    save_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path), task="detect")
    camera = Picamera2()
    camera.configure(
        camera.create_preview_configuration(
            main={"size": (args.width, args.height), "format": "RGB888"},
            buffer_count=2,
        )
    )
    camera.start()
    time.sleep(1.0)  # allow exposure and white balance to settle

    window = "Railway defect detector"
    if not args.headless:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    print("Live detection started. Press q in the preview window to quit.")
    print(f"Model: {model_path}")
    try:
        while True:
            started = time.monotonic()
            # Picamera2 RGB888 returns an RGB array; Ultralytics accepts RGB arrays.
            frame = camera.capture_array()
            result = model.predict(
                source=frame,
                imgsz=args.imgsz,
                conf=args.conf,
                device="cpu",
                verbose=False,
            )[0]
            annotated = result.plot()

            defect_count = 0
            if result.boxes is not None:
                for cls_id in result.boxes.cls.tolist():
                    label = str(result.names.get(int(cls_id), int(cls_id))).lower()
                    if "defect" in label and "non-defect" not in label:
                        defect_count += 1

            elapsed = time.monotonic() - started
            status = f"{elapsed:.2f}s/frame | detections: {len(result.boxes) if result.boxes is not None else 0}"
            cv2.putText(
                annotated,
                status,
                (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            if defect_count:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                output = save_dir / f"defect_{stamp}.jpg"
                cv2.imwrite(str(output), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                print(f"Defect-class detections: {defect_count}; saved {output}")

            if not args.headless:
                # OpenCV expects BGR for display; Picamera2 frame and result.plot() are RGB.
                cv2.imshow(window, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            remaining = args.interval - (time.monotonic() - started)
            if remaining > 0:
                time.sleep(remaining)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        camera.stop()
        if not args.headless:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
