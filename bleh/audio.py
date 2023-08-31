import numpy as np
import colorsys
import time
import serial

import pyaudio

def remap(i):
    if i < 4:
        return i
    return 7 - i

chunk = 1024 * 2 # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16
channels = 2
fs = 44100  # samples per second

p = pyaudio.PyAudio()  # Create an interface to PortAudio

#Select Device
print ( "Available devices:\n")
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print ( str(info["index"]) +  ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))
    pass

def get_splits(d):
    l = len(d)
    vals = [d[k] for k in d]
    s = sum(vals)/16
    i = 0
    f = 0
    rtn = []
    while i < l:
        f += d[i]
        if f > s:
            rtn.append(i - 1)
            f = 0
        i += 1
    return rtn

# totals = {}
#ToDo change to your device ID
device_id = 5
device_info = p.get_device_info_by_index(device_id)
# channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
# https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.__init__
# if "your mom":
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
    s = [0.0] * 8
    # l, r = [0.0] * 4, [0.0] * 4
    # totals = {}
    # for i in range(chunk*2):
    #     totals[i] = 0
    bleh = lambda x : x if x > 10 else 0
    splits = [0, 8, 16, 32, 64, 128, 256, 512, 1600] # [173, 714, 3634, 4096, 4559, 7479, 8018] # [250, 750, 1750, 3750, 6000, 7200, 8100]
    try:
        while True:
            while not stream.get_read_available():
                time.sleep(2*1024.0/44100)
                continue
            data = stream.read(chunk)
            data_np = np.frombuffer(data, dtype='h')
            # print((data_np[0]))
            # print(np.fft.fftfreq(data_np))
            data_np = (np.fft.fft(data_np, axis=0))
            # print(np.angle(data_np))
            # print(np.fft.fftfreq(8, data_np))
            # data_np 
            data_np = np.abs(data_np)
            data_np[data_np < 20] = 0
            # data_np = list(map(lambda x: x if x > 10 else 0, data_np))
            data_np = np.cumsum(data_np)
            d = [(data_np[splits[i+1]]-data_np[splits[i]] + data_np[4095-splits[i]] - data_np[4095-splits[i+1]])**2 for i in range(8)]
            # d = [
            #         (np.sum(data_np[:splits[0]],         )  + np.sum(data_np[4096-  splits[0]:]))**2,
            #         (np.sum(data_np[splits[0]:splits[1]])  + np.sum(data_np[4096 - splits[1]:4096 - splits[0]]))**2,
            #         (np.sum(data_np[splits[1]:splits[2]])  + np.sum(data_np[4096 - splits[2]:4096 - splits[1]]))**2,
            #         (np.sum(data_np[splits[2]:splits[3]])  + np.sum(data_np[4096 - splits[3]:4096 - splits[2]]))**2,
            #         (np.sum(data_np[splits[3]:splits[4]])  + np.sum(data_np[4096 - splits[4]:4096 - splits[3]]))**2,
            #         (np.sum(data_np[splits[4]:splits[5]])  + np.sum(data_np[4096 - splits[5]:4096 - splits[4]]))**2,
            #         (np.sum(data_np[splits[5]:splits[6]])  + np.sum(data_np[4096 - splits[6]:4096 - splits[5]]))**2,
            #         (np.sum(data_np[splits[6]:splits[7]])  + np.sum(data_np[4096 - splits[7]:4096 - splits[6]]))**2,
            #     ]
            m = max(m, np.max(d))
            
            s = [max((s[i] * 0.7 +d[i]*0.3), d[i]) for i in range(8)]

            # l_channel = data_np[0::2]
            # # print(l_channel)
            # r_channel = data_np[1::2]
            # l_channel = np.abs(np.fft.fft(l_channel, axis=0))
            # dl = [
            #         (np.sum(l_channel[0:256]))**1.2,
            #         (np.sum(l_channel[256:2048]))**1.2,
            #         (np.sum(l_channel[2048:3850]))**1.2,
            #         (np.sum(l_channel[3850:]))**1.2
            #     ]
            # m = max(m, np.max(dl))
            # l = [max((l[i] * 0.05 + dl[i]*0.95), dl[i]) for i in range(4)]

            # r_channel = np.abs(np.fft.fft(r_channel, axis=0))
            # dr = [
            #         (np.sum(r_channel[0:256]))**1.2,
            #         (np.sum(r_channel[256:2048]))**1.2,
            #         (np.sum(r_channel[2048:3850]))**1.2,
            #         (np.sum(r_channel[3850:]))**1.2
            #     ]
            # m = max(m, np.max(dr))
            # r = [max((r[i] * 0.05 + dr[i]*0.95), dr[i]) for i in range(4)]
            # print(len(r_channel))
            
            # for i in range(4)[::-1]:
            #     l[i] = max(l[i] * 0.5, (max(l_channel[i], l_channel[i] * 0.5 + l[i] * 0.5)) - sum(l[i:]))
            #     r[i] = max(r[i] * 0.5, (max(r_channel[i], r_channel[i] * 0.5 + r[i] * 0.5)) - sum(r[i:]))
            # m = max(m, np.max(l), np.max(r))
    

            # l = [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(l)]
            # r = [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(r)]
            b = bytearray()
            for x in [colorsys.hsv_to_rgb((base_hue + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(s)]:
                for rgb in x:
                    b.append(int(64*rgb))
            # for x in [colorsys.hsv_to_rgb((base_hue + 0.5 + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(l[0:4])][::-1]:
            #     for rgb in x:
            #         b.append(int(64*rgb))
            if ser.writable():
                ser.write(b)
            base_hue += 1.0/500
    finally:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # print(get_splits(totals))
