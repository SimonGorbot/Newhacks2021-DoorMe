#include <Servo.h>
#define SERVO_PIN 3
#define SOUND_SENSOR_PIN 8

#define SERVO_IN_POS 110
#define SERVO_OUT_POS 30

Servo doorActuator;




void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  doorActuator.attach(SERVO_PIN);
  pinMode(SOUND_SENSOR_PIN, INPUT);
  doorActuator.write(SERVO_IN_POS);
}

bool prevState = false;
bool currState = false;

int debounce = 200;
unsigned long long lastKnock = 0;
int sequenceRight = 0;
int shortKnock = 1000;
int longKnock = 3000;

bool locked = false;
void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available())
  {
    char in = Serial.read();
    switch(in){
      case 'L':
        doorActuator.write(SERVO_OUT_POS);
        locked = true;
        break;
      case 'U':
        doorActuator.write(SERVO_IN_POS);
        locked = false;
        break;
    }
      
  }
  currState = digitalRead(SOUND_SENSOR_PIN);
  if(currState && (millis() - lastKnock > debounce))
  {
    Serial.println("Knock");
    if(sequenceRight == 0 && millis() - lastKnock < shortKnock)
    {
      sequenceRight++;
      int ti = millis() - lastKnock;
      Serial.println(ti);
    }
    if(sequenceRight == 1 && (millis() - lastKnock > shortKnock) && (millis() - lastKnock < longKnock))
    {
      locked = true;
      doorActuator.write(SERVO_OUT_POS);
      Serial.println("done");
    }
    lastKnock = millis();
  }
  if(millis() - lastKnock > longKnock && sequenceRight != 0)
  {
    sequenceRight = 0;
  }
  prevState = currState;
}
