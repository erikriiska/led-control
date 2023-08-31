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
    s = sum(vals)/8
    i = 0
    f = 0
    rtn = []
    while i < l:
        f += d[i]
        if f > s:
            rtn.append(i - 1)
            f = 0
        i += 1
    return [0] + rtn + [2048]

# totals = {}
#ToDo change to your device ID
device_id = 5
device_info = p.get_device_info_by_index(device_id)
# channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
# https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.__init__
# if "your mom":
with serial.Serial(port='/dev/cu.usbmodem101', baudrate=115200, timeout=10) as ser:
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
    ls = [0.0] * 8
    rs = [0.0] * 8
    # l, r = [0.0] * 4, [0.0] * 4
    # totals = {}
    # for i in range(chunk*2):
    #     totals[i] = 0
    bleh = lambda x : x if x > 10 else 0
    splits = [0, 26, 96, 206, 349, 498, 662, 839, 2048]
    splits = [int(x/2) for x in splits]
    # splits =  # [0, 8, 16, 32, 64, 128, 256, 512, 1024] 
    # splits = [sum(splits[0:i]) for i in range(1, 10)]
    print(splits)
    totals = {}
    for i in range(2048):
        totals[i] = 0.0001
    try:
        while True:
            while not stream.get_read_available():
                time.sleep(1.0/44100)
            data = stream.read(chunk)
            # while stream.get_read_available():
            #     data = stream.read(chunk)
            data_np = np.frombuffer(data, dtype='h')
            l_np = data_np[0::2]
            r_np = data_np[1::2]
            print(len(l_np))
            l_np = np.abs(np.fft.fft(l_np, axis=0))
            r_np = np.abs(np.fft.fft(r_np, axis=0))
            # data_np = (np.fft.fft(data_np, axis=0))
            # data_np = np.abs(data_np)
            for i in range(1024):
                totals[i] += (l_np[i] + l_np[2047-i] + r_np[i] + r_np[2047])
            # l_np[l_np < 20] = 0
            # r_np[r_np < 20] = 0
            l_np = np.cumsum(l_np)
            # print(l_np)
            r_np = np.cumsum(r_np)
            l = [(l_np[splits[i+1]]-l_np[splits[i]] + l_np[2047-splits[i]] - l_np[2047-splits[i+1]])**2 for i in range(8)]
            r = [(r_np[splits[i+1]]-r_np[splits[i]] + r_np[2047-splits[i]] - r_np[2047-splits[i+1]])**2 for i in range(8)]
            m = max(m, np.max(r), np.max(l))
            
            ls = [max((ls[i] * 0.7 + l[i]*0.3), l[i]) for i in range(8)]
            rs = [max((rs[i] * 0.7 + r[i]*0.3), r[i]) for i in range(8)]

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
            for x in [colorsys.hsv_to_rgb((base_hue+i*10.0/256)%1, 1.0, x*1.0/m) for i, x in enumerate(ls)]:
                for rgb in x:
                    b.append(int(128*rgb))
            for x in [colorsys.hsv_to_rgb((base_hue+(8-i)*10.0/256)%1, 1.0, x*1.0/m) for i, x in enumerate(rs[::-1])]:
                for rgb in x:
                    b.append(int(128*rgb))
            # for x in [colorsys.hsv_to_rgb((base_hue + 0.5 + (i/(15)))%1, 1.0, x*1.0/m) for i, x in enumerate(l[0:4])][::-1]:
            #     for rgb in x:
            #         b.append(int(64*rgb))
            
            t = time.time()
            if ser.writable():
                ser.write(b)
            print(time.time()-t)
            base_hue += 1.0/256
            # if base_hue >= 1:
            #     splits = [int(x/2) for x in get_splits(totals)]
            base_hue = base_hue % 1
            print(get_splits(totals))
            #     print(splits)
    finally:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # print(get_splits(totals))

        .0001201629638671875
