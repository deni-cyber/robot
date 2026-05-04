#THIS FILE IS THE BRAIN OF THE ROBOT, IT PROCESSES VISION DATA AND DECIDES WHAT TO DO.
# IT RECEIVES DATA FROM THE VISION MODULE, DECIDES WHETHER TO LOCK ONTO A TARGET, AND THEN SENDS COMMANDS TO THE ACTUATOR MODULE TO PICK UP THE TARGET.
# IT ALSO SENDS STATUS UPDATES TO THE WEB MODULE TO DISPLAY ON THE DASHBOARD.

from shared import RobotState, ArmCommand, Status

def brain_process(vision_queue, motion_queue, arm_queue, status_queue, control_queue):
    state = RobotState.IDLE

    locked_target = None
    stable_count = 0
    STABLE_N = 3
    arm_busy = False

    while True:
        if vision_queue.empty():
            continue

        detec_obj = vision_queue.get()

        # ---------------- LOCK LOGIC ----------------
        if detec_obj.detec_objected:
            if locked_target is None:
                locked_target = detec_obj
                stable_count = 1
            else:
                # Check if it's roughly the same target
                if abs(detec_obj.x - locked_target.x) < 0.05 and abs(detec_obj.y - locked_target.y) < 0.05:
                    stable_count += 1
                    locked_target = detec_obj
                    print(f"[LOCK] stable_count={stable_count}, x={detec_obj.x:.2f}, y={detec_obj.y:.2f}")
                else:
                    # New target → reset lock
                    locked_target = detec_obj
                    stable_count = 1
        else:
            locked_target = None
            stable_count = 0
            arm_busy = False
            state = RobotState.IDLE

        # ---------------- STATE LOGIC ----------------
        if locked_target is not None:
            state = RobotState.TARGET_LOCKED

            if stable_count >= STABLE_N and not arm_busy:
                state = RobotState.PICKING

                # Convert to real coordinates (simple mapping)
                X = (locked_target.x - 0.5) * 20.0
                Y = locked_target.distance * 30.0

                if not arm_queue.full():
                    arm_queue.put(ArmCommand("PICK", X, Y))
                    print(f"[BRAIN] PICK sent → X:{X:.2f}, Y:{Y:.2f}")
                    arm_busy = True

        # ---------------- STATUS ----------------
        if not status_queue.full():
            status_queue.put(Status(
                state.name,
                detec_obj.detec_objected,
                detec_obj.x,
                detec_obj.y
            ))