import numpy as np
import colorsys
import time
import serial

import pyaudio

def remap(i):
    if i < 4:
        return i
    return 7 - i

chunk = 1024 * 4 # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16
channels = 2
fs = 1024 * 16 * 4  # samples per second

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
# channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
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

    base_hue = 0
    print('\nRecording', device_id, '...\n')
    m = 1
    s = [0.0] * 4
    l, r = [0.0] * 4, [0.0] * 4

    try:
        while True:
            while not stream.get_read_available():
                continue
            data = stream.read(chunk)
            data_np = np.frombuffer(data, dtype='h')

            # data_np = np.abs(np.fft.fft(data_np, axis=0))
            # d = [
            #         (np.sum(data_np[0:512]))**2,
            #         (np.sum(data_np[512:4096]))**2,
            #         (np.sum(data_np[4096:7770]))**2,
            #         (np.sum(data_np[7770:]))**2
            #     ]
            # m = max(m, np.max(d))
            # s = [max((s[i] * 0.05 +d[i]*0.95), d[i]) for i in range(4)]

            l_channel = data_np[0::2]
            r_channel = data_np[1::2]
            l_channel = np.abs(np.fft.fft(l_channel, axis=0))
            dl = [
                    (np.sum(l_channel[0:256]))**2,
                    (np.sum(l_channel[256:2048]))**2,
                    (np.sum(l_channel[2048:3850]))**2,
                    (np.sum(l_channel[3850:]))**2
                ]
            m = max(m, np.max(dl))
            l = [max((l[i] * 0.05 + dl[i]*0.95), dl[i]) for i in range(4)]

            r_channel = np.abs(np.fft.fft(r_channel, axis=0))
            dr = [
                    (np.sum(r_channel[0:256]))**2,
                    (np.sum(r_channel[256:2048]))**2,
                    (np.sum(r_channel[2048:3850]))**2,
                    (np.sum(r_channel[3850:]))**2
                ]
            m = max(m, np.max(dr))
            r = [max((r[i] * 0.05 + dr[i]*0.95), dr[i]) for i in range(4)]
            # print(len(r_channel))
            
            # for i in range(4)[::-1]:
            #     l[i] = max(l[i] * 0.5, (max(l_channel[i], l_channel[i] * 0.5 + l[i] * 0.5)) - sum(l[i:]))
            #     r[i] = max(r[i] * 0.5, (max(r_channel[i], r_channel[i] * 0.5 + r[i] * 0.5)) - sum(r[i:]))
            # m = max(m, np.max(l), np.max(r))
    

            # l = [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(l)]
            # r = [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(r)]
            b = bytearray()
            for x in [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(r[0:4])]:
                for rgb in x:
                    b.append(int(64*rgb))
            for x in [colorsys.hsv_to_rgb((base_hue + 0.5 + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(l[0:4])][::-1]:
                for rgb in x:
                    b.append(int(64*rgb))
            if ser.writable():
                ser.write(b)
            base_hue += 1.0/500
    finally:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
