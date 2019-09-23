#include <SPI.h>                                      //SPI library
#include <Wire.h>                                     //I2C library for OLED
#include <Adafruit_GFX.h>                             //graphics library for OLED
#include <Adafruit_SSD1306.h>                         //OLED driver

#define OLED_RESET 7                                  //OLED reset, not hooked up but required by library
Adafruit_SSD1306 display(OLED_RESET);                 //declare instance of OLED library called display

#define left 5
#define right 4
#define enter 6
#define up 2
#define down 3

const int greek_figure[5] = {120, 20, 40, 60, 80};
const int home_figure[5] = {120, 0, 0, 0, 0};
const int bottle_figure[5] = {45, 80, 80, 80, 80};
const int bag_figure[5] = {45, 60, 60, 60, 60};
const int point_figure[5] = {45, 0, 80, 80, 80};
const int pen_figure[5] = {80, 60, 60, 80, 80};

typedef struct single_menu{
  char* option[10];
  byte len;
};

typedef struct single_packet{
  unsigned int mode;
  byte data[5];
};

boolean debounce, select;
byte menu_pointer, previous_menu_pointer;

single_menu main_menu = {"Hand Calibration", "Hand Figure", "EEG Calibration","Wrist Calibration", "W-E Rotation", "About", "--", "--", "--", "--", 10};
single_menu hand_menu = {" << back", "Thumb", "Index", "Middle", "Ring", "Pinky", "", "", "", "", 6};
single_menu hand_figure = {" << back", "Home All Fingers", "Greek figure", "Hold bottle", "Hold bag", "Point finger", "Hold pen", "", "", "", 7};
char* finger_list[] = {"Thumb", "Index", "Middle", "Ring", "Pinky"};

byte buttonState, lastButtonState;
byte menu_index = 0;

byte calibrate_step = 1;
boolean begin_SSVEP, toggle;

void setup(){
  Serial.begin(115200);
  pinMode(left, INPUT);
  pinMode(right, INPUT);
  pinMode(up, INPUT);
  pinMode(down, INPUT);
  pinMode(enter, INPUT);
  pinMode(13, OUTPUT);
  
  display.begin(SSD1306_SWITCHCAPVCC,0x3C);           //begin OLED @ hex addy 0x3C
  display.setTextSize(2);                             //set OLED text size to 1 (1-6)
  display.setTextColor(WHITE);                        //set text color to white
  analogReference(DEFAULT);                           // Use default (5v) aref voltage.
  
  debounce = true;
  select = false;
  
  display.clearDisplay();
  display.setCursor(10, 20);
  display.print("CTRL MENU");
  display.setCursor(0, 40);
  display.setTextSize(1);
  display.print("Sys. Function Tester");
  display.display();
  delay(2000);
  
  menu_pointer = 0;
  print_menu(main_menu, 0);
  display.drawRect(0, 0, 120, 11, WHITE);
  display.display();

  buttonState = 0;
  lastButtonState = 0;

  previous_menu_pointer = 0;
  begin_SSVEP = false;
}

ISR(TIMER1_COMPA_vect){
  if(begin_SSVEP){
    digitalWrite(13, toggle);
    toggle = !toggle;
  }
}

