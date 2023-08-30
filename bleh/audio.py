import numpy as np
import colorsys
import time
import serial

import pyaudio

chunk = 1024 # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16
channels = 2
fs = 44100  # Record at 44100 samples per second

p = pyaudio.PyAudio()  # Create an interface to PortAudio

#Select Device
print ( "Available devices:\n")
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print ( str(info["index"]) +  ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))
    pass

#ToDo change to your device ID
device_id = 5
device_info = p.get_device_info_by_index(device_id)
channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
# https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.__init__
with serial.Serial(port='/dev/cu.usbmodem101', baudrate=9600, timeout=10) as ser:
    time.sleep(5)
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=int(device_info["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device_info["index"],
                    )

    # frames = []  # Initialize array to store frames
    base_hue = 0
    print('\nRecording', device_id, '...\n')
    m = [1] * 5
    t = time.time()
    frame_total = [0] * 5
    frame_num = 0
    try:
        while True:
            data = stream.read(chunk)
            data_np = np.frombuffer(data, dtype='h')
            data_np = np.abs(np.fft.fft(data_np, 5, axis=0))
            for i, v in enumerate(data_np):
                frame_total[i] += v
            frame_num += 1
            for i, v in enumerate(data_np):
                m[i] = max(m[i], v)

            if time.time() > t:
                lst = [ x * 1.0/(m[i]*frame_num) for i, x in enumerate(frame_total)]
                lst = [colorsys.hsv_to_rgb((base_hue + (i/(30)))%1, 1.0, x) for i, x in enumerate(lst)]
                print(lst)
                b = bytearray()
                for x in lst:
                    for rgb in x:
                        b.append(int(30*rgb))
                for x in lst[::-1]:
                    for rgb in x:
                        b.append(int(30*rgb))
                ser.write(b)
                t = time.time() + (1.0/30)
                frame_num = 0
                frame_total = [0] * 5
                base_hue += 1.0/250
    finally:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
