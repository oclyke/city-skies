// Record sound and send it as raw data to a remote client over a UDP connection
#include <Bounce.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

#include <NativeEthernet.h>
#include <NativeEthernetUdp.h>

// GUItool: begin automatically generated code
AudioInputI2S            i2s2;           //xy=105,63
AudioAnalyzePeak         peak1;          //xy=278,108
AudioRecordQueue         queue1;         //xy=281,63
AudioPlaySdRaw           playRaw1;       //xy=302,157
AudioOutputI2S           i2s1;           //xy=470,120
AudioConnection          patchCord1(i2s2, 0, queue1, 0);
AudioConnection          patchCord2(i2s2, 0, peak1, 0);
AudioConnection          patchCord3(playRaw1, 0, i2s1, 0);
AudioConnection          patchCord4(playRaw1, 0, i2s1, 1);
AudioControlSGTL5000     sgtl5000_1;     //xy=265,212
// GUItool: end automatically generated code


// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 4, 177);

unsigned int localPort = 42310; // local port to listen on

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

// which input on the audio shield will be used?
const int myInput = AUDIO_INPUT_LINEIN;
//const int myInput = AUDIO_INPUT_MIC;

// buffer for recorded samples to be sent via UDP
const int block_bytelen = 256;
const int buffer_blocklen = 2;
const int buffer_bytelen = block_bytelen * buffer_blocklen;
byte buffer[buffer_bytelen];

// Variables to track the remote connection
bool have_remote = false;
IPAddress remoteIP;
uint16_t remotePort = 0;

void setup() {
  // Open serial communications
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Hello world");

  // Audio connections require memory, and the record queue
  // uses this memory to buffer incoming audio.
  AudioMemory(60);

  // Enable the audio shield, select input, and enable output
  sgtl5000_1.enable();
  sgtl5000_1.inputSelect(myInput);
  sgtl5000_1.volume(0.5);

  // start the Ethernet
  Ethernet.begin(mac, ip);

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

  // Begin recording
  startRecording();
}


void loop() {
  // when using a microphone, continuously adjust gain
  if (myInput == AUDIO_INPUT_MIC){
    adjustMicLevel();
  }

  // check any incoming UDP packets
  handleUDPPackets();

  fillBuffer();
  pushBuffer();
}


void startRecording() {
  Serial.println("startRecording");
  queue1.begin();
}

void fillBuffer() {
  if (queue1.available() >= buffer_blocklen) {
    // Fetch 2 blocks from the audio library and copy
    // into a 512 byte buffer.  The Arduino SD library
    // is most efficient when full 512 byte sector size
    // writes are used.
    memcpy(buffer, queue1.readBuffer(), block_bytelen);
    queue1.freeBuffer();
    memcpy(buffer + block_bytelen, queue1.readBuffer(), block_bytelen);
    queue1.freeBuffer();
  }
}

void pushBuffer() {
  if (!have_remote) {
    Serial.println("No remote client connected, data discarded\n");
  } else {
    // send a reply to the IP address and port that sent us the packet we received
    Udp.beginPacket(remoteIP, remotePort);
    Udp.write(buffer, buffer_bytelen);
    Udp.endPacket();

    for (size_t idx = 0; idx < buffer_bytelen / 2; idx++) {
      // try to reconstruct the value
      uint16_t value = buffer[2 *idx] + buffer[2 *(idx + 1)] * 255;
      Serial.println(value);
    }
  }
}

void handleUDPPackets() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    // Store the info about the remote client
    remoteIP = Udp.remoteIP();
    remotePort = Udp.remotePort();
    have_remote = true;

    // read the packet into packetBufffer
    char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);

    // alert to the status of received data
    Serial.println("Received UDP packet:\t");
    Serial.println(packetBuffer);
  }
}

void adjustMicLevel() {
  // TODO: read the peak1 object and adjust sgtl5000_1.micGain()
  // if anyone gets this working, please submit a github pull request :-)
}