void loop(){
  if(menu_index == 0){
    button_panel(main_menu);
    if(select){
      previous_menu_pointer = menu_pointer;
      switch(menu_pointer){
        case 0:
          menu_pointer = 0;
          print_menu(hand_menu, 0);
          display.drawRect(0, 0, 120, 11, WHITE);
          display.display();
          menu_index = 1;
          break;
        case 1:
          menu_pointer = 0;
          print_menu(hand_figure, 0);
          display.drawRect(0, 0, 120, 11, WHITE);
          display.display();
          menu_index = 1;       
          break;
        case 2:
          menu_pointer = 0;
          menu_index = 1;
          break;
        case 3:
          menu_pointer = 0;
          menu_index = 1;
          break;
        case 4:
          menu_pointer = 0;
          menu_index = 1;
          break;
        case 5:
          display.clearDisplay();
          display.setCursor(10, 20);
          display.setTextSize(2);
          display.print("CTRL MENU");
          display.setCursor(0, 40);
          display.setTextSize(1);
          display.print("Sys. Function Tester");
          display.display();
          delay(5000);
          menu_pointer = 0;
          print_menu(main_menu, 0);
          display.drawRect(0, 0, 120, 11, WHITE);
          display.display();
          break;
      default:
          break;
      }
      select = false;
    } 
  }else if(menu_index == 1){
    switch(previous_menu_pointer){
      case 0:
        button_panel(hand_menu);
        break;
      case 1:
        button_panel(hand_figure);
        break;
      case 2:
        begin_SSVEP = true;
        ssvep_controller();
        break;
      case 3:
        wrist_calibration_module();
        break;
      case 4:
        transhumeral_rotation_module();
        break;
      default:
        break;
    }
    if(select){
      previous_menu_pointer = (10 * menu_pointer) + previous_menu_pointer;
      switch(previous_menu_pointer){
        //preivous_menu_pointer works as followed:
        //    {newest}{previous}{previous}{..}{first choice}
        //Example: 124 <- 3 layers, first choice = 4, second = 2 then latest 1
        case 00:
          return_main();
          break;   
        case 10:
          menu_pointer = 0;
          menu_index = 2;
          break;   
        case 20:
          menu_pointer = 0;
          menu_index = 2;
          break;
        case 30:
          menu_pointer = 0;
          menu_index = 2;
          break;
        case 40:
          menu_pointer = 0;
          menu_index = 2;
          break;
        case 50:
          menu_pointer = 0;
          menu_index = 2;
          break;
        case 01:
          return_main();
          break;
        case 11:
          send_hand_figure(menu_pointer-1);
          return_main();
          break;
        case 21:
          send_hand_figure(menu_pointer-1);
          return_main();
          break;
        case 31:
          send_hand_figure(menu_pointer-1);
          return_main();
          break;
        case 41:
          send_hand_figure(menu_pointer-1);
          return_main();
          break;
        case 51:
          send_hand_figure(menu_pointer-1);
          return_main();
          break;
        case 61:
          send_hand_figure(menu_pointer-1);
          return_main();
        case 02:
          begin_SSVEP = false;
          digitalWrite(13, LOW);
          return_main();
          break;
        case 03:
          return_main();
          break;
        case 04:
          return_main();
          break;
        default:
          break;
      }
      select = false;
    }
  } else if(menu_index == 2){
    byte current_level_pointer = (previous_menu_pointer * 0.1) - 1;
    switch(current_level_pointer){
      case 0:
        finger_calibrate_module(current_level_pointer);
        break;  
      case 1:
        finger_calibrate_module(current_level_pointer);
        break;
      case 2:
        finger_calibrate_module(current_level_pointer);
        break;
      case 3:
        finger_calibrate_module(current_level_pointer);
        break;
      case 4:
        finger_calibrate_module(current_level_pointer);
        break;
      default:
        break;
    }
    if(select){
      switch(current_level_pointer){
        case 0:
          return_main();
          break;
        case 1:
          return_main();
          break;
        case 2:
          return_main();
          break;
        case 3:
          return_main();
          break;
        case 4:
          return_main();
          break;
        default:
          break; 
      }
      select = false;
    }
  }
  delay(10);
}

