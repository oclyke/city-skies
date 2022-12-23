# esptool modifications for OSX on ARM Silicon

the following modifications were necessary to enable esptool.py to put the
target into bootloading mode when runing from a host machine with arm64
silicon. for more details see:

https://github.com/espressif/esptool/issues/712
https://github.com/espressif/esp-idf/issues/8251

``` diff
diff --git a/esptool.py b/esptool.py
index 9353bc9..e6ed711 100755
--- a/esptool.py
+++ b/esptool.py
@@ -23,6 +23,14 @@ import sys
 import time
 import zlib
 
+import fcntl
+import termios
+
+TIOCMSET = getattr(termios, 'TIOCMSET', 0x5418)
+TIOCMGET = getattr(termios, 'TIOCMGET', 0x5415)
+TIOCM_DTR = getattr(termios, 'TIOCM_DTR', 0x002)
+TIOCM_RTS = getattr(termios, 'TIOCM_RTS', 0x004)
+
 try:
     import serial
 except ImportError:
@@ -563,6 +571,18 @@ class ESPLoader(object):
         # request is sent with the updated RTS state and the same DTR state
         self._port.setDTR(self._port.dtr)
 
+    def _setDTRAndRTS(self, dtr = False, rts = False):
+         status = struct.unpack('I', fcntl.ioctl(self._port.fileno(), TIOCMGET, struct.pack('I', 0)))[0]
+         if dtr:
+            status |= TIOCM_DTR
+         else:
+            status &= ~TIOCM_DTR
+         if rts:
+            status |= TIOCM_RTS
+         else:
+            status &= ~TIOCM_RTS
+         fcntl.ioctl(self._port.fileno(), TIOCMSET, struct.pack('I', status))
+
     def _get_pid(self):
         if list_ports is None:
             print("\nListing all serial ports is currently not available. Can't get device PID.")
@@ -614,13 +634,13 @@ class ESPLoader(object):
             fpga_delay = True if self.FPGA_SLOW_BOOT and os.environ.get("ESPTOOL_ENV_FPGA", "").strip() == "1" else False
             delay = 7 if fpga_delay else 0.5 if extra_delay else 0.05  # 0.5 needed for ESP32 rev0 and rev1
 
-            self._setDTR(False)  # IO0=HIGH
-            self._setRTS(True)   # EN=LOW, chip in reset
+            self._setDTRAndRTS(False, False)
+            self._setDTRAndRTS(True, True)
+            self._setDTRAndRTS(False, True) # IO0=HIGH & EN=LOW, chip in reset
             time.sleep(0.1)
-            self._setDTR(True)   # IO0=LOW
-            self._setRTS(False)  # EN=HIGH, chip out of reset
+            self._setDTRAndRTS(True, False) # IO0=LOW & # EN=HIGH, chip out of reset
             time.sleep(delay)
-            self._setDTR(False)  # IO0=HIGH, done
+            self._setDTRAndRTS(False, False) # IO0=HIGH, done
 
     def _connect_attempt(self, mode='default_reset', usb_jtag_serial=False, extra_delay=False):
         """ A single connection attempt """
```
