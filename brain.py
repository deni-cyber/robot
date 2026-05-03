from shared import RobotState, MotionCommand, ArmCommand, Status

def brain_process(vision_queue, motion_queue, arm_queue, status_queue, control_queue):
    state = RobotState.SEARCHING

    while True:
        # Handle manual control
        if not control_queue.empty():
            cmd = control_queue.get()
            if cmd == "STOP":
                state = RobotState.IDLE

        if not vision_queue.empty():
            detection = vision_queue.get()

            if state == RobotState.SEARCHING:
                if detection.detected:
                    state = RobotState.TARGET_LOCKED

            elif state == RobotState.TARGET_LOCKED:
                if abs(detection.x - 0.5) < 0.1:
                    state = RobotState.APPROACHING

            elif state == RobotState.APPROACHING:
                if detection.y > 0.8:
                    state = RobotState.PICKING

            elif state == RobotState.PICKING:
                if not arm_queue.full():
                    arm_queue.put(ArmCommand("PICK"))
                state = RobotState.SEARCHING

            # Motion logic
            if state in [RobotState.SEARCHING, RobotState.TARGET_LOCKED]:
                angular = (detection.x - 0.5)
                linear = 0.0
            elif state == RobotState.APPROACHING:
                angular = (detection.x - 0.5)
                linear = 0.3
            else:
                angular = 0.0
                linear = 0.0

            if not motion_queue.full():
                motion_queue.put(MotionCommand(linear, angular))

            if not status_queue.full():
                status_queue.put(Status(state.name, detection.detected, detection.x, detection.y))