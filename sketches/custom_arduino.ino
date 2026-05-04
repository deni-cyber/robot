#include <Servo.h>

#define BASESERVOPIN A0
#define ARM1SERVOPIN A1
#define ARM2SERVOPIN A2
#define GRIPSERVOPIN A3

Servo arm1servo, arm2servo, baseservo, gripservo;

// --- ARM GEOMETRY & CONSTANTS ---
const double L1 = 75.0; // Length of arm segment 1
const double L2 = 75.0; // Length of arm segment 2
const int GRIP_OPEN = 40;
const int GRIP_CLOSED = 90;

// --- PRESET POSITIONS ---
// Adjust these to fit your robot's physical setup
const double HOME_X = 75.0, HOME_Y = 0.0, HOME_Z = 75.0;
const double DROP_X = 0.0, DROP_Y = 80.0, DROP_Z = 50.0;

int angleToMicroseconds(double angle)
{
    return (int)(460.0 + (((2400.0 - 460.0) / 180.0) * angle));
}

void moveToAngle(double b, double a1, double a2, double g)
{
    arm1servo.writeMicroseconds(angleToMicroseconds(188 - a1));
    arm2servo.writeMicroseconds(angleToMicroseconds(a2 + 101));
    baseservo.writeMicroseconds(angleToMicroseconds(b + 90));
    gripservo.writeMicroseconds(angleToMicroseconds(g));
}

void moveToPos(double x, double y, double z, double g)
{
    double b = atan2(y, x) * (180 / PI);
    double l = sqrt(x * x + y * y);
    double h = sqrt(l * l + z * z);

    // Basic bounds checking to prevent math errors (acos of > 1.0)
    if (h > (L1 + L2))
        h = L1 + L2;

    double phi = atan2(z, l) * (180 / PI);
    double theta = acos((h / 2.0) / L1) * (180 / PI);

    double a1 = phi + theta;
    double a2 = phi - theta;

    moveToAngle(b, a1, a2, g);
}

// --- THE MISSION SEQUENCE ---
void executeFullPickSequence(double targetX, double targetY)
{
    // 1. Move to target (Assume Z is constant for ground pick, e.g., 10mm)
    moveToPos(targetX, targetY, 10.0, GRIP_OPEN);
    delay(1000);

    // 2. Close Gripper
    moveToPos(targetX, targetY, 10.0, GRIP_CLOSED);
    delay(800);

    // 3. Move to Drop position
    moveToPos(DROP_X, DROP_Y, DROP_Z, GRIP_CLOSED);
    delay(1500);

    // 4. Drop
    moveToPos(DROP_X, DROP_Y, DROP_Z, GRIP_OPEN);
    delay(800);

    // 5. Return Home
    moveToPos(HOME_X, HOME_Y, HOME_Z, GRIP_OPEN);
    Serial.println("COMPLETE"); // Signal to Pi (optional)
}

void setup()
{
    baseservo.attach(BASESERVOPIN, 460, 2400);
    arm1servo.attach(ARM1SERVOPIN, 460, 2400);
    arm2servo.attach(ARM2SERVOPIN, 460, 2400);
    gripservo.attach(GRIPSERVOPIN, 460, 2400);

    Serial.begin(115200);

    // Start at Home
    moveToPos(HOME_X, HOME_Y, HOME_Z, GRIP_OPEN);
}

void loop()
{
    if (Serial.available() > 0)
    {
        String cmd = Serial.readStringUntil('\n');

        if (cmd.startsWith("PICK"))
        {
            // Expected format: "PICK,75.0,20.0"
            int firstComma = cmd.indexOf(',');
            int secondComma = cmd.indexOf(',', firstComma + 1);

            if (firstComma != -1 && secondComma != -1)
            {
                double px = cmd.substring(firstComma + 1, secondComma).toFloat();
                double py = cmd.substring(secondComma + 1).toFloat();

                executeFullPickSequence(px, py);

                // Flush buffer so we don't repeat commands sent during move
                while (Serial.available() > 0)
                    Serial.read();
            }
        }
    }
}