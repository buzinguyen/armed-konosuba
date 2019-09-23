bool toggle;

void setup(){
  pinMode(10, OUTPUT);
  Serial.begin(115200);
  pulse10();
}
//256 - 1 0 0
//1024 - 1 0 1
//64 - 0 1 1

void pulse10(){
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 3124;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12);  
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

void pulse15(){
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 520;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

void pulse20(){
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 6249;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS11) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

void pulse22(){
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 354;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

void pulse25(){
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 1249;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS12);  
  TIMSK1 |= (1 << OCIE1A);
  sei();
}

ISR(TIMER1_COMPA_vect){
  digitalWrite(10, toggle);
  toggle = !toggle;
}

void loop(){
  while(!Serial.available());
  if(Serial.available()){
    int incoming = Serial.read() - '0';
    switch(incoming){
      case 0:
        pulse10();
        break;
      case 1:
        pulse15();
        break;
      case 2:
        pulse20();
        break;
      case 3:
        pulse25();
        break;
      default:
        break;
    }
  }
  
}

