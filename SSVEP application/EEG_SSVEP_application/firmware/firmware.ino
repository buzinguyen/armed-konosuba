#include <stdlib.h>
#include <stdio.h>

bool toggle;
int count;

struct packetStructure{
  uint8_t count;
  uint8_t data[1500];
};
volatile packetStructure packet;
int len_struct = sizeof(packet);

void sendPacket(){
  Serial.write('S');
  Serial.write((uint8_t*)&packet, len_struct);
  Serial.write('E');
  return;
}

void sendBytes(int value){
  byte buf[2];
  buf[1] = value & 255;
  buf[0] = (value >> 8) & 255;
  Serial.write(buf, sizeof(buf));
}

void setup() {
  // put your setup code here, to run once:
  pinMode(10, OUTPUT);
  pinMode(A1, INPUT);
  Serial.begin(115200);
  count = 0;
  
  cli();
  
  // 256 Hz
  TCCR0A = 0;
  TCCR0B = 0;
  TCNT0  = 0;
  OCR0A = 60;
  TCCR0A |= (1 << WGM01);
  TCCR0B |= (1 << CS02) | (1 << CS00);
  TIMSK0 |= (1 << OCIE0A);
   
  //14 Hz square wave
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 557;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A); 
    
  /* 
  20 Hz square wave
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 6249;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS11) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A); 
  */

  /*
  10 Hz square wave
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 3124;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12);  
  TIMSK1 |= (1 << OCIE1A); 
  */

  /* 2 Hz square wave
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 15624;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12);  
  TIMSK1 |= (1 << OCIE1A); 
  */
  
  sei();

  packet.count = 0;
}

ISR(TIMER0_COMPA_vect){
  // read analog at 256 Hz and send packet immediately
  packet.data[count] = byte(analogRead(1) * 0.25);
  if(count == 1499){
    packet.count = packet.count + 1;
    Serial.write('S');
    Serial.write((uint8_t*)&packet, sizeof(packet));
    Serial.write('E');
    count = 0;
  } else{
    count++;
  }
}

ISR(TIMER1_COMPA_vect){
  digitalWrite(10, toggle);
  toggle = !toggle;
}

void loop() {
  // put your main code here, to run repeatedly:
}
