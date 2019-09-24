import processing.net.*;
Client client;
packet single_packet;
static final int NUMBER_OF_MODE = 6;
/*
7 modes of:
- change pivot
- change thumb
- change index
- change middle
- change ring
- change pinky then send packet
*/
public class packet{
  // The mode is as followed:
  // - mode = 0: set entire hand figure
  // - mode = 1: set individual finger: for homing and calibrating
  // When mode == 1, read for the data of a sensor and only do "open"
  // NOTICE: when sending packet from processing to python, this mode value is not important, only the Tkinter GUI on python set this mode
  private float thumb, index, middle, ring, pinky;
  private int mode;
  
  void init(){
    thumb = 0.0;
    index = 0.0;
    middle = 0.0;
    ring = 0.0;
    pinky = 0.0;
    mode = 0;
  }  
  void setThumb(float x){
    thumb = x;
  }
  void setIndex(float x){
    index = x;
  }
  void setMiddle(float x){
    middle = x;
  }
  void setRing(float x){
    ring = x;
  }
  void setPinky(float x){
    pinky = x;
  }
  void setMode(int i){
    mode = i;
  }
  String read(){
    return str(mode) + "," + str(thumb) + "," + str(index) + "," + str(middle) + "," + str(ring) + "," + str(pinky);
  }
}
PShape f11, f12, f13;
PShape f21, f22, f23;
PShape f31, f32, f33;
PShape f41, f42, f43;
PShape f51, f52, f53;
PShape palm, forearm;
float rotX, rotY;
float pivotX, pivotY;
float handCurl, wristCurl;
float thumbCurl, indexCurl, middleCurl, ringCurl, pinkyCurl;
float zoom;
int mode;

void setup(){
  size(1000, 800, P3D);
  f11 = loadShape("f11.obj");
  f12 = loadShape("f12.obj");
  f13 = loadShape("f13.obj");
  f21 = loadShape("f21.obj");
  f22 = loadShape("f22.obj");
  f23 = loadShape("f23.obj");
  f31 = loadShape("f31.obj");
  f32 = loadShape("f32.obj");
  f33 = loadShape("f33.obj");
  f41 = loadShape("f41.obj");
  f42 = loadShape("f42.obj");
  f43 = loadShape("f43.obj");
  f51 = loadShape("f51.obj");
  f52 = loadShape("f52.obj");
  f53 = loadShape("palm3_2.obj");
  palm = loadShape("palm3_1.obj");
  forearm = loadShape("forearm.obj");
  
  f11.disableStyle();
  f12.disableStyle();
  f13.disableStyle();
  f21.disableStyle();
  f22.disableStyle();
  f23.disableStyle();
  f31.disableStyle();
  f32.disableStyle();
  f33.disableStyle();
  f41.disableStyle();
  f42.disableStyle();
  f43.disableStyle();
  f51.disableStyle();
  f52.disableStyle();
  f53.disableStyle();
  palm.disableStyle();
  forearm.disableStyle();
  
  zoom = -2.0;
  mode = 0;
  client = new Client(this, "localhost", 50007);
  single_packet = new packet();
  single_packet.init();
  if(ping() == 4){
    println("Connection established!");
  }
  else{
    println("Unstable connection with host, check server..");
  }
}

