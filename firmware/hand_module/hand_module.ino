#include <Servo.h>
#define thumbLimUp 120
#define thumbLimDown 10
#define fingerSpeed 20 // delay after 1 tick
#define resolution 40 // 3600/40/90 = 1 -> resolution of 1 degree
#define motorLimit 3600 // max amount of milliseconds motor can continuously rotate

typedef struct single_finger{
  byte enable;
  byte phase;
  unsigned int pos;
};

typedef struct finger_packet{
  unsigned int mode;
  byte thumb;
  byte index;
  byte middle;
  byte ring;
  byte pinky;
};

int processing_figure[5] = {0, 0, 0, 0, 0};

Servo thumb;
single_finger index = {5, 4, 0};
single_finger middle = {7, 6, 0};
single_finger ring = {9 ,8, 0};
single_finger pinky = {11, 10, 0};
finger_packet packet;

volatile int thumbPos;
unsigned long currentTime;

void setup() {
  // put your setup code here, to run once:
  pinMode(index.enable, OUTPUT);
  pinMode(index.phase, OUTPUT);
  pinMode(middle.enable, OUTPUT);
  pinMode(middle.phase, OUTPUT);
  pinMode(ring.enable, OUTPUT);
  pinMode(ring.phase, OUTPUT);
  pinMode(pinky.enable, OUTPUT);
  pinMode(pinky.phase, OUTPUT);
  Serial.begin(115200);
  
  currentTime = millis();
  thumb.attach(3);
  
  thumbPos = thumbLimUp;
  thumb.write(thumbPos);

  for(int i = 0; i < 3; i++){
    digitalWrite(13, HIGH);
    delay(50);
    digitalWrite(13, LOW);
    delay(50);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  /*
   * For each finger there is an array, index 0 for directional pin and 1 for PWM
   */
  while(!Serial.available());
  if(Serial.available() > 0){
    Serial.readBytes((uint8_t*)&packet, sizeof(packet));
  }
  switch(packet.mode){
    case 0:
      processing_figure[0] = packet.thumb;
      processing_figure[1] = packet.index;
      processing_figure[2] = packet.middle;
      processing_figure[3] = packet.ring;
      processing_figure[4] = packet.pinky;
      setMultiFinger(processing_figure);
      break;
    case 1:
      if(packet.thumb){
        if(thumbPos < thumbLimUp - packet.thumb){
          thumbPos+= packet.thumb;
        }
        thumb.write(thumbPos);
        break;
      }
      if(packet.index){
        index.pos = 0;
        run(&index, 0, packet.index * resolution);
        break;
      }
      if(packet.middle){
        middle.pos = 0;
        run(&middle, 0, packet.middle * resolution);
        break;
      }
      if(packet.ring){
        ring.pos = 0;
        run(&ring, 0, packet.ring * resolution);
        break;
      }
      if(packet.pinky){
        pinky.pos = 0;
        run(&pinky, 0, packet.pinky * resolution);
        break;
      }
    case 2:
      if(packet.thumb){
        if(thumbPos > thumbLimDown + packet.thumb){
          thumbPos -= packet.thumb;
        }
        thumb.write(thumbPos);
        break;
      }
      if(packet.index){
        index.pos = 0;
        run(&index, 1, packet.index * resolution);
        break;
      }
      if(packet.middle){
        middle.pos = 0;
        run(&middle, 1, packet.middle * resolution);
        break;
      }
      if(packet.ring){
        ring.pos = 0;
        run(&ring, 1, packet.ring * resolution);
        break;
      }
      if(packet.pinky){
        pinky.pos = 0;
        run(&pinky, 1, packet.pinky * resolution);
        break;
      }
  }
}

void setMultiFinger(int data[5]){
  /*
   * Following the array will be the new position of thumb, index, middle, ring, pinky
   * try to run all 5 fingers together and using millis() to stop any finger that has reached the required position
   */
   int newIndexPos = data[1]*resolution;
   int newMiddlePos = data[2]*resolution;
   int newRingPos = data[3]*resolution;
   int newPinkyPos = data[4]*resolution;
   int offsetIndex, offsetMiddle, offsetRing, offsetPinky, offsetMax;
   
   if(newIndexPos > index.pos){
    //digitalWrite(index.enable, HIGH);
    digitalWrite(index.phase, HIGH);
    offsetIndex = newIndexPos - index.pos;
   } else if(newIndexPos < index.pos){
    //digitalWrite(index.enable, HIGH);
    digitalWrite(index.phase, LOW);
    offsetIndex = index.pos - newIndexPos;
   } else{
    digitalWrite(index.enable, LOW);
    offsetIndex = 0;
   }

   offsetMax = offsetIndex;

   if(newMiddlePos > middle.pos){
    //digitalWrite(middle.enable, HIGH);
    digitalWrite(middle.phase, HIGH);
    offsetMiddle = newMiddlePos - middle.pos;
   } else if(newMiddlePos < middle.pos){
    //digitalWrite(middle.enable, HIGH);
    digitalWrite(middle.phase, LOW);
    offsetMiddle = middle.pos - newMiddlePos;
   } else{
    digitalWrite(middle.enable, LOW);
    offsetMiddle = 0;
   }

   if(offsetMiddle > offsetMax){
    offsetMax = offsetMiddle;
   }

   if(newRingPos > ring.pos){
    //digitalWrite(ring.enable, HIGH);
    digitalWrite(ring.phase, HIGH);
    offsetRing = newRingPos - ring.pos;
   } else if(newRingPos < ring.pos){
    //digitalWrite(ring.enable, HIGH);
    digitalWrite(ring.phase, LOW);
    offsetRing = ring.pos - newRingPos;
   } else{
    digitalWrite(ring.enable, LOW);
    offsetRing = 0;
   }

   if(offsetRing > offsetMax){
    offsetMax = offsetRing;
   }

   if(newPinkyPos > pinky.pos){
    //digitalWrite(pinky.enable, HIGH);
    digitalWrite(pinky.phase, HIGH);
    offsetPinky = newPinkyPos - pinky.pos;
   } else if(newPinkyPos < pinky.pos){
    //digitalWrite(pinky.enable, HIGH);
    digitalWrite(pinky.phase, LOW);
    offsetPinky = pinky.pos - newPinkyPos;
   } else{
    digitalWrite(pinky.enable, LOW);
    offsetPinky = 0;
   }

   if(offsetPinky > offsetMax){
    offsetMax = offsetPinky;
   }

   currentTime = millis();
   int running_interval = offsetMax * 0.025; // this is because the current resolution is 40, change this value to 1/resolution if the resolution changes
   
   if(offsetIndex > 0){
    digitalWrite(index.enable, HIGH);
   }
   if(offsetMiddle > 0){
    digitalWrite(middle.enable, HIGH);
   }
   if(offsetRing > 0){
    digitalWrite(ring.enable, HIGH);
   }
   if(offsetPinky > 0){
    digitalWrite(pinky.enable, HIGH);
   }
   
   for(int i = 0; i < running_interval; i++){
    if(millis() - currentTime < offsetIndex || millis() - currentTime < offsetMiddle || millis() - currentTime < offsetRing || millis() - currentTime < offsetPinky){
      delay(resolution);
      if((millis() - currentTime) >= offsetIndex){
      digitalWrite(index.enable, LOW);
      }
      if((millis() - currentTime) >= offsetMiddle){
        digitalWrite(middle.enable, LOW);
      }
      if((millis() - currentTime) >= offsetRing){
        digitalWrite(ring.enable, LOW);
      }
      if((millis() - currentTime) >= offsetPinky){
        digitalWrite(pinky.enable, LOW);
      }
    }
   }

   index.pos = newIndexPos;
   middle.pos = newMiddlePos;
   ring.pos = newRingPos;
   pinky.pos = newPinkyPos;
   
   thumb.write(data[0]);
}

void setFinger(void *Data, int newPos){
  /*
   * Each finger, apart from thumb, runs within the motorLimit (default 3600)
   * 3600 here is 3600 ms continuous rotation, assuming every finger starts at 0 (wide open)
   * Fingers have real limit from 0 to 90 degree corresponding to 3600, hence for 1 degree change, the motor needs to 
   * rotate for 3600/90 = 40 ms.
   * To calculate current angular position of finger, use finger.pos/resolution
   * 
   * Input int newPos is angular value (degree)
   */

   single_finger *fingerData = (single_finger*) Data;
   int newRunTime = newPos*resolution;
   int offset = newRunTime - fingerData->pos;
   if(offset > 0){
    // new position is pointing in, hence _dir = 1
    fingerData->pos = newRunTime;
    run(Data, 1, offset);
   }
   else if(offset < 0){
    // new position is pointing in, hence _dir = 1
    fingerData->pos = newRunTime;
    run(Data, 0, -offset);
   }
}

void run(void *Data, int _dir, int _t){
  // _dir: 0 - open, 1 - close
  single_finger *fingerData = (single_finger*) Data;
  digitalWrite(fingerData->enable, HIGH);
  digitalWrite(fingerData->phase, _dir);
  delay(_t);
  digitalWrite(fingerData->enable, LOW);
}

void setThumb(int _dir, int _t){
  if(_dir){
    currentTime = millis();
    while(((millis() - currentTime) < _t) && thumbPos >= thumbLimDown){
      thumbPos = thumbPos - 1;
      thumb.write(thumbPos);              // tell servo to go to position in variable 'pos'
      delay(fingerSpeed);
    }
  } else{
    currentTime = millis();
    while(((millis() - currentTime) < _t) && thumbPos <= thumbLimUp){
      thumbPos = thumbPos + 1;
      thumb.write(thumbPos);              // tell servo to go to position in variable 'pos'
      delay(fingerSpeed);
    }
  }
}

