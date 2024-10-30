import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import simpleaudio as sa
import os

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])

if file_path:
    sample_rate, data = wavfile.read(file_path)

    if len(data.shape) == 1:
        data = np.column_stack((data, data))

    time = np.linspace(0, len(data) / sample_rate, num=len(data))

    plt.figure(figsize=(10, 4))
    plt.plot(time, data[:, 0], label="Kairys kanalas")
    plt.plot(time, data[:, 1], label="Dešinys kanalas", alpha=0.7)
    plt.title('Pradinio garso signalo laiko diagrama')
    plt.xlabel('Laikas (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()


    def apply_panning(data, sample_rate, panning_speed=2):
        n_samples = len(data)
        pan_envelope = np.sin(2 * np.pi * np.linspace(0, panning_speed, n_samples))

        left_channel = data[:, 0] * (0.5 * (1 - pan_envelope))
        right_channel = data[:, 1] * (0.5 * (1 + pan_envelope))

        return np.column_stack((left_channel, right_channel))

    panning_speed = 2
    processed_data = apply_panning(data, sample_rate, panning_speed)

    plt.figure(figsize=(10, 4))
    plt.plot(time, processed_data[:, 0], label="Kairys kanalas (apdorotas)")
    plt.plot(time, processed_data[:, 1], label="Dešinys kanalas (apdorotas)", alpha=0.7)
    plt.title('Apdoroto garso signalo laiko diagrama (su panning efektu)')
    plt.xlabel('Laikas (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

    processed_file_path = "processed_audio.wav"
    wavfile.write(processed_file_path, sample_rate, np.int16(processed_data))

    print("Pasirinkite, kurį garso įrašą norite išklausyti:")
    print("1 - Pradinis garso įrašas")
    print("2 - Apdorotas garso įrašas")
    print("q - Išeiti")
    while True:
        choice = input("Įrašykite savo pasirinkimą (1, 2 ar q): ")

        if choice == '1':
            print("Leidžiamas pradinis garso įrašas...")
            wave_obj = sa.WaveObject.from_wave_file(file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        elif choice == '2':
            print("Leidžiamas apdorotas garso įrašas...")
            wave_obj = sa.WaveObject.from_wave_file(processed_file_path)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        elif choice == 'q':
            print("Išeinama iš programos...")
            break
        else:
            print("Neteisingas pasirinkimas. Prašome įvesti 1, 2 arba q.")

    save_path = filedialog.asksaveasfilename(defaultextension=".wav",
                                             filetypes=[("WAV files", "*.wav")],
                                             title="Išsaugoti apdorotą signalą")

    if save_path:
        wavfile.write(save_path, sample_rate, np.int16(processed_data))
        print(f"Apdorotas failas išsaugotas kaip: {os.path.basename(save_path)}")