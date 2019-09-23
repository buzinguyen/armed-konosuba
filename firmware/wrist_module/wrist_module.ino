/* 
 * serial packet design for entire arm: 
 *  - Share the same format of{unsigned int, byte, byte, byte, byte, byte}
 *  - Fisrt unsigned int is mode: 0 for hand figure, 1 and 2 for finger calibration, 3 for elbow, 4 for wrist
 *  - Next 5 bytes, depends on the mode, controlling data of at most 5 motors
 */
volatile int key;

/*
 * For wrist, mode should be 4
 * data byte correspondence:
 *  - 0 nothing
 *  - 1 up
 *  - 2 down
 *  Sample data packet for hand to curl left: {4, 2, 1, 0, 0, 0}
 *  Add in rotor for transhumeral rotation
 *  - 0 nothing
 *  - 1 rotate left
 *  - 2 rotate right
 *  Add in thumb, mode 5 and byte 4 of packet
 *  - 0 nothing
 *  - 1 out
 *  - 2 in
 */
typedef struct wrist_packet{
  unsigned int mode;
  byte left_motor;
  byte right_motor;
  byte rotor;
  byte thumb;
  byte blank_value;
};
wrist_packet packet;

void setup() {
  // put your setup code here, to run once:
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  Serial.begin(115200);
  for(int i = 0; i < 3; i++){
    digitalWrite(13, HIGH);
    delay(50);
    digitalWrite(13, LOW);
    delay(50);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  while(!Serial.available());
  if(Serial.available() > 0){
    Serial.readBytes((uint8_t*)&packet, sizeof(packet));
  }
  if(packet.mode == 4){
    byte movement = packet.left_motor * 10 + packet.right_motor;
    switch(movement){
      case 11:
        hand_up();
        break;
      case 12:
        hand_right();
        break;
      case 21:
        hand_left();
        break;
      case 22:
        hand_down();
        break;
      default:
        break;
    }
    switch(packet.rotor){
      case 1:
        rotate_left();
        break;
      case 2:
        rotate_right();
        break;
      default:
        break;
    }
  }
  else if(packet.mode == 5){
    switch(packet.thumb){
      case 1:
        thumb_in();
        break;
      case 2:
        thumb_out();
        break;
      default:
        break;
    }
  }
}

void rotate_left(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 5){
    digitalWrite(9, HIGH);
    digitalWrite(8, HIGH); 
  }
  digitalWrite(9, LOW);
}

void rotate_right(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 5){
    digitalWrite(9, HIGH);
    digitalWrite(8, LOW); 
  }
  digitalWrite(9, LOW);
}

void thumb_out(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 50){
    digitalWrite(11, HIGH);
    digitalWrite(10, HIGH); 
  }
  digitalWrite(11, LOW);
}

void thumb_in(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 50){
    digitalWrite(11, HIGH);
    digitalWrite(10, LOW); 
  }
  digitalWrite(11, LOW);
}

void hand_left(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(6, LOW);
  }
  digitalWrite(7, LOW);
  digitalWrite(5, LOW);
}

void hand_right(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(4, LOW);
    digitalWrite(6, HIGH);
  }
  digitalWrite(7, LOW);
  digitalWrite(5, LOW);
}

void hand_up(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(4, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, HIGH);
  }
  digitalWrite(5, LOW);
  digitalWrite(7, LOW);
}

void hand_down(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
  }
  digitalWrite(5, LOW);
  digitalWrite(7, LOW);
}

void left_up(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(4, LOW);
  }
  digitalWrite(5, LOW);
}

void left_down(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(5, HIGH);
    digitalWrite(4, HIGH);
  }
  digitalWrite(5, LOW);
}

void right_up(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(6, LOW);
    digitalWrite(7, HIGH);
  }
  digitalWrite(7, LOW);
}

void right_down(){
  unsigned long currentTime = millis();
  while(millis() - currentTime <= 200){
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
  }
  digitalWrite(7, LOW);
}

