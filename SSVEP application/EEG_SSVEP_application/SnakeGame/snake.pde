class Snake {
  PVector pos;
  PVector vel;
  ArrayList<PVector> hist;
  int len;
  int moveX = 0;
  int moveY = 0;

  Snake() {
    pos = new PVector(100, 100);
    vel = new PVector();
    hist = new ArrayList<PVector>();
    len = 0;
  }

  void update() {
    hist.add(pos.copy());
    pos.x += vel.x*grid;
    pos.y += vel.y*grid;
    moveX = int(vel.x);
    moveY = int(vel.y);

    pos.x = (pos.x + width_canvas) % width_canvas;
    pos.y = (pos.y + height_canvas) % height_canvas;

    if (hist.size() > len) {
      hist.remove(0);
    }

    for (PVector p : hist) {
      if (p.x == pos.x && p.y == pos.y) {
        dead = true;
        if (len > highscore) highscore = len;
      }
    }
  }

  void eat() {
    if (pos.x == food.x && pos.y == food.y) {
      len++;
      if (speed > 50) speed--;
      newFood();
    }
  }

  void show() {
    noStroke();
    fill(125);
    rect(pos.x + offset_x, pos.y + offset_y, grid, grid);
    for (PVector p : hist) {
      rect(p.x + offset_x, p.y + offset_y, grid, grid);
    }
  }
}

void keyPressed() {
  if (keyCode == LEFT && snake.moveX != 1) {
    snake.vel.x = -1;
    snake.vel.y = 0;
  } else if (keyCode == RIGHT && snake.moveX != -1) {
    snake.vel.x = 1;
    snake.vel.y = 0;
  } else if (keyCode == UP && snake.moveY != 1) {
    snake.vel.y = -1;
    snake.vel.x = 0;
  } else if (keyCode == DOWN && snake.moveY != -1) {
    snake.vel.y = 1;
    snake.vel.x = 0;
  }
}