void button_panel(single_menu m){
  buttonState = 0;
  for(int i = 2; i < 6; i++){
    buttonState |= (digitalRead(i) << (i - 2));
  }
  if(buttonState != lastButtonState){
    if(buttonState != 0){
      byte new_pointer = 0;
      switch(buttonState){
        case (1 << (up - 2)):
          if(menu_pointer > 0) new_pointer = menu_pointer - 1;
          else new_pointer = 0;
          break;
        case (1 << (down - 2)):
          if(menu_pointer < (m.len - 1)) new_pointer = menu_pointer + 1;
          else new_pointer = (m.len - 1);
          break;
        case (1 << (right - 2)):
          break;
        case (1 << (left - 2)):
          break;
        default:
          break;
      }
      if(new_pointer < 5){
        display.drawRect(0, menu_pointer*10, 120, 11, BLACK);
        display.drawRect(0, new_pointer*10, 120, 11, WHITE);
        write_scroll(new_pointer, m.len);
        display.display();
      } else{
        print_menu(m, new_pointer - 5);
        write_scroll(new_pointer, m.len);
        display.drawRect(0, 5*10, 120, 11, WHITE);
        display.display();
      }
      menu_pointer = new_pointer;
    }
  }
  lastButtonState = buttonState;
  
  if(digitalRead(enter) && debounce){
    debounce = false;
    select = true;
  }
  if(digitalRead(enter)){
    debounce = false;
  } else{
    debounce = true;
  }
}

void print_menu(single_menu m, byte pointer){
  display.clearDisplay();
  display.drawRect(122, 0, 5, 63, WHITE);
  display.setTextSize(1);
  if(m.len <= 6){
    for(int i = 0; i < m.len; i++){
      display.setCursor(2, i*10 + 2);
      display.print(m.option[i]);
    }
  } else{
    for(int i = 0; i < 6; i++){
      display.setCursor(2, i*10 + 2);
      display.print(m.option[i+pointer]);
    }
  }
  write_scroll(menu_pointer, m.len);
  display.display();
}

void write_scroll(byte current_pos, byte max_pos){
  // 60 pixels to write and max options per menu is 10, so each is 6
  display.fillRect(123, 1, 3, 61, BLACK);
  if(max_pos > 6){
    byte length = (10 - max_pos)*6 + 36;
    if(current_pos > 5){
      display.fillRect(123, 1 + (current_pos - 5)*6, 3, length + 1, WHITE); 
    } else{
      display.fillRect(123, 1, 3, length + 1, WHITE);
    } 
  } else{
    display.fillRect(123, 1, 3, 61, WHITE);
  }
}

void finger_calibrate_module(byte finger_index){
  /*
   * Use after the sequence "Hand Calibration" -> <a finger> -> this module
   * The input finger index is 0 - thumb, 1 - index, 2 - middle, 3 - ring, 4 - pinky
   * The changes made here will be written to Serial and send to the hand module for finger calibration
   */
   
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Calibrate");
  display.setCursor(60, 0);
  display.print(finger_list[finger_index]);
  display.drawTriangle(56, 32, 70, 32, 63, 21, WHITE);
  display.drawTriangle(56, 34, 70, 34, 63, 45, WHITE);
  display.setCursor(75, 25);
  display.print("open");
  display.setCursor(75, 35);
  display.print("close");
  display.setCursor(2, 52);
  display.print("back");
  display.drawRect(0, 50, 25, 11, WHITE);

  display.drawTriangle(55, 52, 55, 62, 47, 57, WHITE);
  display.drawTriangle(75, 52, 75, 62, 83, 57, WHITE);
  if(calibrate_step > 9){
    display.setCursor(60, 52);
  } else{
    display.setCursor(62, 52); 
  }
  display.print(calibrate_step);
  
  display.display();
  
  buttonState = 0;
  for(int i = 2; i < 6; i++){
    buttonState |= (digitalRead(i) << (i - 2));
  }
  if(buttonState != lastButtonState){
    if(buttonState != 0){
      single_packet packet = {1, 0, 0, 0, 0, 0};
      switch(buttonState){
        case (1 << (up - 2)):
          display.fillTriangle(56, 32, 70, 32, 63, 21, WHITE);
          packet.data[finger_index] = calibrate_step;
          packet.mode = 1;
          break;
        case (1 << (down - 2)):
          display.fillTriangle(56, 34, 70, 34, 63, 45, WHITE);
          packet.data[finger_index] = calibrate_step;
          packet.mode = 2;
          break;
        case (1 << (right - 2)):
          display.fillTriangle(75, 52, 75, 62, 83, 57, WHITE);
          calibrate_step++;
          break;
        case (1 << (left - 2)):
          display.fillTriangle(55, 52, 55, 62, 47, 57, WHITE);
          if(calibrate_step > 0) calibrate_step--;
          break;
        default:
          break;
      }
      display.display();
      Serial.write((uint8_t*)&packet, sizeof(packet));
    }
  }
  lastButtonState = buttonState;
  
  if(digitalRead(enter) && debounce){
    debounce = false;
    select = true;
  }
  if(digitalRead(enter)){
    debounce = false;
  } else{
    debounce = true;
  }
}

