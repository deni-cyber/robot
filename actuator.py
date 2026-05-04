#THIS FILE IS THE ACTUATOR MODULE, IT RECEIVES COMMANDS FROM THE BRAIN AND CONTROLS THE PHYSICAL ARM TO PICK UP LITTER.
# IT ALSO UPDATES THE STATUS OF THE ROBOT TO "PICKING" WHEN IT STARTS THE PICKING SEQUENCE, AND THEN BACK TO "IDLE" ONCE THE SEQUENCE IS LIKELY COMPLETE.
import time

def actuator_process(arm_queue):
    # ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    
    # How long the Arduino takes to do the full Home -> Pick -> Drop -> Home sequence
    SEQUENCE_TIME = 8.0 
    last_cmd_time = 0

    print("[ACTUATOR] Sequence mode active.")

    while True:
        if not arm_queue.empty():
            arm = arm_queue.get()
            current_time = time.time()

            if arm.action == "PICK":
                # Only send if the previous physical sequence has likely finished
                if current_time - last_cmd_time > SEQUENCE_TIME:
                    cmd = f"PICK,{arm.x:.2f},{arm.y:.2f}\n"
                    print(f"[ACTUATOR] Triggering Mission: {cmd.strip()}")
                    # ser.write(cmd.encode())
                    #UPDATING STATUS OF THE ROBOT TO PICKING
                    last_cmd_time = current_time
                else:
                    print("[ACTUATOR] Busy: Sequence in progress, command ignored.")

        time.sleep(0.05)