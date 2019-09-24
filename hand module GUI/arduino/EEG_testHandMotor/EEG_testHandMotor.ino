#include <Servo.h>
#define upperLim 120
#define lowerLim 10

#define timeVar 250

typedef struct single_finger{
  byte enable;
  byte phase;
};

Servo thumb;
single_finger index = {5, 4};
single_finger middle = {7, 6};
single_finger ring = {9 ,8};
single_finger pinky = {11, 10};

volatile int dir, finger, t, pos;

unsigned long currentTime;

void setup() {
  // put your setup code here, to run once:
  pinMode(index.enable, OUTPUT);
  pinMode(index.phase, OUTPUT);
  pinMode(middle.enable, OUTPUT);
  pinMode(middle.phase, OUTPUT);
  Serial.begin(9600);
  currentTime = millis();
  thumb.attach(3);
  pos = upperLim;
  thumb.write(pos);
}

void loop() {
  // put your main code here, to run repeatedly:
  /*
   * For each finger there is an array, index 0 for directional pin and 1 for PWM
   */
  Serial.println("Input finger 0 - thumb, 1 - index , 2 - middle, 3 - ring, 4 - pinky):");
  while(!Serial.available());
  if(Serial.available() > 0){
    finger = Serial.read() - '0';
  }
  Serial.print("Finger = "); Serial.println(finger);

  Serial.println("Input direction (0 - open, 1 - close):");
  while(!Serial.available());
  if(Serial.available() > 0){
    dir = Serial.read() - '0';
  }
  Serial.print("Dir: "); Serial.println(dir);

  Serial.println("Input duration:");
  while(!Serial.available());
  if(Serial.available() > 0){
    t = Serial.read() - '0';
  }
  Serial.print("Time: "); Serial.println(t);

  currentTime = millis();
  switch(finger){
    case 0:
      runThumb(dir, t*timeVar);
      break;
    case 1:
      run(index, dir, t*timeVar);
      break;
    case 2:
      run(middle, dir, t*timeVar);
      break;
    case 3:
      run(ring, dir, t*timeVar);
      break;
    case 4:
      run(pinky, dir, t*timeVar);
      break;
    default:
      break;
  }
}

void run(single_finger _finger, int _dir, int _t){
  digitalWrite(_finger.enable, HIGH);
  digitalWrite(_finger.phase, _dir);
  delay(_t);
  digitalWrite(_finger.enable, LOW);
}

void runThumb(int _dir, int _t){
  if(_dir){
    currentTime = millis();
    while(((millis() - currentTime) < _t) && pos >= lowerLim){
      pos = pos - 1;
      thumb.write(pos);              // tell servo to go to position in variable 'pos'
      delay(20);
    }
  } else{
    currentTime = millis();
    while(((millis() - currentTime) < _t) && pos <= upperLim){
      pos = pos + 1;
      thumb.write(pos);              // tell servo to go to position in variable 'pos'
      delay(20);
    }
  }
}