void wrist_calibration_module(){
  /*   
   *    direction index: 1: up/down 2: left/right
   */
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Calibrate Wrist");
  display.setCursor(60, 0);
  display.drawTriangle(56, 32, 70, 32, 63, 21, WHITE);
  display.drawTriangle(56, 34, 70, 34, 63, 45, WHITE);
  display.setCursor(75, 25);
  display.print("up");
  display.setCursor(75, 35);
  display.print("down");
  display.setCursor(2, 52);
  display.print("back");
  display.drawRect(0, 50, 25, 11, WHITE);

  display.drawTriangle(48, 52, 48, 62, 40, 57, WHITE);
  display.drawTriangle(77, 52, 77, 62, 85, 57, WHITE);
  display.setCursor(52, 52);
  display.print("curl");
  
  display.display();
  
  buttonState = 0;
  for(int i = 2; i < 6; i++){
    buttonState |= (digitalRead(i) << (i - 2));
  }
  if(buttonState != lastButtonState){
    if(buttonState != 0){
      single_packet packet = {4, 0, 0, 0, 0, 0};
      switch(buttonState){
        case (1 << (up - 2)):
          display.fillTriangle(56, 32, 70, 32, 63, 21, WHITE);
          packet.data[0] = 1;
          packet.data[1] = 1;
          break;
        case (1 << (down - 2)):
          display.fillTriangle(56, 34, 70, 34, 63, 45, WHITE);
          packet.data[0] = 2;
          packet.data[1] = 2;
          break;
        case (1 << (right - 2)):
          display.fillTriangle(77, 52, 77, 62, 85, 57, WHITE);
          packet.data[0] = 1;
          packet.data[1] = 2;
          break;
        case (1 << (left - 2)):
          display.fillTriangle(48, 52, 48, 62, 40, 57, WHITE);
          packet.data[0] = 2;
          packet.data[1] = 1;
          break;
        default:
          break;
      }
      display.display();
      Serial.write((uint8_t*)&packet, sizeof(packet));
    }
  }
  lastButtonState = buttonState;
  
  if(digitalRead(enter) && debounce){
    debounce = false;
    select = true;
  }
  if(digitalRead(enter)){
    debounce = false;
  } else{
    debounce = true;
  }
}

void transhumeral_rotation_module(){
  /*   
   *    direction index: 1: left 2: right
   */
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Calibrate W-E Rtn");
  display.setCursor(2, 52);
  display.print("back");
  display.drawRect(0, 50, 25, 11, WHITE);

  display.drawTriangle(48, 32, 48, 42, 40, 37, WHITE);
  display.drawTriangle(77, 32, 77, 42, 85, 37, WHITE);
  display.setCursor(52, 32);
  display.print("curl");
  
  display.display();
  
  buttonState = 0;
  for(int i = 2; i < 6; i++){
    buttonState |= (digitalRead(i) << (i - 2));
  }
  if(buttonState != lastButtonState){
    if(buttonState != 0){
      single_packet packet = {4, 0, 0, 0, 0, 0};
      switch(buttonState){
        case (1 << (right - 2)):
          display.fillTriangle(77, 32, 77, 42, 85, 37, WHITE);
          packet.data[0] = 0;
          packet.data[1] = 0;
          packet.data[2] = 2;
          break;
        case (1 << (left - 2)):
          display.fillTriangle(48, 32, 48, 42, 40, 37, WHITE);
          packet.data[0] = 0;
          packet.data[1] = 0;
          packet.data[2] = 1;
          break;
        default:
          break;
      }
      display.display();
      Serial.write((uint8_t*)&packet, sizeof(packet));
    }
  }
  lastButtonState = buttonState;
  
  if(digitalRead(enter) && debounce){
    debounce = false;
    select = true;
  }
  if(digitalRead(enter)){
    debounce = false;
  } else{
    debounce = true;
  }
}