void draw() {
  background(255);
  smooth();
  lights(); 
  directionalLight(51, 102, 126, -1, 0, 0);
  translate(width/2, height/2 + 150);
  rotateY(pivotY);
  rotateX(pivotX);
  scale(zoom);
  
  fill(#888888);
  translate(0, 0, -14.8);
  shape(forearm);
  
  fill(#FFFFFF);
  translate(0, 0, 14.8);
  rotateY(wristCurl);
  shape(palm);
  
  fill(#888888);
  translate(-27.31, 0, 78);//put all the origin of all the functions to the origin of pinky
  
  setMode(mode);
}

void setMode(int mode){
  switch(mode){
    case 0:
      //moving pivot
      middle(middleCurl*21/25, middleCurl*21/25, middleCurl*21/25);
      pinky(pinkyCurl*21/25, pinkyCurl*21/25, pinkyCurl*21/25);
      thumb(thumbCurl*15/25, -PI/4, thumbCurl*21/25);
      ring(ringCurl*21/25, ringCurl*21/25, ringCurl*21/25);
      index(indexCurl*21/25, indexCurl*21/25, indexCurl*21/25);
      break;
    case 1:
      //set thumb
      middle(middleCurl*21/25, middleCurl*21/25, middleCurl*21/25);
      pinky(pinkyCurl*21/25, pinkyCurl*21/25, pinkyCurl*21/25);
      thumb(handCurl*15/25, -PI/4, handCurl*21/25);
      ring(ringCurl*21/25, ringCurl*21/25, ringCurl*21/25);
      index(indexCurl*21/25, indexCurl*21/25, indexCurl*21/25);
      break;
    case 2:
      //set index
      middle(middleCurl*21/25, middleCurl*21/25, middleCurl*21/25);
      pinky(pinkyCurl*21/25, pinkyCurl*21/25, pinkyCurl*21/25);
      thumb(thumbCurl*15/25, -PI/4, thumbCurl*21/25);
      ring(ringCurl*21/25, ringCurl*21/25, ringCurl*21/25);
      index(handCurl*21/25, handCurl*21/25, handCurl*21/25);
      break;
    case 3:
      //set middle
      middle(handCurl*21/25, handCurl*21/25, handCurl*21/25);
      pinky(pinkyCurl*21/25, pinkyCurl*21/25, pinkyCurl*21/25);
      thumb(thumbCurl*15/25, -PI/4, thumbCurl*21/25);
      ring(ringCurl*21/25, ringCurl*21/25, ringCurl*21/25);
      index(indexCurl*21/25, indexCurl*21/25, indexCurl*21/25);
      break;
    case 4:
      //set ring
      middle(middleCurl*21/25, middleCurl*21/25, middleCurl*21/25);
      pinky(pinkyCurl*21/25, pinkyCurl*21/25, pinkyCurl*21/25);
      thumb(thumbCurl*15/25, -PI/4, thumbCurl*21/25);
      ring(handCurl*21/25, handCurl*21/25, handCurl*21/25);
      index(indexCurl*21/25, indexCurl*21/25, indexCurl*21/25);
      break;
    case 5:
      //set pinky
      middle(middleCurl*21/25, middleCurl*21/25, middleCurl*21/25);
      pinky(handCurl*21/25, handCurl*21/25, handCurl*21/25);
      thumb(thumbCurl*15/25, -PI/4, thumbCurl*21/25);
      ring(ringCurl*21/25, ringCurl*21/25, ringCurl*21/25);
      index(indexCurl*21/25, indexCurl*21/25, indexCurl*21/25);
      break;
  }
}

void thumb(float curlA, float curlB, float curlC)
{
  fill(#FFFFFF);
  translate(55.01, 0, -58);
  rotateZ(-curlA);
  shape(f53);  
  fill(#888888);
  translate(27.8, 0, 25.96);
  rotateY(-curlB);
  shape(f52);
  translate(0, 0, 28);
  rotateY(-curlC);
  shape(f51);
  rotateY(curlC);
  translate(0, 0, -28);
  rotateY(curlB);
  translate(-27.8, 0, -25.96);
  rotateZ(curlA);
  translate(-55.01, 0, 58);
}

void pinky(float curlA, float curlB, float curlC){
  translate(0, 0, 0);
  rotateX(curlA);
  shape(f13);
  translate(0, 0, 28);
  rotateX(curlB);
  shape(f12);
  translate(0, 0, 28);
  rotateX(curlC);
  shape(f11);  
  rotateX(-curlC);
  translate(0, 0, -28);
  rotateX(-curlB);
  translate(0, 0, -28);
  rotateX(-curlA);
}

void ring(float curlA, float curlB, float curlC){
  translate(20, 0, 0);
  rotateX(curlA);
  shape(f23);
  translate(0, 0, 38);
  rotateX(curlB);
  shape(f22);
  translate(0, 0, 38);
  rotateX(curlC);
  shape(f21);
  rotateX(-curlC);
  translate(0, 0, -38);
  rotateX(-curlB);
  translate(0, 0, -38);
  rotateX(-curlA);
  translate(-20, 0, 0);
}

void middle(float curlA, float curlB, float curlC){
  translate(40, 0, 0);
  rotateX(curlA);
  shape(f33);
  translate(0, 0, 48);
  rotateX(curlB);
  shape(f32);
  translate(0, 0, 38);
  rotateX(curlC);
  shape(f31);
  rotateX(-curlC);
  translate(0, 0, -38);
  rotateX(-curlB);
  translate(0, 0, -48);
  rotateX(-curlA);
  translate(-40, 0, 0);
}

void index(float curlA, float curlB, float curlC){
  translate(60, 0, 0);
  rotateX(curlA);
  shape(f43);
  translate(0, 0, 38);
  rotateX(curlB);
  shape(f42);
  translate(0, 0, 38);
  rotateX(curlC);
  shape(f41);
  rotateX(-curlC);
  translate(0, 0, -38);
  rotateX(-curlB);
  translate(0, 0, -38);
  rotateX(-curlA);
  translate(-60, 0, 0);
}

void mouseDragged(){
  float incrementY = (mouseX - pmouseX) * 0.01;
  float incrementX = (mouseY - pmouseY) * 0.01;
  
  if(mode == 0){
    pivotX += incrementX;
    pivotY += incrementY;
  } else{
    if((handCurl + incrementX  < PI/2 && incrementX > 0) || (handCurl + incrementX > 0 && incrementX < 0)){
      handCurl += incrementX;
    }
    
    //if((wristCurl + incrementY  < 5*PI/18 && incrementY > 0) || (wristCurl + incrementY > -4*PI/9 && incrementY < 0)){
    //  wristCurl += incrementY;
    //}
  }
}

void mouseClicked(){
  switch(mode){
    case 0: //set pivot stage, reset all curls
      thumbCurl = 0;
      indexCurl = 0;
      middleCurl = 0;
      ringCurl = 0;
      pinkyCurl = 0;
      break;
    case 1: //set thumb
      thumbCurl = handCurl;
      break;
    case 2: //set index
      indexCurl = handCurl;
      break;
    case 3: //set middle
      middleCurl = handCurl;
      break;
    case 4:
      ringCurl = handCurl;
      break;
    case 5: //set pinky
      pinkyCurl = handCurl;
      single_packet.setThumb(thumbCurl);
      single_packet.setIndex(indexCurl);
      single_packet.setMiddle(middleCurl);
      single_packet.setRing(ringCurl);
      single_packet.setPinky(pinkyCurl);
      single_packet.setMode(0);
      client.write(single_packet.read());
      break;
  }
  if(mode < NUMBER_OF_MODE - 1){
    mode = mode + 1;
  } else{
    mode = 0;
  }
  handCurl = 0;
}

void mouseWheel(MouseEvent event){
  float e = event.getCount();
  zoom = zoom + e*0.1;
}

int ping(){
  String dataIn = "";
  int counter = 0;
  for(int i = 0; i < 4; i++){
    client.write(str(i));
    while(!(client.available() > 0));
    if(client.available() > 0){
      dataIn = client.readString();
    }
    try{
      if(dataIn.equals(str(i)) == false){
        print(i);
        println("Something is wrong, check server side");
      } else{
        counter++;
      }
    } catch(NullPointerException e){
    }
  }
  return counter;
}
