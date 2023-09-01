import numpy as np
import colorsys
import time
import serial

import pyaudio

h = 0.5             # hue change coefficient
brightness = 128    # maximum brightness out of 0-255
fade = 0.6          # how slowly to exponentially turn off lights [0.0 - 1.0]
c = 1.3             # audio -> light intensity exponent (smoothing factor should be 1.0+)
noise_gate = 0.01   # minimum signal to sum

chunk = 1024 * 4 # Record in chunks of 1024 samples
sample_format = pyaudio.paFloat32
fs = 96000  # samples per second

channels = 2 # stereo audio

p = pyaudio.PyAudio()  # Create an interface to PortAudio

#Select Device
print ( "Available devices:\n")
for i in range(0, p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print ( str(info["index"]) +  ": \t %s \n \t %s \n" % (info["name"], p.get_host_api_info_by_index(info["hostApi"])["name"]))
    pass

def get_splits(d):
    l = len(d)
    s = sum([d[k] for k in d])/8
    i, f = 0, 0
    rtn = []
    while i < l:
        f += d[i]
        if f > s:
            rtn.append(i)
            f = 0
        i += 1
    return rtn + [chunk//2]

remap = lambda x: int(abs(7.5 - x))

totals = {}
device_id = 2
device_info = p.get_device_info_by_index(device_id)
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
    m = 1
    ls = [0.0] * 8
    rs = [0.0] * 8
    splits = [3, 7, 16, 28, 49, 104, 287, chunk//2]
    print(splits)
    totals = {}
    for i in range(chunk//2):
        totals[i] = 0.0
    try:
        while True:
            while not stream.get_read_available():
                time.sleep(0.2*chunk/fs)
            data = stream.read(chunk)
            data_np = np.frombuffer(data, dtype='f')
            l_np = data_np[0::2]
            r_np = data_np[1::2]
            l_np = np.abs(np.fft.fft(l_np, axis=0))
            r_np = np.abs(np.fft.fft(r_np, axis=0))
            l_np[l_np < noise_gate] = 0
            r_np[r_np < noise_gate] = 0
            l = [0.0] * 8
            r = [0.0] * 8
            section = 0
            for i in range(chunk//2):
                if i > splits[section]:
                    section += 1
                totals[i] += (l_np[i] + l_np[chunk-1-i] + r_np[i] + r_np[chunk-1-i])
                l[section] += l_np[i] + l_np[chunk-1-i]
                r[section] += r_np[i] + r_np[chunk-1-i]
            l = [x**c for x in l]
            r = [x**c for x in r]
            m = max(m, np.max(r), np.max(l))
            ls = [max((ls[i] * fade + l[i]* (1-fade)), l[i]) for i in range(8)]
            rs = [max((rs[i] * fade + r[i]* (1-fade)), r[i]) for i in range(8)]
            
            base_hue += h*((max(r) + max(l))**3/(64*m**3))
            base_hue = base_hue % 1

            # convert to colors and emit to serial
            b = bytearray()
            for i, x in enumerate(rs + ls[::-1]):
                color = colorsys.hsv_to_rgb((base_hue - remap(i)*5.0/256)%1, 1.0, x*1.0/m)
                for rgb in color:
                    b.append(int(brightness*rgb))
            # for x in [colorsys.hsv_to_rgb((base_hue-i*5.0/256)%1, 1.0, x*1.0/m) for i, x in enumerate(rs)]:
            #     for rgb in x:
            #         b.append(int(brightness*rgb))
            # for x in [colorsys.hsv_to_rgb((base_hue-(7-i)*5.0/256)%1, 1.0, x*1.0/m) for i, x in enumerate(ls[::-1])]:
            #     for rgb in x:
            #         b.append(int(brightness*rgb))

            ser.write(b)
            splits = get_splits(totals)

    finally:
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        print(get_splits(totals))

