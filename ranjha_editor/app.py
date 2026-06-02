import os
import glob
from flask import Flask, request, jsonify, render_template_string
import yt_dlp
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

def search_and_download_youtube(lyrics):
    """بغیر کسی کنورژن کے یوٹیوب سے آڈیو ڈاؤن لوڈ کرنے کا فول پروف فنکشن"""
    # لیرکس سے فالتو کریکٹرز اور ایموجیز صاف کرنا
    clean_query = "".join([c for c in lyrics if c.isalnum() or c.isspace()])
    search_query = f"ytsearch1:{clean_query} audio"
    
    # پرانی عارضی فائلیں صاف کرنا
    for f in glob.glob("input_song.*") + glob.glob("song.wav"):
        try: os.remove(f)
        except: pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'input_song.%(ext)s',  # جو بھی فارمیٹ ملے اسی میں سیو کرو (m4a/webm/mp3)
        'quiet': True,
        'overwrites': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(search_query, download=True)
        
    # ڈاؤن لوڈ کی گئی فائل کا اصل نام اور ایکسٹینشن ڈھونڈنا
    downloaded_files = glob.glob("input_song.*")
    if not downloaded_files:
        raise Exception("یوٹیوب سے گانا ڈاؤن لوڈ نہیں ہو سکا!")
        
    actual_file = downloaded_files[0]
    ext = actual_file.split('.')[-1].lower()
    
    # پائتھن کے ذریعے اسے فورا WAV میں تبدیل کرنا تاکہ اسپیچ ریکگنیشن کو فائل مل جائے
    if ext == 'mp3':
        sound = AudioSegment.from_mp3(actual_file)
    elif ext == 'm4a':
        sound = AudioSegment.from_file(actual_file, format="m4a")
    elif ext == 'webm':
        sound = AudioSegment.from_file(actual_file, format="webm")
    else:
        sound = AudioSegment.from_file(actual_file)
        
    sound.export("song.wav", format="wav")
    
    # اصل ڈاؤن لوڈڈ فائل کو ڈیلیٹ کر دینا تاکہ کچرا جمع نہ ہو
    if os.path.exists(actual_file):
        os.remove(actual_file)
        
    return "song.wav"

def find_lyrics_timestamp(audio_path, lyrics_text):
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_wav(audio_path)
    
    chunk_length_ms = 15000 
    for i, chunk in enumerate(sound[::chunk_length_ms]):
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        
        with sr.AudioFile(chunk_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="ur")
                words = lyrics_text.split()
                if any(w in text or w.lower() in text.lower() for w in words):
                    os.remove(chunk_path)
                    return (i * 15)
            except:
                pass
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
            
    return 30  # اگر لیرکس گانے میں بالکل نہ ملیں تو ڈیفالٹ 30 سیکنڈ سے ویڈیو بنے گی

def make_black_screen_video(audio_path, lyrics_text, start_time, duration=12):
    video_path = "final_output.mp4"
    
    # اگر گانا چھوٹا ہے تو ہینڈل کرنا
    audio = AudioFileClip(audio_path)
    if start_time + duration > audio.duration:
        start_time = max(0, audio.duration - duration)
        
    audio_clip = audio.subclip(start_time, start_time + duration)
    background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
    
    txt_clip = TextClip(lyrics_text, fontsize=50, color='white', font='Arial', size=(900, None), method='label')
    txt_clip = txt_clip.set_position('center').set_duration(duration)
    
    video = CompositeVideoClip([background, txt_clip])
    video = video.set_audio(audio_clip)
    
    video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
    return video_path

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ur">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ranjha AI Video Maker</title>
    <style>
        body { background-color: #121212; color: white; font-family: system-ui, sans-serif; text-align: center; padding: 30px; direction: rtl; }
        .container { max-width: 500px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input[type="text"] { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #2a2a2a; color: white; font-size: 16px; text-align: center; }
        button { width: 95%; padding: 12px; background: #1DB954; color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 15px; }
        button:hover { background: #1ed760; }
        .status { margin-top: 20px; color: #1DB954; font-weight: bold; display: none; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Ranjha AI Lyrics Video Maker 🎬</h2>
        <p>اپنے لیرکس اور ایموجیز لکھیں:</p>
        
        <form id="videoForm">
            <input type="text" id="lyricsInput" placeholder="یہاں لیرکس + ایموجیز لکھیں... 🥺❤️" required>
            <button type="submit">بلیک اسکرین ویڈیو بنائیں ✨</button>
        </form>
        
        <div class="status" id="statusText">
            آٹو پروسیسنگ جاری ہے... ⏳<br>
            یوٹیوب سے گانا نکال کر لیرکس ٹائم میچ کیا جا رہا ہے...
        </div>
    </div>

    <script>
        document.getElementById('videoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const status = document.getElementById('statusText');
            status.style.display = 'block';
            
            const payload = { lyrics: document.getElementById('lyricsInput').value };
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                status.style.display = 'none';
                alert(data.message || data.error);
            } catch (err) {
                status.style.display = 'none';
                alert('کوئی ایرر آیا ہے، دوبارہ چیک کریں!');
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    lyrics = data.get('lyrics', '')
    
    if not lyrics:
        return jsonify({"error": "لیرکس لکھنا ضروری ہے!"}), 400
        
    try:
        audio_file = search_and_download_youtube(lyrics)
        start_time = find_lyrics_timestamp(audio_file, lyrics)
        video_file = make_black_screen_video(audio_file, lyrics, start_time, duration=12)
        
        if os.path.exists("song.wav"): os.remove("song.wav")
        
        return jsonify({"message": f"مبارک ہو رانجھا! ویڈیو '{video_file}' بن گئی ہے! ✨"})
    except Exception as e:
        return jsonify({"error": f"خرابی آئی: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

