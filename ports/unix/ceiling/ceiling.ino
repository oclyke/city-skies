/*
This example will receive multiple universes via Artnet and control a strip of ws2811 leds via 
Paul Stoffregen's excellent OctoWS2811 library: https://www.pjrc.com/teensy/td_libs_OctoWS2811.html
This example may be copied under the terms of the MIT license, see the LICENSE file for details
*/

#include <NativeEthernet.h>
#include <NativeEthernetUdp.h>
#include <SPI.h>
#include <OctoWS2811.h>

// display info
const size_t DISPLAY_WIDTH = 33;
const size_t DISPLAY_HEIGHT = 32;
const size_t ledsPerStrip = (2*(4*DISPLAY_WIDTH)); // use the largest number of all strips

// pin mapping for strips, as well as calculation of number of strips
uint8_t pinList[8] = {2, 5, 6, 14};
size_t numStrips = sizeof(pinList) / sizeof(uint8_t);
const int numLeds = ledsPerStrip * numStrips;

// display and drawing memory
const size_t octoWS2811IntsPerPixel = 6; // the required number of ints per pixel when using octoWS2811
DMAMEM int displayMemory[ledsPerStrip*octoWS2811IntsPerPixel];
int drawingMemory[ledsPerStrip*octoWS2811IntsPerPixel];

// the octoWS2811 manager
const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 octo_leds(ledsPerStrip, displayMemory, drawingMemory, config, numStrips, pinList);

// IP Address
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 4, 177);
unsigned int localPort = 6454; // Standard Art-Net port


// buffers for receiving and sending data
const size_t ARTNET_MAX_BUFFER_LEN = 18 + 512;
char rx_buffer[ARTNET_MAX_BUFFER_LEN];

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

// an incoming pixel data buffer
#define NUM_LEDS (DISPLAY_WIDTH * DISPLAY_HEIGHT)
int pixels[NUM_LEDS];
const size_t start_universe = 0;
const size_t pixel_len_bytes = sizeof(pixels);

// a very crude way to signal a full frame reception:
// compare the number of packets received against the number expected
const size_t universes_expected = (pixel_len_bytes / 512) + 1;
size_t universes_received = 0;

void setup()
{
  Serial.begin(115200);

  // start the Ethernet
  Ethernet.begin(mac, ip);

  octo_leds.begin();
  // initTest();

  // Check for Ethernet hardware present
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
    while (true) {
      delay(1); // do nothing, no point running without Ethernet hardware
    }
  }
  if (Ethernet.linkStatus() == LinkOFF) {
    Serial.println("Ethernet cable is not connected.");
  }

  // start UDP
  Udp.begin(localPort);
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    showPacketInfo(packetSize);
    Udp.read(rx_buffer, ARTNET_MAX_BUFFER_LEN);

    uint8_t sequence = rx_buffer[12];
    size_t length = (((uint16_t)rx_buffer[16]) << 8) | (((uint16_t)rx_buffer[17]) << 0);
    size_t universe = ((((uint16_t)rx_buffer[15]) << 8) | (((uint16_t)rx_buffer[14]) << 0)) & 0x7fff;

    Serial.printf("sequence: %d, length: %d, universe: %d\n", sequence, length, universe);

    size_t universe_offset = universe - start_universe;
    size_t start_index = 512 * universe_offset; // any universe offset is assumed to have been caused by a full artnet packet
    size_t final_index = start_index + length - 1;
    if (final_index < pixel_len_bytes) {
      uint8_t* pixel_buffer_start = ((uint8_t*)pixels) + start_index;
      memcpy(pixel_buffer_start, &rx_buffer[18], length);

      universes_received++; // mark this universe as received
      if (universes_received >= universes_expected) {
        universes_received = 0;

        // Now push the pixel data into the output driver
        copyPixelsToOutput();
      }
    } else {
      Serial.printf("DATA TOO LONG. got %d bytes, can absorb up to %d bytes\n", final_index, pixel_len_bytes);
    }
  }
}

void copyPixelsToOutput() {
  for (size_t v = 0; v < DISPLAY_HEIGHT; v++) {
    if(v & 0x01) {
      // odd rows are backward
      for (size_t u = 0; u < DISPLAY_WIDTH; u++) {
        octo_leds.setPixel(v * DISPLAY_WIDTH + u, pixels[((v + 1) * DISPLAY_WIDTH) - u - 1]);
      }
    } else {
      // even rows are forward
      for (size_t u = 0; u < DISPLAY_WIDTH; u++) {
        octo_leds.setPixel(v * DISPLAY_WIDTH + u, pixels[v * DISPLAY_WIDTH + u]);
      }
    }
  }
  octo_leds.show();
}

void showPacketInfo(int packetSize) {
  Serial.print("Received packet of size ");
  Serial.println(packetSize);
  Serial.print("From ");
  IPAddress remote = Udp.remoteIP();
  for (int i=0; i < 4; i++) {
    Serial.print(remote[i], DEC);
    if (i < 3) {
      Serial.print(".");
    }
  }
  Serial.print(", port ");
  Serial.println(Udp.remotePort());
}

void initTest(){
  for (int i = 0 ; i < numLeds ; i++)
    octo_leds.setPixel(i, 127, 0, 0);
  octo_leds.show();
  delay(500);
  for (int i = 0 ; i < numLeds  ; i++)
    octo_leds.setPixel(i, 0, 127, 0);
  octo_leds.show();
  delay(500);
  for (int i = 0 ; i < numLeds  ; i++)
    octo_leds.setPixel(i, 0, 0, 127);
  octo_leds.show();
  delay(500);
  for (int i = 0 ; i < numLeds  ; i++)
    octo_leds.setPixel(i, 0, 0, 0);
  octo_leds.show();
}
