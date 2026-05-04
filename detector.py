import cv2
from edge_impulse_linux.image import ImageImpulseRunner

class LitterDetector:
    def __init__(self, model_path, camera_index=0):
        self.runner = ImageImpulseRunner(model_path)
        self.runner.init()
        self.labels = self.runner.labels

        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise Exception("Camera not accessible")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # smoothing
        self.prev_x = None
        self.prev_y = None
        self.alpha = 0.6

    def _get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def _smooth(self, x, y):
        if self.prev_x is None:
            self.prev_x, self.prev_y = x, y
            return x, y

        x_s = self.alpha * x + (1 - self.alpha) * self.prev_x
        y_s = self.alpha * y + (1 - self.alpha) * self.prev_y

        self.prev_x, self.prev_y = x_s, y_s
        return x_s, y_s

    def detect(self, threshold=0.5):
        frame = self._get_frame()
        if frame is None:
            return None

        model_input = cv2.resize(frame, (96, 96))
        features, _ = self.runner.get_features_from_image(model_input)
        result = self.runner.classify(features)

        boxes = result.get("result", {}).get("bounding_boxes", [])
        if not boxes:
            self.prev_x = None
            self.prev_y = None
            return None

        h, w, _ = frame.shape
        scale_x = w / 96
        scale_y = h / 96

        detections = []

        for bb in boxes:
            if bb["value"] >= threshold:
                cx = (bb["x"] + bb["width"] / 2) * scale_x
                cy = (bb["y"] + bb["height"] / 2) * scale_y

                nx = cx / w
                ny = cy / h

                nx, ny = self._smooth(nx, ny)

                real_height = bb["height"] * scale_y

                detections.append({
                    "label": bb["label"],
                    "confidence": bb["value"],
                    "nx": nx,
                    "ny": ny,
                    "distance": 1.0 / (real_height + 1e-5)
                })

        if not detections:
            return None

        return max(detections, key=lambda d: d["confidence"])

    def release(self):
        self.cap.release()
        self.runner.stop()
