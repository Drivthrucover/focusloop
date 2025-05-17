import numpy as np
import zmq
import time
from pylsl import StreamInlet, resolve_streams
from scipy.signal import welch, iirnotch, filtfilt, butter
from pylsl import StreamInlet, resolve_streams
import time

print("Looking for an EEG stream...")

# Keep trying for up to 10 seconds
start_time = time.time()
streams = []

while not streams and time.time() - start_time < 10:
    streams = resolve_streams()
    streams = [s for s in streams if s.type() == 'EEG']
    time.sleep(0.5)

if not streams:
    print("No EEG stream found. Make sure Muse is streaming via muselsl.")
    exit(1)

inlet = StreamInlet(streams[0])
print("EEG stream found.")


# Sampling rate (Muse sends 256 Hz)
sampling_rate = 256
n_channels = 4
window_size = sampling_rate * 1  # 1 second = 256 samples
buffer = np.zeros((window_size, n_channels))

# Reading new data into the buffer while deleting the oldest data
print("Streaming EEG and filling buffer...")

while True:
    sample, timestamp = inlet.pull_sample()
    # Check if the channel reads -1000 and skip if so
    if -1000 in sample[:4]:
        print("Skipping sample with -1000 value.")
        continue
    buffer = np.roll(buffer, -1, axis=0)       # Shift buffer left by 1
    buffer[-1, :] = sample[:4]                     # Insert new sample at the end

    # Optional: show first channel value to confirm updates
    print(f"{timestamp:.3f} | CH1: {sample[0]:.4f}")


