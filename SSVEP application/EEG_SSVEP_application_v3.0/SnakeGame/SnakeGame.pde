import processing.net.*;
Client client;

int grid = 20; //How big each grid square will be
PVector food;
int speed = 100;
boolean dead = true;
int highscore = 0;
Snake snake;
Blinking_led led_10Hz = new Blinking_led(375, 10, 300, 110, 450, 110, 10); //top
Blinking_led led_15Hz = new Blinking_led(10, 375, 110, 300, 110, 450, 15); //left
Blinking_led led_20Hz = new Blinking_led(740, 375, 640, 300, 640, 450, 20); //right
Blinking_led led_25Hz = new Blinking_led(375, 740, 300, 640, 450, 640, 25); //bottom
public int width_canvas = 500;
public int height_canvas = 500;
public int offset_x = 125;
public int offset_y = 125;

void setup() {
  size(750, 750);
  snake = new Snake();
  food = new PVector();
  newFood();
  frameRate(480);
  client = new Client(this, "localhost", 50007);
}

void draw() {
  background(0);
  fill(255);
  if (!dead) {
    if (frameCount % speed == 0) {
      snake.update();
    }
    snake.show();
    snake.eat();
    fill(255, 0, 0);
    rect(food.x + offset_x, food.y + offset_y, grid, grid);
    textAlign(LEFT);
    textSize(15);
    fill(255);
    text("Score: " + snake.len, 10 + offset_x, 20 + offset_y);
  } else {
    textSize(25);
    textAlign(CENTER, CENTER);
    text("Snake Game\nClick to start" + "\nHighscore: " + highscore, (width_canvas/2) + offset_x, (height_canvas/2) + offset_y);
  }
  
  led_10Hz.update();
  led_15Hz.update();
  led_20Hz.update();
  led_25Hz.update();
  stroke(255);
  line(offset_x, offset_y, offset_x + width_canvas, offset_y);
  line(offset_x, offset_y + height_canvas, offset_x + width_canvas, offset_y + height_canvas);
  line(offset_x, offset_y, offset_x, offset_y + height_canvas);
  line(offset_x + width_canvas, offset_y, offset_x + width_canvas, offset_y + height_canvas);
  if (client.available() > 0) { 
    int dataIn = client.read();
    if (dataIn == 52 && snake.moveX != 1) {
      snake.vel.x = -1;
      snake.vel.y = 0;
    } else if (dataIn == 54 && snake.moveX != -1) {
      snake.vel.x = 1;
      snake.vel.y = 0;
    } else if (dataIn == 56 && snake.moveY != 1) {
      snake.vel.y = -1;
      snake.vel.x = 0;
    } else if (dataIn == 50 && snake.moveY != -1) {
      snake.vel.y = 1;
      snake.vel.x = 0;
    }
  } 
}

void newFood() {
  food.x = floor(random(width_canvas));
  food.y = floor(random(height_canvas));
  food.x = floor(food.x/grid) * grid;
  food.y = floor(food.y/grid) * grid;
}

void mousePressed() {
  if (dead) {
    snake = new Snake();
    newFood();
    speed = 100;
    dead = false;
  }
}
