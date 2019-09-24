#include <Servo.h>
#define upperLim 120
#define lowerLim 10

#define timeVar 40

typedef struct single_finger{
  byte enable;
  byte phase;
};

Servo thumb;
single_finger index = {5, 4};
single_finger middle = {7, 6};
single_finger ring = {9 ,8};
single_finger pinky = {11, 10};

volatile int pos, key;

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
  while(!Serial.available());
  if(Serial.available() > 0){
    key = Serial.read() - '0';
  }
  
  switch(key){
    case 0:
      runThumb(0, timeVar);
      break;
    case 1:
      runThumb(1, timeVar);
      break;
    case 4:
      run(index, 1, timeVar);
      break;
    case 7:
      run(index, 0, timeVar);
      break;
    case 5:
      run(middle, 1, timeVar);
      break;
    case 8:
      run(middle, 0, timeVar);
      break;
    case 6:
      run(ring, 1, timeVar);
      break;
    case 9:
      run(ring, 0, timeVar);
      break;
    case 2:
      run(pinky, 1, timeVar);
      break;
    case 3:
      run(pinky, 0, timeVar);
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

