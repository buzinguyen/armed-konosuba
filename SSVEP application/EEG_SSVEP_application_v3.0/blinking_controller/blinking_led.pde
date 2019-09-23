class Blinking_led{
  private int frequency;
  private int time = millis();
  private int current_mode = 1;
  private int counter;
  private int a, b, c, d, e, f;
  
  Blinking_led(int a, int b, int c, int d, int e, int f, int frequency){
    this.frequency = frequency;
    this.counter = int(500.0/float(frequency));
    this.a = a;
    this.b = b;
    this.c = c;
    this.d = d;
    this.e = e;
    this.f = f;
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
    triangle(a, b, c, d, e, f);
  }
}
