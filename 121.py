import sounddevice as sd
import numpy as np

# مائیک فائٹنگ کے لیے بہترین سیٹنگز
GAIN = 15.0 
CHANNELS = 1
RATE = 48000 # ریٹ تھوڑا بڑھا دیا تاکہ کوالٹی بہتر ہو
BLOCKSIZE = 1024 # بفر کو درمیانہ رکھا ہے تاکہ اٹکے نہ

print("==============================")
print("     121 MIC: NO-LAG MODE     ")
print("==============================")
print("Status: Powering Up...")

def callback(indata, outdata, frames, time, status):
    # آواز کو بہت تیزی سے بوسٹ کرنا
    outdata[:] = indata * GAIN

try:
    # 'low-latency' کی وجہ سے آواز اٹکے گی نہیں
    with sd.Stream(channels=CHANNELS, samplerate=RATE, blocksize=BLOCKSIZE, 
                   latency='low', callback=callback):
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\nStopped.")
except Exception as e:
    print(f"Error: {e}")

