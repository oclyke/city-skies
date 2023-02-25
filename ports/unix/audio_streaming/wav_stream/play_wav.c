/*
 * Copyright (c) 2015 Andrew Kelley
 *
 * This file is part of libsoundio, which is MIT licensed.
 * See http://opensource.org/licenses/MIT
 */

#include <soundio/soundio.h>
#include <sndfile.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static int usage(char *exe) {
    fprintf(stderr, "Usage: %s <input file>\n", exe);
    return 1;
}

static void write_sample_s16ne(char *ptr, double sample) {
    int16_t *buf = (int16_t *)ptr;
    double range = (double)INT16_MAX - (double)INT16_MIN;
    double val = sample * range / 2.0;
    *buf = val;
}

static void write_sample_s32ne(char *ptr, double sample) {
    int32_t *buf = (int32_t *)ptr;
    double range = (double)INT32_MAX - (double)INT32_MIN;
    double val = sample * range / 2.0;
    *buf = val;
}

static void write_sample_float32ne(char *ptr, double sample) {
    float *buf = (float *)ptr;
    *buf = sample;
}

static void write_sample_float64ne(char *ptr, double sample) {
    double *buf = (double *)ptr;
    *buf = sample;
}

// data for wav info
SF_INFO sfinfo;
SNDFILE *infile = NULL;

// buffer for samples from the file
#define	BLOCK_SIZE (4096)
double* snd_buf = NULL;


static void (*write_sample)(char *ptr, double sample);

static volatile bool want_pause = false;
static void write_callback(struct SoundIoOutStream *outstream, int frame_count_min, int frame_count_max) {
    struct SoundIoChannelArea *areas;
    int err;

    // attempt to feed the maximum number of frames
    // (one frame includes a sample for every channel)
    // output: single channel
    // input (file): channel count from sfinfo struct
    int frames_left = frame_count_max;

    for (;;) {
        int frame_count = frames_left;

        // restrict the number of frames to handle in this chunk to the size
        // of the buffer used to read from the file
        int allowed_frames = BLOCK_SIZE / sfinfo.channels;
        if (frame_count > allowed_frames) {
            frame_count = allowed_frames;
        }

        // read new data into the buffer
        int file_readcount = (int) sf_readf_double (infile, snd_buf, frame_count);

        // check for 0 frame count
        if (!frame_count) {
            break;
        }

        if (file_readcount <= 0) {
            break;
        }



        // start writing to the output stream
        if ((err = soundio_outstream_begin_write(outstream, &areas, &frame_count))) {
            fprintf(stderr, "unrecoverable stream error: %s\n", soundio_strerror(err));
            exit(1);
        }

        // expose info about the output
        const struct SoundIoChannelLayout *layout = &outstream->layout;

        // actually set channel data using the proper write_samples function
        for (int frame = 0; frame < frame_count; frame += 1) {
            double sample = snd_buf[frame * sfinfo.channels + 0]; // get the sample from just one channel of the input audio... this could later be improved

            // maybe I will need to track progress through the file in terms of sample rate? see seconds_offset in the original sine example...

            for (int channel = 0; channel < layout->channel_count; channel += 1) {
                write_sample(areas[channel].ptr, sample);
                areas[channel].ptr += areas[channel].step;
            }
        }

        // stop writing to the output stream
        if ((err = soundio_outstream_end_write(outstream))) {
            if (err == SoundIoErrorUnderflow)
                return;
            fprintf(stderr, "unrecoverable stream error: %s\n", soundio_strerror(err));
            exit(1);
        }


        // decrement the number of frames that need to be pushed into the output
        frames_left -= frame_count;
        if (frames_left <= 0) {
            break;
        }
    }

    soundio_outstream_pause(outstream, want_pause);
}

static void underflow_callback(struct SoundIoOutStream *outstream) {
    static int count = 0;
    fprintf(stderr, "underflow %d\n", count++);
}

