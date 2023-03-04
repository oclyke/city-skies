import uasyncio as asyncio
import math
import hidden_shades
from hidden_shades.audio.source import ManagedAudioSource
import socket
from collections import deque

async def stream_audio_source():
    # specify the sample frequency and sample length
    sample_frequency = 44100
    sample_length = 1024

    # add this audio source to the audio manager
    source = ManagedAudioSource(hidden_shades.audio_manager, "AudioStreamUDP", (sample_frequency, sample_length))

    # select this source for the audio manager
    hidden_shades.audio_manager.select_source("AudioStreamUDP")

    # initialize the audio manager once all audio sources have been registered
    hidden_shades.audio_manager.initialize()


    # create and connect a socket to the audio server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockaddr = socket.getaddrinfo('0.0.0.0', 42310)[0][-1]
    sock.connect(sockaddr)

    # create a buffer to receive data from the socket connection
    BYTES_PER_SAMPLE = 4
    buffer_length = BYTES_PER_SAMPLE * sample_length
    buffer = bytearray(buffer_length)

    # create a deque to streamline operations
    d = deque((), sample_length)

    # preallocate memory to store the strengths in
    strengths = [0.0] * 32

    while True:
        # wait for some amount of time
        # (to allow other tasks to operate)
        # ((this is ugly, and it's because I don't know 
        # how to make a proper asynchronous UDP client in
        # micropython))
        await asyncio.sleep(0.01)

        # read data into the buffer
        bytes_read = sock.readinto(buffer)

        # convert data into samples in deque
        samples_read = int(bytes_read / BYTES_PER_SAMPLE)
        for idx in range(samples_read):
            sample = int.from_bytes(buffer[BYTES_PER_SAMPLE*(idx):BYTES_PER_SAMPLE*(idx+1)], 'little')
            d.append(sample)

        # check available data length
        available_samples = len(d)
        if available_samples < sample_length:
            # if we don't have a full sample set then continue
            print(f"waiting for {sample_length - available_samples} more samples")
            continue

        # consume the samples into the fft plan
        for idx in range(sample_length):
            source._samples[idx] = d.popleft()

        # now that the audio source is filled with data compute the fft
        source.compute_fft()

        # zero the DC component of the fft before doing any further analysis
        source.zero_fft_dc()

        # check out some optional info on the computed FFT
        stats = source.fft_stats
        sum, max, max_idx = stats
        bin_width = source.fft_bin_width
        strongest_freq = max_idx * source.fft_bin_width
        source.get_fft_strengths(strengths)
    
        # formatted = tuple(f"{s/max:.5f}" for s in strengths)
        # print(f"strongest: {strongest_freq} hz, bin_width: {bin_width}, strengths: {formatted}")
        # # print(strengths)
        # print('')
        # print(f"bin_width: {bin_width:.2f}, strongest: {strongest_freq} hz [{max_idx}]", stats, strongest_freq)
