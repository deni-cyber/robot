import time
from shared import Detection
from detector import *  # your class
from shared import MODELPATH

def vision_process(vision_queue):
    detector = LitterDetector( MODELPATH )  # path to your model

    try:
        while True:
            result = detector.detect()

            if result is None:
                detection = Detection(
                    detected=False,
                    confidence=0.0,
                    x=0.0,
                    y=0.0,
                    distance=0.0,
                    timestamp=time.time()
                )
                print("no detectable object")
            else:
                detection = Detection(
                    detected=True,
                    confidence=result["confidence"],
                    x=result["nx"],   # already normalized
                    y=result["ny"],
                    distance=result.get("distance", 0.0),
                    timestamp=time.time()
                )
                print(detection)
            # Non-blocking queue push
            if not vision_queue.full():
                if vision_queue.full():
                    vision_queue.get()  # discard old

                vision_queue.put(detection)
                
            # Small delay to stabilise CPU usage
            time.sleep(0.03)  # ~30 FPS cap

    finally:
        detector.release()
