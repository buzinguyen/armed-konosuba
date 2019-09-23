class blinking_led{
  private int frequency;
  private int time = millis();
  private int current_mode = 1;
  private int counter;
  private int a, b, c, d;
  
  blinking_led(int a, int b, int c, int d, int frequency){
    this.frequency = frequency;
    this.counter = int(500.0/float(frequency));
    this.a = a;
    this.b = b;
    this.c = c;
    this.d = d;
  }
  
  void update(){
    int passedMillis = millis() - time; // calculates passed milliseconds
    if(passedMillis >= counter){
        time = millis();
        if(current_mode == 1) current_mode = 0;
        else current_mode = 1;
    }
    if(current_mode == 1) fill(255);
    else fill(0);
    ellipse(a, b, c, d);
  }
}

blinking_led led_10Hz = new blinking_led(50, 50, 100, 100, 10); //top left
blinking_led led_15Hz = new blinking_led(50, 450, 100, 100, 15);//bottom left
blinking_led led_20Hz = new blinking_led(450, 50, 100, 100, 20);//top right
blinking_led led_25Hz = new blinking_led(450, 450, 100, 100, 25);//bottom right

void setup() {
  size(500, 500);
  background(102);
  noStroke();
  frameRate(480);
}
 
void draw() {
  background(100); 
  led_10Hz.update();
  led_15Hz.update();
  led_20Hz.update();
  led_25Hz.update();
}
