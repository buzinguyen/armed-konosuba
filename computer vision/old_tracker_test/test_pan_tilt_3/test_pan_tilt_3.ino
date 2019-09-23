#include <Servo.h> 

Servo LRmove;
Servo UDmove;

byte currentUD;
byte currentLR;

typedef struct serial_packet{
  byte LR; //0: subtract, 1: add
  byte UD; //0: subtract, 1: add
  byte calibrate_LR;
  byte calibrate_UD;
};

serial_packet packet;

void setup() 
{ 
  currentUD = 70;
  currentLR = 90;
  Serial.begin(115200);
  LRmove.attach(9);
  UDmove.attach(10);
  LRmove.write(currentLR);
  UDmove.write(currentUD);
}

void loop() {
  while(!Serial.available());
  if(Serial.available() > 0){
    Serial.readBytes((uint8_t*)&packet, sizeof(packet));
    if(packet.LR){
      if(currentLR + packet.calibrate_LR <= 180){
        currentLR = currentLR + packet.calibrate_LR;
      } else{
        currentLR = 180;
      }
    } else{
      if(currentLR - packet.calibrate_LR >= 0){
        currentLR = currentLR - packet.calibrate_LR;
      } else{
        currentLR = 0;
      }
    }
    if(packet.UD){
      if(currentUD + packet.calibrate_UD <= 180){
        currentUD = currentUD + packet.calibrate_UD;
      } else{
        currentUD = 180;
      }
    } else{
      if(currentUD - packet.calibrate_UD >= 0){
        currentUD = currentUD - packet.calibrate_UD;
      } else{
        currentUD = 0;
      }
    }
  }
  UDmove.write(currentUD);
  LRmove.write(currentLR);
}
