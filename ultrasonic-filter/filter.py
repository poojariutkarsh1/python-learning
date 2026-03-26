import serial
import time
import numpy as np
ser = serial.Serial('COM8', 9600)

time.sleep(2)  #arduino reset

data = []

print("Listening...\n")

for i in range(50):   # start with 50 values
    line = ser.readline().decode().strip()

    try:
        value = float(line)
        data.append(value)
        print(value)
    except:
        print("Skipped:", line)

ser.close()

print("\nDone collecting!")
print("Data:", data[:10])  # show first 10

arr = np.array(data)

window = 5

filtered = []

for i in range(len(arr) - window + 1):
    chunk = arr[i:i+window]
    med = np.median(chunk)
    filtered.append(med)

print("\nRAW vs FILTERED:\n")

limit = min(20, len(filtered))

for i in range(limit):
    print(f"{data[i]}  --->  {filtered[i]}")

raw_spikes = sum(1 for x in data if x > 100)
filtered_spikes = sum(1 for x in filtered if x > 100)

print("\nSpikes in raw data:", raw_spikes)
print("Spikes after filtering:", filtered_spikes)