import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import time
from scipy.signal import butter, lfilter

# --- آڈیو سیٹنگز ---
SAMPLE_RATE = 44100  
GAIN_FACTOR = 18.0   # والیم کو 18 گنا بڑھانے کے لیے (فل لاؤڈ)
CHANNELS = 1         

# بیس فلٹر (Low-pass filter) کا فارمولا جو آواز کو بھاری کرے گا
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def record_and_boost():
    try:
        duration = int(input("[+] کتنے سیکنڈ کی فائٹ وائس ریکارڈ کرنی ہے؟ (مثال: 15): "))
    except ValueError:
        print("[-] درست نمبر لکھیں۔")
        return

    output_filename = f"121_UltraBass_{int(time.time())}.wav"
    save_path = os.path.join("/sdcard/Download", output_filename)

    print(f"\n[!] ریکارڈنگ شروع... ہینڈز فری مائیک پاس کر کے فل لاؤڈ بولیں!")
    
    # مائیکروفون سے لائیو ڈیٹا کیپچر کرنا
    audio_data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()  
    
    print("[*] ریکارڈنگ مکمل۔ اب آواز کو الٹرا بیس اور لاؤڈ کیا جا رہا ہے...")

    # 1. آواز کو بھاری (Bass Boost) کرنا
    heavy_bass_audio = apply_lowpass_filter(audio_data, cutoff=300, fs=SAMPLE_RATE, order=2)

    # 2. والیم کو ملٹی پلائی کرنا
    boosted_audio = heavy_bass_audio * GAIN_FACTOR

    # 3. آواز کو کٹنے سے بچانے کے لیے لیمیٹر لگانا
    boosted_audio = np.clip(boosted_audio, -0.9, 0.9)

    # ڈاؤن لوڈ فولڈر میں سیو کرنا
    try:
        sf.write(save_path, boosted_audio, SAMPLE_RATE)
        print(f"\n[v] کامیابی کے ساتھ الٹرا بیس وائس سیو ہو گئی!")
        print(f"[ فائل کا نام ]: {output_filename}")
        print(f"[ لوکیشن ]: اپنے موبائل کا Download فولڈر چیک کریں۔\n")
    except Exception as e:
        print(f"[-] فائل سیو کرنے میں مسئلہ آیا: {e}")

if __name__ == "__main__":
    print("=== 121 ULTRA BASS MIC (OFFLINE TOOL) ===")
    record_and_boost()

