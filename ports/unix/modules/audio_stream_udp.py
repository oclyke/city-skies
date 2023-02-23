import uasyncio as asyncio
import math
import hidden_shades
from hidden_shades.audio.source import ManagedAudioSource
import socket

async def stream_audio_source():
    # specify the sample frequency and sample length
    sample_frequency = 44100
    sample_length = 256
    bytes_per_sample = 2

    # add this audio source to the audio manager
    source = ManagedAudioSource(hidden_shades.audio_manager, "AudioStreamUDP", (sample_frequency, sample_length))

    # select this source for the audio manager
    hidden_shades.audio_manager.select_source("AudioStreamUDP")

    # initialize the audio manager once all audio sources have been registered
    hidden_shades.audio_manager.initialize()


    # create and connect a socket to the audio server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockaddr = socket.getaddrinfo('192.168.4.177', 42310)[0][-1]
    sock.connect(sockaddr)

    # let the server know we are listening
    sock.send(b'Hello From City-Skies')

    buffer_length = 512
    buffer = bytearray(buffer_length)

    while True:
        # wait for some amount of time
        # (to allow other tasks to operate)
        # ((this is ugly, and it's because I don't know 
        # how to make a proper asynchronous UDP client in
        # micropython))
        await asyncio.sleep(0.01)

        # read data into the buffer
        bytes_read = sock.readinto(buffer)

        # check the number of bytes read to make sure it matches the expected sample length
        expected_bytes = bytes_per_sample * sample_length
        if expected_bytes != bytes_read:
            print(f'ERROR - unexpected bumber of bytes received. Got {bytes_read} bytes when expecting {expected_bytes} bytes')
            continue

        # read the samples into the audio source
        for idx in range(sample_length):
            sample = int.from_bytes(buffer[2*(idx):2*(idx+1)], 'little')
            source._samples[idx] = sample

        # now that the audio source is filled with data compute the fft
        source.compute_fft()

        # check out some optional info on the computed FFT
        stats = source.fft_stats
        _, _, max_idx = stats
        bin_width = source.fft_bin_width
        strongest_freq = max_idx * source.fft_bin_width
        # source.get_fft_strengths(strengths)
        # print(strengths)
        # print('')
        # print(stats, bin_width, strongest_freq)
