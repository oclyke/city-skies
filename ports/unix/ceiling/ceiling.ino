/*
This example will receive multiple universes via Artnet and control a strip of ws2811 leds via 
Paul Stoffregen's excellent OctoWS2811 library: https://www.pjrc.com/teensy/td_libs_OctoWS2811.html
This example may be copied under the terms of the MIT license, see the LICENSE file for details
*/

#include <Artnet.h>
#include <NativeEthernet.h>
#include <NativeEthernetUdp.h>
#include <SPI.h>
#include <OctoWS2811.h>

#define DISP_WIDTH (33)
#define DISP_HEIGHT (32)
#define TOTAL_LEDS (DISP_WIDTH * DISP_HEIGHT)

// strip length (choose size of the largest strip)
const int ledsPerStrip = (2*4*DISP_WIDTH);

// pins for the individual strips
uint8_t pinList[8] = {2, 5, 6, 14};
const size_t numStrips = sizeof(pinList) / sizeof(uint8_t);

// OctoWS2811 settings
const size_t pixelExpansionFactor = 6; // this is the number of ints that should be reserved for each pixel when using OctoWS2811
const int numLeds = ledsPerStrip * numStrips;
const int numberOfChannels = numLeds * 3; // Total number of channels you want to receive (1 led = 3 channels)
DMAMEM int displayMemory[ledsPerStrip*pixelExpansionFactor];
int drawingMemory[ledsPerStrip*pixelExpansionFactor];
const int config = WS2811_GRB | WS2811_800kHz;
OctoWS2811 octo_leds(ledsPerStrip, displayMemory, drawingMemory, config, numStrips, pinList);

// Artnet settings
Artnet artnet;
const int startUniverse = 0; // CHANGE FOR YOUR SETUP most software this is 1, some software send out artnet first universe as 0.

// Check if we got all universes
const int maxUniverses = numberOfChannels / 512 + ((numberOfChannels % 512) ? 1 : 0);
bool universesReceived[maxUniverses];
bool sendFrame = 1;
int previousDataLength = 0;

// Change ip and mac address for your setup
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 4, 177);

void setup()
{
  Serial.begin(115200);
  artnet.begin(mac, ip);
  octo_leds.begin();
  initTest();

  // this will be called for each packet received
  artnet.setArtDmxCallback(onDmxFrame);
}

void loop()
{
  // we call the read function inside the loop
  artnet.read();
}

void onDmxFrame(uint16_t universe, uint16_t length, uint8_t sequence, uint8_t* data)
{
  Serial.println("HEY! We got an artnet frame!");

  
  sendFrame = 1;

  // Store which universe has got in
  if ((universe - startUniverse) < maxUniverses)
    universesReceived[universe - startUniverse] = 1;

  for (int i = 0 ; i < maxUniverses ; i++)
  {
    if (universesReceived[i] == 0)
    {
      sendFrame = 0;
      break;
    }
  }

  // read universe and put into the right part of the display buffer
  for (int i = 0; i < length / 3; i++)
  {
    int led = i + (universe - startUniverse) * (previousDataLength / 3);
    if (led < numLeds)
      octo_leds.setPixel(led, data[i * 3], data[i * 3 + 1], data[i * 3 + 2]);
  }
  previousDataLength = length;      
  
  if (sendFrame)
  {
    octo_leds.show();
    // Reset universeReceived to 0
    memset(universesReceived, 0, maxUniverses);
  }
}

void initTest()
{
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
