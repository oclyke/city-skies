import uasyncio as asyncio
from hidden_shades.audio.source import ManagedAudioSource
from machine import I2S, Pin
import ics43432


class ICS43432AudioSource(ManagedAudioSource):
    def __init__(self, path, name, audio_config, i2s_pin_config):
        super().__init__(path, name, audio_config)

        sample_freq, num_samples = audio_config
        sck_pin, ws_pin, sd_pin = i2s_pin_config
        bytes_per_sample = 4

        # create a buffer
        self._buf = bytearray(bytes_per_sample * num_samples)

        # make i2s driver object
        self._driver = I2S(
            1,
            sck=Pin(sck_pin),
            ws=Pin(ws_pin),
            sd=Pin(sd_pin),
            mode=I2S.RX,
            bits=bytes_per_sample * 8,
            format=I2S.MONO,  # I2S.STEREO | I2S.MONO
            rate=sample_freq,
            ibuf=bytes_per_sample * 2 * num_samples,
        )

        # callback for non-blocking operation
        self._data_flag = asyncio.ThreadSafeFlag()

        self._driver.irq(lambda driver: self._handle_data(driver))  # attach callback

    def _handle_data(self, driver):
        """
        callback when data is present from the I2S driver
        """
        self._data_flag.set()

    async def run(self):
        self._driver.readinto(self._buf)  # trigger first read manually

        while True:
            # explicitly allow processing for other tasks in case flag is already set
            await asyncio.sleep(0)

            # wait for data to be filled
            await self._data_flag.wait()
            print("data ready")

            # extract the bytes from the drivers
            self._driver.readinto(self._buf)

            # format bytes into statically allocated floating point sample buffer
            ics43432.bytes_to_float_buffer(self._buf, self._buffer)

            # perform standard processsing
            self.apply_volume()
            self.fft.compute()
            self.fft_postprocess()
