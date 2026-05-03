from shared import RobotState, MotionCommand, Status
import time

def brain_process(vision_queue, motion_queue, arm_queue, status_queue, control_queue):

    state = RobotState.SEARCHING

    target_locked = False
    stable_count = 0

    CENTER_TOL = 0.08
    STABLE_FRAMES = 5

    last_detection = None
    arm_busy = False
    bin_full = False

    while True:

        # ================= CONTROL INPUT =================
        if not control_queue.empty():
            cmd = control_queue.get()

            if cmd == "STOP":
                state = RobotState.IDLE
                motion_queue.put(MotionCommand(0, 0))

        # ================= STATUS FROM ARDUINO =================
        if not status_queue.empty():
            msg = status_queue.get()

            if msg == "ARM_START":
                arm_busy = True

            elif msg == "ARM_DONE":
                arm_busy = False
                state = RobotState.SEARCHING

            elif msg == "BIN_FULL":
                bin_full = True
                state = RobotState.IDLE
                motion_queue.put(MotionCommand(0, 0))

        # ================= VISION =================
        if not vision_queue.empty():
            detection = vision_queue.get()
            last_detection = detection

            if not detection.detected:
                stable_count = 0
                target_locked = False
                continue

            # -------- alignment check --------
            centered = abs(detection.x - 0.5) < CENTER_TOL

            if centered:
                stable_count += 1
            else:
                stable_count = 0

            if stable_count >= STABLE_FRAMES:
                target_locked = True

        # ================= STATE MACHINE =================

        if state == RobotState.IDLE:
            motion_queue.put(MotionCommand(0, 0))

        # ---------------- SEARCHING ----------------
        elif state == RobotState.SEARCHING:

            if last_detection and last_detection.detected:

                error = last_detection.x - 0.5
                angular = error * 1.5
                linear = 0.0

                motion_queue.put(MotionCommand(linear, angular))

                state = RobotState.TARGET_LOCKED

        # ---------------- TARGET LOCK ----------------
        elif state == RobotState.TARGET_LOCKED:

            if last_detection is None:
                state = RobotState.SEARCHING
                continue

            error = last_detection.x - 0.5

            motion_queue.put(MotionCommand(0.0, error * 1.5))

            # send target to Arduino (only once when stable)
            if target_locked and not arm_busy:

                x = int(last_detection.x * 96)
                y = int(last_detection.y * 96)

                arm_queue.put(f"TARGET:{x},{y}")

                state = RobotState.APPROACHING

        # ---------------- APPROACHING ----------------
        elif state == RobotState.APPROACHING:

            if last_detection is None:
                state = RobotState.SEARCHING
                continue

            error = last_detection.x - 0.5
            angular = error * 1.2

            # move forward until close
            linear = 0.25 if last_detection.distance < 0.15 else 0.0

            motion_queue.put(MotionCommand(linear, angular))

            # trigger pick when close + stable + not busy
            if (last_detection.distance < 0.15 and
                target_locked and
                not arm_busy):

                arm_queue.put("PICK")
                arm_busy = True

                state = RobotState.WAITING_PICK

        # ---------------- WAIT PICK ----------------
        elif state == RobotState.WAITING_PICK:

            motion_queue.put(MotionCommand(0, 0))

            # wait for Arduino confirmation
            if not arm_busy:
                state = RobotState.SEARCHING

        # ================= STATUS OUTPUT =================
        if last_detection:
            if not status_queue.full():
                status_queue.put(Status(
                    state.name,
                    last_detection.detected,
                    last_detection.x,
                    last_detection.y
                ))

        time.sleep(0.02)