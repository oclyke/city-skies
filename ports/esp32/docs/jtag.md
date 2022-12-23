# jtag debugging
use the [esp-prog](https://docs.espressif.com/projects/espressif-esp-iot-solution/en/latest/hw-reference/ESP-Prog_guide.html) board from espressif

## connections
follow [this table](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/jtag-debugging/tips-and-quirks.html#do-not-use-jtag-pins-for-something-else)

ESP32 Pin --> JTAG Signal
MTDO / IO15 --> TDO
MTDI / IO12 --> TDI
MTCK / IO13 --> TCK (~10k pulldown)
MTMS / IO14 --> TMS (~10k pulldown)
MTDO / IO15 --> GND

## ensure flash voltage is respected
do at least one of the following:

* [make sure that the ESP32_FLASH_VOLTAGE variable is set for openocd](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/jtag-debugging/tips-and-quirks.html#openocd-configuration-variables)
* [burn the e-fuse settings for flash voltage](https://docs.espressif.com/projects/esptool/en/latest/esp32/espefuse/index.html#setting-flash-voltage-vdd-sdio)
* ensure that the MTDI (IO12) strapping pin is set to the correct level at startup

## libusb access
```sudo chmod -R 777 /dev/bus/usb/```

## openocd usage

### config files
we use pre-defined config files from espressif and aggregate them in board-specific config files called ```openocd.cfg```

where openocd takes a config file you can use the path ```./boards/${target board}/openocd.cfg```

for example for the 13r:
```./boards/13r/openocd.cfg```

### start openocd
```openocd -f ${path_to_config_file}```

```idf.py openocd --openocd-commands "-f ./boards/13r/openocd.cfg"```

### application upload
upload the application
```openocd -f ./boards/13r/openocd.cfg -c "program_esp build/micropython.bin 0x10000 verify reset exit"```

```idf.py openocd --openocd-commands "-f ./boards/13r/openocd.cfg -c 'program_esp build/micropython.bin 0x10000 verify'"```
