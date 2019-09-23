import java.io.File;
import processing.net.*;
Client client;

color black  = color(0, 0, 0);
color white  = color(255, 255, 255);
color blue   = color(0, 0, 255);
color yellow = color(255, 255, 0);

String mazeFileName = "sample.maze";

int xblocks;
int yblocks;

int xExit;
int yExit;
int xStart;
int yStart;

int blockSize = 40;

int mapWidth;
int mapHeight;

boolean gameOver = false;

public class Position {
  int   x,  y;
  float xR, yR;
  boolean isBarrier;
  Position north, east, south, west;

  public Position( int X, int Y, boolean IsBarrier ) {
    x  = x;
    y  = Y;
    xR = X*blockSize;
    yR = Y*blockSize;
    isBarrier = IsBarrier;
    north     = null;
    east      = null; 
    south     = null;
    west      = null;
  }

  void draw() {
    noStroke();
    if ( isBarrier ) {
      fill(black);
    } else {
      fill(white);
    }

    rect(xR, yR, blockSize, blockSize);
  }
}; 

public class Player {
  int x, y;
  Position pos;
  public Player( int X, int Y ) {
    x = X;
    y = Y; 
    pos = maze[y][x];
  } 
  
  void north() {
    if(pos.north != null && !pos.north.isBarrier) {
      pos = pos.north;
      y--;    
    }  
  }
  void east() {
    if(pos.east != null && !pos.east.isBarrier) {
      pos=pos.east;
      x++;
    }
  }
  void south() {
    if(pos.south != null && !pos.south.isBarrier) {
      pos=pos.south;
      y++;
    } 
  }
  void west() {
    if(pos.west != null && !pos.west.isBarrier) {
      pos=pos.west;
      x--;
    }
  }
  
  void draw() {
    stroke(1.0);
    strokeWeight(1.0);
    fill(white);
    ellipse((0.5+x)*blockSize, (0.5+y)*blockSize, blockSize, blockSize);
    fill(black);
    ellipse((x+0.3)*blockSize, (y+0.35)*blockSize, 0.15*blockSize, 0.15*blockSize);
    ellipse((x+0.7)*blockSize, (y+0.35)*blockSize, 0.15*blockSize, 0.15*blockSize);
    noFill();
    strokeWeight(3.0);
    arc((x+0.5)*blockSize, (y+0.4)*blockSize, 0.8*blockSize, 0.8*blockSize, 0.5, PI-0.5);
    if(x==xExit && y==yExit) {
      gameOver=true;
    }    
  }
}


Position[][] maze;
Player player;

// How we move around in the maze
void keyPressed() {
  if (key == CODED)
  {
    switch(keyCode) {
    case LEFT:
      player.west(); 
      break;
    case UP:
      player.north();
      break;
    case RIGHT:
      player.east();
      break;
    case DOWN:
      player.south();
      break;
    }
  }
}


void setup() {
  surface.setResizable(true);

  // Load the maze text file
  String[] text = loadStrings(mazeFileName);

  xblocks = text[0].length();
  yblocks = text.length;

  mapWidth  = xblocks*blockSize;
  mapHeight = yblocks*blockSize;

  maze = new Position[yblocks][];

  // Determine maze size and locations of start and exit
  for ( int row=0; row<yblocks; ++row ) {

    maze[row] = new Position[xblocks];

    for (int col=0; col<xblocks; ++col) {    

      char c = text[row].charAt(col);
      
      boolean isBarrier = c == 'X';      
      boolean isExit    = c == 'E';
      boolean isStart   = c == 'O';
      
      maze[row][col] = new Position(col, row, isBarrier); 

      if(isExit) {
        xExit = col;
        yExit = row;
      }
      if(isStart) {
        xStart = col;
        yStart = row;
      }       
    }
  }   

  // Do connectivity
  
  for( int row=1; row<yblocks-1; ++row ) {
    for( int col=1; col<xblocks-1; ++col ) {
      maze[row][col].north = maze[row-1][col]; 
      maze[row][col].east  = maze[row][col+1];
      maze[row][col].south = maze[row+1][col];
      maze[row][col].west  = maze[row][col-1]; 
    }    
  }

  player = new Player(xStart,yStart);
 
  int X = player.pos.x;
  int Y = player.pos.y;
  //System.out.println("Start is at (" + xStart + "," + yStart +")");  
  //System.out.println("Exit is at (" + xExit + "," + yExit +")");
  
  surface.setSize(mapWidth, mapHeight);
  client = new Client(this, "localhost", 50007);
}


void draw() {
  if (!gameOver) {
    background(white);
    for ( int row=0; row<yblocks; ++row ) {
      for ( int col=0; col<xblocks; ++col ) {
        maze[row][col].draw();
      }
    }  
    player.draw();
  } else {
    background(black);
    textSize(2*blockSize);
    fill(white);
    textAlign(CENTER);
    text("Training Completed", 0.5*mapWidth, 0.5*mapHeight);
  }
  
  if (client.available() > 0) { 
    int dataIn = client.read();
    if (dataIn == 52) {
      player.west();
    } else if (dataIn == 54) {
      player.east();
    } else if (dataIn == 56) {
      player.north();
    } else if (dataIn == 50) {
      player.south();
    }
  }
}
