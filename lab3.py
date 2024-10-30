import wave
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# Signal gating
def gate_signal(signal, threshold):
    gated_signal = np.where(np.abs(signal) < threshold, 0, signal)
    return gated_signal

# Threshold calculation
def select_threshold(signal):
    m = np.mean(np.abs(signal))  # Mean of values of the signal
    print(f"Signal amplitude mean: {m:.2f}")
    
    # User input for threshold
    while True:
        try:
            user_input = input("Enter threshold or press Enter for default (20%): ")
            if user_input == "":
                threshold_percentage = 20  # Default threshold
            else:
                threshold_percentage = float(user_input)
            break
        except ValueError as e:
            print(e)
    
    threshold = (threshold_percentage / 100) * m  # Set threshold as a percentage of the mean
    return threshold

# User input for audio file
while True:
    try:
        print("Enter the name of the .wav file: ")
        file = f'{input()}.wav'
        wav_obj = wave.open(file, 'rb')
        break
    except FileNotFoundError:
        print(f"File '{file}' not found.")

# Save gated signal to file
def save_gated_signal(gated_signal, sample_freq, file):
    output_file = file.replace('.wav', '_gated.wav')
    
    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(1)  # Mono
        wav_out.setsampwidth(2)  # Number of bytes per sample
        wav_out.setframerate(sample_freq)  # Set the sample rate
        
        # Convert the gated signal to bytes and write to the file
        wav_out.writeframes(gated_signal.astype(np.int16).tobytes())

# Process wav file
sample_freq = wav_obj.getframerate()  # Sampling frequency
n_samples = wav_obj.getnframes()  # Total number of frames
n_channels = wav_obj.getnchannels()  # Number of channels

signal_wave = wav_obj.readframes(n_samples)
signal_array = np.frombuffer(signal_wave, dtype=np.int16)
wav_obj.close()

# If stereo, reshape the array
if n_channels == 2:
    signal_array = signal_array.reshape((-1, 2))

# If stereo, choose one channel
signal_mono = signal_array[:, 0] if n_channels == 2 else signal_array

# Select threshold
threshold = select_threshold(signal_mono)
print(f"Selected threshold: {threshold}")

# Apply gating
gated_signal = gate_signal(signal_mono, threshold)

# Create time axis
times = np.linspace(0, n_samples/sample_freq, num=n_samples)

# Ask user if they want to play the original or gated audio
def play_audio(signal, gated_signal):
    while True:
        try:
            choice = input(f"Play the original audio (o) / Play gated audio (g) / Exit (0): ").lower()
            if choice == 'o':
                print(f"Playing original audio...")
                sd.play(signal, samplerate=sample_freq)
                sd.wait()
            elif choice == 'g':
                print(f"Playing gated audio...")
                sd.play(gated_signal, samplerate=sample_freq)
                sd.wait()
            elif choice == '0':
                print("Exiting program.")
                break
            else:
                print("Invalid input, please enter 'o', 'g' or '0'.")
        except Exception as e:
            print(f"An error occurred: {e}")


# Plot signals
plt.figure(figsize=(12, 8))

# Plot original signal
plt.subplot(2, 1, 1)
plt.plot(times, signal_mono, label="Original Signal", alpha=0.7)
plt.axhline(y=threshold, color='g', linestyle='--', label=f"Threshold (+{threshold:.2f})")
plt.axhline(y=-threshold, color='g', linestyle='--', label=f"Threshold (-{threshold:.2f})")
plt.title(f'Original Waveform of {file}')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()

# Plot gated signal
plt.subplot(2, 1, 2)
plt.plot(times, gated_signal, label="Gated Signal", alpha=0.7, color='r')
plt.axhline(y=threshold, color='g', linestyle='--', label=f"Threshold (+{threshold:.2f})")
plt.axhline(y=-threshold, color='g', linestyle='--', label=f"Threshold (-{threshold:.2f})")
plt.title(f'Gated Waveform of {file}')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()

plt.tight_layout()
plt.show(block=False)

# Play audio
play_audio(signal_mono, gated_signal)

# Save gated signal to file
save_gated_signal(gated_signal, sample_freq, file)