// https://github.com/una1veritas/Processing-sketches/blob/master/libraries/udp/examples/udp/udp.pde
import hypermedia.net.*;

UDP control_udp;
UDP data_udp;

// the dimensions of the simulated display in number of pixels
int WIDTH = 23;
int HEIGHT = 13;

// a scaling factor, each LED is represented as a square of this size
int SCALE = 50;

// memory for the simulated pixels
color[] leds = new color[WIDTH * HEIGHT];

void settings() {
  size(WIDTH * SCALE, HEIGHT * SCALE);
  
}

void setup() {
  noStroke();
 colorMode(RGB, 255, 255, 255);
  
  // set up UDP listener for data messages
  data_udp = new UDP( this, 6420 );
  data_udp.log( true );
  data_udp.listen( true );
}

//process events
void draw() {
  for (int idx = 0; idx < WIDTH; idx++) {
   for (int idy = 0; idy < HEIGHT; idy++) {
    fill(color(leds[idy * WIDTH + idx]));  // Use color variable 'c' as fill color
    rect( SCALE*idx,  SCALE*idy, 50, 50);  // Draw rectangle 
   }
  }
}

 void receive( byte[] data ) {       // <-- default handler
//void receive( byte[] data, String ip, int port ) {  // <-- extended handler
  if (data.length == 4) {
    int w = (int(data[1]) << 8) | (int(data[0]));
    int h = (int(data[3]) << 8) | (int(data[2]));
  } else {
    int bpp = 4;
    for (int idx = 0; idx < data.length / bpp; idx++) {
      leds[idx] = color(int(data[idx * bpp + 2]), int(data[idx * bpp + 1]), int(data[idx * bpp + 0]));
    }
  }
}
