import time
import cv2
from shared import Detection
from detector import LitterDetector
from shared import MODELPATH

def vision_process(vision_queue, frame_queue):
    """
    Captures video, runs inference, draws debug info, 
    and distributes data to the Brain and Web processes.
    """
    # Initialize the detector inside the process
    detector = LitterDetector(MODELPATH)
    
    print("[VISION] AI Inference process started.")

    try:
        while True:
            # 1. Get detection data and the actual image frame
            # (Note: Requires the update to detector.py we discussed)
            result, frame = detector.detect()

            if frame is None:
                continue

            detection = None
            h, w, _ = frame.shape

            # 2. Process Detection Results
            if result:
                detection = Detection(
                    detected=True,
                    confidence=result["confidence"],
                    x=result["nx"],   
                    y=result["ny"],
                    distance=result.get("distance", 0.0),
                    timestamp=time.time()
                )

                # --- DRAWING FOR WEB STREAM ---
                # Convert normalized (0-1) to pixel coordinates
                ix = int(result["nx"] * w)
                iy = int(result["ny"] * h)
                
                # Draw a target crosshair and label
                cv2.drawMarker(frame, (ix, iy), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
                cv2.putText(frame, f"Litter {result['confidence']:.2f}", (ix + 10, iy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                # No object found
                detection = Detection(
                    detected=False,
                    confidence=0.0,
                    x=0.0,
                    y=0.0,
                    distance=0.0,
                    timestamp=time.time()
                )
                cv2.putText(frame, "Scanning...", (10, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            # 3. Update the Vision Queue (for the Brain)
            # We use a "Drop Oldest" strategy to keep the robot responsive
            if vision_queue.full():
                try:
                    vision_queue.get_nowait()
                except:
                    pass
            vision_queue.put(detection)

            # 4. Update the Frame Queue (for the Web Server)
            # Only put if the web server is ready to avoid memory backup
            if not frame_queue.full():
                frame_queue.put(frame)

            # 5. Maintain Frame Rate (Approx 30 FPS)
            time.sleep(0.01)

    except Exception as e:
        print(f"[VISION ERROR] {e}")
    finally:
        detector.release()