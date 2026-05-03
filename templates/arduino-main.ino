#include <Servo.h>

// ================= SERVOS =================
Servo base;
Servo shoulder;
Servo gripper;

// current positions
float basePos = 90;
float shoulderPos = 10;
float gripperPos = 135;

// targets
float baseTarget = 90;
float shoulderTarget = 10;
float gripperTarget = 135;

// ================= MOTORS =================
int in1 = 2;
int in2 = 3;
int in3 = 4;
int in4 = 7;

int ena = 5;
int enb = 6;

int speedSlow = 90;

// ================= ULTRASONIC =================
#define TRIG_BIN 13
#define ECHO_BIN A0

#define TRIG_FRONT 8
#define ECHO_FRONT 9

// ================= STATE =================
enum ArmState
{
  ARM_IDLE,
  ARM_MOVE_TO_TARGET,
  ARM_GRASP,
  ARM_LIFT,
  ARM_DROP,
  ARM_HOME
};

ArmState armState = ARM_IDLE;

// ================= TARGET FROM PI =================
float targetX = 48;
float targetY = 48;

// ================= FLAGS =================
bool binFull = false;
bool motionBlocked = false;

// ================= TIMING =================
unsigned long armTimer = 0;

// ================= SETUP =================
void setup()
{
  Serial.begin(9600);

  base.attach(10);
  shoulder.attach(11);
  gripper.attach(12);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  pinMode(ena, OUTPUT);
  pinMode(enb, OUTPUT);

  pinMode(TRIG_BIN, OUTPUT);
  pinMode(ECHO_BIN, INPUT);

  pinMode(TRIG_FRONT, OUTPUT);
  pinMode(ECHO_FRONT, INPUT);

  stopMotors();

  Serial.println("SYSTEM READY");
}

// ================= MOTOR CONTROL =================
void setMotor(int left, int right)
{
  analogWrite(ena, left);
  analogWrite(enb, right);

  digitalWrite(in1, left > 0);
  digitalWrite(in2, left == 0);

  digitalWrite(in3, right > 0);
  digitalWrite(in4, right == 0);
}

void forward() { setMotor(speedSlow, speedSlow); }
void left() { setMotor(0, speedSlow); }
void right() { setMotor(speedSlow, 0); }
void stopMotors() { setMotor(0, 0); }

// ================= ULTRASONIC =================
float readBin()
{
  digitalWrite(TRIG_BIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_BIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_BIN, LOW);

  long t = pulseIn(ECHO_BIN, HIGH);
  return t * 0.034 / 2;
}

float readFront()
{
  digitalWrite(TRIG_FRONT, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_FRONT, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_FRONT, LOW);

  long t = pulseIn(ECHO_FRONT, HIGH);
  return t * 0.034 / 2;
}

// ================= SERVO SMOOTH STEP =================
void stepServo(Servo &s, float &current, float target, float step)
{
  if (abs(current - target) < step)
  {
    current = target;
  }
  else
  {
    current += (current < target) ? step : -step;
  }
  s.write((int)current);
}

// ================= ARM IK (your mapping system) =================
void computeTarget()
{
  float correctedX = targetX - 6;
  correctedX = constrain(correctedX, 0, 96);

  baseTarget = map(correctedX, 0, 96, 30, 150);
  shoulderTarget = map(targetY, 0, 96, 70, 130);
}

// ================= ARM STATE MACHINE =================
void updateArm()
{

  switch (armState)
  {

  case ARM_IDLE:
    break;

  case ARM_MOVE_TO_TARGET:
    computeTarget();

    stepServo(base, basePos, baseTarget, 1);
    stepServo(shoulder, shoulderPos, shoulderTarget, 1);

    if (abs(basePos - baseTarget) < 2 &&
        abs(shoulderPos - shoulderTarget) < 2)
    {

      armTimer = millis();
      armState = ARM_GRASP;
    }
    break;

  case ARM_GRASP:
    stepServo(gripper, gripperPos, 150, 2);

    if (millis() - armTimer > 500)
    {
      armState = ARM_LIFT;
    }
    break;

  case ARM_LIFT:
    stepServo(shoulder, shoulderPos, 45, 1);

    if (millis() - armTimer > 1200)
    {
      armState = ARM_HOME;
    }
    break;

  case ARM_HOME:
    stepServo(base, basePos, 90, 1);
    stepServo(shoulder, shoulderPos, 10, 1);
    stepServo(gripper, gripperPos, 135, 2);

    if (millis() - armTimer > 2000)
    {
      Serial.println("ARM_DONE");
      armState = ARM_IDLE;
    }
    break;
  }
}

// ================= SERIAL =================
void handleSerial(String cmd)
{

  if (cmd.startsWith("TARGET:"))
  {
    int c = cmd.indexOf(',');

    targetX = cmd.substring(7, c).toFloat();
    targetY = cmd.substring(c + 1).toFloat();

    Serial.println("TARGET_OK");
  }

  else if (cmd == "PICK")
  {
    if (armState == ARM_IDLE)
    {
      armState = ARM_MOVE_TO_TARGET;
      Serial.println("ARM_START");
    }
  }

  else if (cmd == "STOP")
  {
    stopMotors();
  }
}

// ================= LOOP =================
void loop()
{

  // --------- sensors ----------
  float binDist = readBin();
  float frontDist = readFront();

  if (binDist < 10)
  {
    binFull = true;
    Serial.println("BIN_FULL");
  }

  motionBlocked = (frontDist < 15 || binFull);

  // --------- serial ----------
  if (Serial.available())
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    handleSerial(cmd);
  }

  // --------- safety ----------
  if (motionBlocked)
    stopMotors();

  // --------- arm ----------
  updateArm();
}