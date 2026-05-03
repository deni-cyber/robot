#include <Servo.h>

// -------------------- STATE ENUMS --------------------
enum DriveState
{
  DRIVE_IDLE,
  DRIVE_MOVING
};
enum ArmState
{
  ARM_IDLE,
  ARM_PICKING,
  ARM_RESTING
};

// -------------------- GLOBAL STATE --------------------
DriveState driveState = DRIVE_IDLE;
ArmState armState = ARM_IDLE;

// Motion targets
float linear_cmd = 0.0;
float angular_cmd = 0.0;

// Arm timing
unsigned long armStartTime = 0;
const unsigned long PICK_DURATION = 2000; // ms

// Servo
Servo armServo;
int armPin = 9;

// -------------------- SETUP --------------------
void setup()
{
  Serial.begin(115200);
  armServo.attach(armPin);
}

// -------------------- LOOP --------------------
void loop()
{
  readSerial();
  updateDrive();
  updateArm();
}

// -------------------- SERIAL PARSER --------------------
void readSerial()
{
  if (Serial.available())
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("MOVE"))
    {
      handleMove(cmd);
    }
    else if (cmd.startsWith("ARM"))
    {
      handleArm(cmd);
    }
    else if (cmd == "PING")
    {
      Serial.println("ACK");
    }
    else
    {
      Serial.println("ERR");
    }
  }
}

// -------------------- COMMAND HANDLERS --------------------
void handleMove(String cmd)
{
  int first = cmd.indexOf(',');
  int second = cmd.indexOf(',', first + 1);

  if (first == -1 || second == -1)
  {
    Serial.println("ERR");
    return;
  }

  linear_cmd = cmd.substring(first + 1, second).toFloat();
  angular_cmd = cmd.substring(second + 1).toFloat();

  driveState = DRIVE_MOVING;

  Serial.println("ACK");
}

void handleArm(String cmd)
{
  if (armState != ARM_IDLE)
  {
    Serial.println("ERR"); // busy
    return;
  }

  if (cmd.endsWith("PICK"))
  {
    armState = ARM_PICKING;
    armStartTime = millis();
    Serial.println("ACK");
  }
  else if (cmd.endsWith("REST"))
  {
    armState = ARM_RESTING;
    armStartTime = millis();
    Serial.println("ACK");
  }
  else
  {
    Serial.println("ERR");
  }
}

// -------------------- DRIVE STATE MACHINE --------------------
void updateDrive()
{
  switch (driveState)
  {

  case DRIVE_IDLE:
    stopMotors();
    break;

  case DRIVE_MOVING:
    applyMotion(linear_cmd, angular_cmd);
    break;
  }
}

// -------------------- ARM STATE MACHINE --------------------
void updateArm()
{
  switch (armState)
  {

  case ARM_IDLE:
    break;

  case ARM_PICKING:
    performPick();
    if (millis() - armStartTime > PICK_DURATION)
    {
      armState = ARM_IDLE;
      Serial.println("DONE");
    }
    break;

  case ARM_RESTING:
    performRest();
    if (millis() - armStartTime > 1000)
    {
      armState = ARM_IDLE;
      Serial.println("DONE");
    }
    break;
  }
}

// -------------------- MOTOR CONTROL --------------------
void applyMotion(float linear, float angular)
{
  // Replace with your motor driver logic

  float left = linear - angular;
  float right = linear + angular;

  // Example debug
  Serial.print("L:");
  Serial.print(left);
  Serial.print(" R:");
  Serial.println(right);
}

void stopMotors()
{
  // Set motor speeds to zero
}

// -------------------- ARM ACTIONS --------------------
void performPick()
{
  // Example motion
  armServo.write(30); // down
}

void performRest()
{
  armServo.write(90); // up
}