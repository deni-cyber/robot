import time
from shared import Detection

def vision_process(vision_queue):
    while True:
        # ---- Replace this with real camera + model ----
        detected = True
        confidence = 0.8
        x, y = 0.4, 0.5  # normalized coords
        # ---------------------------------------------

        detection = Detection(detected, confidence, x, y, time.time())

        if not vision_queue.full():
            vision_queue.put(detection)

        time.sleep(0.05)  # ~20 FPS cap