void send_hand_figure(byte figure_index){
  single_packet packet = {0, 0, 0, 0, 0, 0};
  switch(figure_index){
    case 0:
      for(int i = 0; i < 5; i++){
        packet.data[i] = home_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    case 1:
      for(int i = 0; i < 5; i++){
        packet.data[i] = greek_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    case 2:
      for(int i = 0; i < 5; i++){
        packet.data[i] = bottle_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    case 3:
      for(int i = 0; i < 5; i++){
        packet.data[i] = bag_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    case 4:
      for(int i = 0; i < 5; i++){
        packet.data[i] = point_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    case 5:
      for(int i = 0; i < 5; i++){
        packet.data[i] = pen_figure[i]; 
      }
      Serial.write((uint8_t*)&packet, sizeof(packet));
      break;
    default:
      break;
  }
}

void ssvep_controller(){
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("Calibrate SSVEP LED");
  display.drawTriangle(56, 32, 70, 32, 63, 21, WHITE); //up
  display.drawTriangle(56, 52, 70, 52, 63, 63, WHITE); //down
  display.drawTriangle(48, 37, 48, 47, 40, 42, WHITE); //left
  display.drawTriangle(77, 37, 77, 47, 85, 42, WHITE); //right
  display.setCursor(75, 22);
  display.print("10");
  display.setCursor(75, 56);
  display.print("25");
  display.setCursor(25, 39);
  display.print("15");
  display.setCursor(90, 39);
  display.print("20");
  display.setCursor(2, 52);
  display.print("back");
  display.drawRect(0, 50, 25, 11, WHITE);

  display.display();
  
  buttonState = 0;
  for(int i = 2; i < 6; i++){
    buttonState |= (digitalRead(i) << (i - 2));
  }
  if(buttonState != lastButtonState){
    if(buttonState != 0){
      cli();
      TCCR1A = 0;
      TCCR1B = 0;
      TCNT1  = 0;
      switch(buttonState){
        case (1 << (up - 2)):
          display.fillTriangle(56, 32, 70, 32, 63, 21, WHITE); //up
          OCR1A = 3124;
          TCCR1B |= (1 << WGM12);
          TCCR1B |= (1 << CS12);
          break;
        case (1 << (down - 2)):
          display.fillTriangle(56, 52, 70, 52, 63, 63, WHITE); //down
          cli();
          OCR1A = 1249;
          TCCR1B |= (1 << WGM12);
          TCCR1B |= (1 << CS12);
          break;
        case (1 << (right - 2)):
          display.fillTriangle(77, 37, 77, 47, 85, 42, WHITE); //right
          cli();
          OCR1A = 6249;
          TCCR1B |= (1 << WGM12);
          TCCR1B |= (1 << CS11) | (1 << CS10);
          break;
        case (1 << (left - 2)):
          display.fillTriangle(48, 37, 48, 47, 40, 42, WHITE); //left
          cli();
          OCR1A = 520;
          TCCR1B |= (1 << WGM12);
          TCCR1B |= (1 << CS12) | (1 << CS10);
          break;
        default:
          break;
      }
      TIMSK1 |= (1 << OCIE1A);
      sei();
      display.display();
    }
  }
  lastButtonState = buttonState;
  
  if(digitalRead(enter) && debounce){
    debounce = false;
    select = true;
  }
  if(digitalRead(enter)){
    debounce = false;
  } else{
    debounce = true;
  }
}

void return_main(){
  menu_pointer = 0;
  menu_index = 0;
  print_menu(main_menu, 0);
  display.drawRect(0, 0, 120, 11, WHITE);
  display.display();
}

