Blinking_led led_10Hz = new Blinking_led(375, 10, 300, 110, 450, 110, 10); //top
Blinking_led led_15Hz = new Blinking_led(10, 375, 110, 300, 110, 450, 15); //left
Blinking_led led_20Hz = new Blinking_led(740, 375, 640, 300, 640, 450, 20); //right
Blinking_led led_25Hz = new Blinking_led(375, 740, 300, 640, 450, 640, 25); //bottom
public int width_canvas = 500;
public int height_canvas = 500;

void setup() {
  size(750, 750);
  frameRate(480);
}

void draw() {
  background(0);
  fill(255);
  
  led_10Hz.update();
  //led_15Hz.update();
  //led_20Hz.update();
  //led_25Hz.update();
  stroke(255);
}