int main(int argc, char **argv) {
    int retval = 0;
    char *exe = argv[0];
    
    char *stream_name = NULL;
    double latency = 0.0;
    int sample_rate = 0;


    // check the number of arguments
    if (2 != argc) {
		printf("Unexpected number of arguments\n");
        return usage(exe);
	}

    // get wav file to play
	char* infilename = argv[1];
	if (infilename [0] == '-') {
        printf ("Error : Input filename (%s) looks like an option.\n\n", infilename) ;
		return usage (exe);
	};

    // open the wav file
    memset (&sfinfo, 0, sizeof (sfinfo)) ;
    infile = sf_open(infilename, SFM_READ, &sfinfo);
	if (NULL == infile) {
        printf ("Not able to open input file %s.\n", infilename);
		puts (sf_strerror (NULL));
		goto cleanup_sf;
	};

    struct SoundIo *soundio = soundio_create();
    if (!soundio) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    // allocate the buffer for samples from the file
	snd_buf = malloc (BLOCK_SIZE * sizeof (double)) ;
	if (snd_buf == NULL) {
        printf ("Error : Out of memory.\n\n");
		return 1;
	};

    // get the soundio backend to use
    // by default this will try backends in order and select the first that is successful
    enum SoundIoBackend backend = SoundIoBackendNone;
    retval = (backend == SoundIoBackendNone) ? soundio_connect(soundio) : soundio_connect_backend(soundio, backend);
    if (0 != retval) {
        fprintf(stderr, "Unable to connect to backend: %s\n", soundio_strerror(retval));
        return 1;
    }
    fprintf(stderr, "Backend: %s\n", soundio_backend_name(soundio->current_backend));

    // with an up-to-date list of output devices select the first that works with the backend
    soundio_flush_events(soundio); // not sure why this is necessary - I think it is meant to drive actions such as updating lists of connected devices etc...
    int selected_device_index = -1;
    selected_device_index = soundio_default_output_device_index(soundio);
    if (selected_device_index < 0) {
        fprintf(stderr, "Output device not found\n");
        return 1;
    }

    // expose the output device that will be used for writing
    struct SoundIoDevice *device = soundio_get_output_device(soundio, selected_device_index);
    if (!device) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }
    fprintf(stderr, "Output device: %s\n", device->name);

    // check that the device can be probed
    if (device->probe_error) {
        fprintf(stderr, "Cannot probe device: %s\n", soundio_strerror(device->probe_error));
        return 1;
    }

    // create an output stream
    struct SoundIoOutStream *outstream = soundio_outstream_create(device);
    if (!outstream) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }
    outstream->write_callback = write_callback;
    outstream->underflow_callback = underflow_callback;
    outstream->name = stream_name;
    outstream->software_latency = latency;
    outstream->sample_rate = sample_rate;

    // set the outstream sample rate from the data read by libsndfile
    outstream->sample_rate = sfinfo.samplerate;

    // select the appropriate format for writing samples
    if (soundio_device_supports_format(device, SoundIoFormatFloat32NE)) {
        outstream->format = SoundIoFormatFloat32NE;
        write_sample = write_sample_float32ne;
    } else if (soundio_device_supports_format(device, SoundIoFormatFloat64NE)) {
        outstream->format = SoundIoFormatFloat64NE;
        write_sample = write_sample_float64ne;
    } else if (soundio_device_supports_format(device, SoundIoFormatS32NE)) {
        outstream->format = SoundIoFormatS32NE;
        write_sample = write_sample_s32ne;
    } else if (soundio_device_supports_format(device, SoundIoFormatS16NE)) {
        outstream->format = SoundIoFormatS16NE;
        write_sample = write_sample_s16ne;
    } else {
        fprintf(stderr, "No suitable device format available.\n");
        return 1;
    }

    // open the output stream
    if ((retval = soundio_outstream_open(outstream))) {
        fprintf(stderr, "unable to open device: %s", soundio_strerror(retval));
        return 1;
    }
    fprintf(stderr, "Software latency: %f\n", outstream->software_latency);
    fprintf(stderr,
            "'p\\n' - pause\n"
            "'u\\n' - unpause\n"
            "'P\\n' - pause from within callback\n"
            "'c\\n' - clear buffer\n"
            "'q\\n' - quit\n");

    if (outstream->layout_error) {
        fprintf(stderr, "unable to set channel layout: %s\n", soundio_strerror(outstream->layout_error));
    }
    if ((retval = soundio_outstream_start(outstream))) {
        fprintf(stderr, "unable to start device: %s\n", soundio_strerror(retval));
        return 1;
    }

    for (;;) {
        soundio_flush_events(soundio);
        int c = getc(stdin);
        if (c == 'p') {
            // pause
            int result = soundio_outstream_pause(outstream, true);
            fprintf(stderr, "pausing result: %s\n", soundio_strerror(result));
        } else if (c == 'P') {
            // want pause??
            want_pause = true;
        } else if (c == 'u') {
            want_pause = false;
            int result = soundio_outstream_pause(outstream, false);
            fprintf(stderr, "unpausing result: %s\n", soundio_strerror(result));
        } else if (c == 'c') {
            int result = soundio_outstream_clear_buffer(outstream);
            fprintf(stderr, "clear buffer result: %s\n", soundio_strerror(result));
        } else if (c == 'q') {
            // quite
            break;
        } else if (c == '\r' || c == '\n') {
            // ignore
        } else {
            fprintf(stderr, "Unrecognized command: %c\n", c);
        }
    }

    soundio_outstream_destroy(outstream);
    soundio_device_unref(device);
    soundio_destroy(soundio);
cleanup_sf:
	sf_close (infile) ;

    return retval;
}
