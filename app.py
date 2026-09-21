import sqlite3
import json
import os
import hashlib
import re
from flask import Flask, render_template, request, send_file, redirect, url_for
from gtts import gTTS

app = Flask(__name__)
CACHE_DIR = "audio_cache"
DB_NAME = "fares_english.db"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def extract_youtube_id(url_or_id):
    if not url_or_id:
        return "jNQXAC9IVRw"
    url_or_id = url_or_id.strip()
    youtube_regex = r'(?:v=|\/([0-9A-Za-z_-]{11}).*|youtu\.be\/|embed\/)([0-9A-Za-z_-]{11})'
    match = re.search(youtube_regex, url_or_id)
    if match:
        return match.group(1) or match.group(2)
    if len(url_or_id) == 11:
        return url_or_id
    return "jNQXAC9IVRw"

@app.route('/tts')
def tts():
    text = request.args.get('text', '').strip()
    if not text:
        return "No text", 400
    
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    file_path = os.path.join(CACHE_DIR, f"{text_hash}.mp3")

    if not os.path.exists(file_path):
        tts_obj = gTTS(text=text, lang='en', slow=False)
        tts_obj.save(file_path)

    return send_file(file_path, mimetype='audio/mpeg')

@app.route('/update_fares_video', methods=['POST'])
def update_fares_video():
    lesson_id = request.form.get('lesson_id')
    raw_input = request.form.get('youtube_url', '')
    new_title = request.form.get('lesson_title', '')
    new_order = request.form.get('lesson_order', 1, type=int)
    clean_id = extract_youtube_id(raw_input) if raw_input else None
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if raw_input:
        cursor.execute('UPDATE lessons SET youtube_id = ?, title = ?, lesson_order = ? WHERE id = ?', (clean_id, new_title, new_order, lesson_id))
    else:
        cursor.execute('UPDATE lessons SET title = ?, lesson_order = ? WHERE id = ?', (new_title, new_order, lesson_id))
        
    conn.commit()
    conn.close()
    
    return redirect(url_for('home', lesson_id=lesson_id))

@app.route('/add_lesson', methods=['GET', 'POST'])
def add_lesson():
    level = request.args.get('level', 'A1')
    if request.method == 'POST':
        level = request.form.get('level')
        title = request.form.get('title')
        raw_url = request.form.get('youtube_url')
        description = request.form.get('description', '')
        lesson_order = request.form.get('lesson_order', 1, type=int)
        
        youtube_id = extract_youtube_id(raw_url)
        
        default_transcript = [
            {"en": "Welcome to this new custom lesson.", "ar": "مرحباً بك في هذا الدرس الجديد المخصص."},
            {"en": "Practice speaking and listening carefully.", "ar": "تدرب على التحدث والاستماع بعناية."}
        ]
        default_templates = [
            {"phrase": "Keep going forward", "meaning": "استمر في التقدم", "example": "Always keep going forward."}
        ]
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO lessons (level, episode_num, title, youtube_id, description, transcript, templates, lesson_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (level, 1, title, youtube_id, description, json.dumps(default_transcript), json.dumps(default_templates), lesson_order))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return redirect(url_for('home', lesson_id=new_id))
        
    return render_template('add_lesson.html', level=level)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # التأكد من وجود الجدول وإنشاء عمود الترتيب (lesson_order) لو مش موجود بدون مسح القديم
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            episode_num INTEGER NOT NULL,
            title TEXT NOT NULL,
            youtube_id TEXT NOT NULL,
            description TEXT,
            transcript TEXT NOT NULL,
            templates TEXT NOT NULL
        )
    ''')
    
    # فحص هل عمود lesson_order موجود ولا لأ، ولو مش موجود بنضيفه بأمان
    cursor.execute("PRAGMA table_info(lessons)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'lesson_order' not in columns:
        cursor.execute("ALTER TABLE lessons ADD COLUMN lesson_order INTEGER DEFAULT 1")
        conn.commit()

    cursor.execute('SELECT COUNT(*) FROM lessons')
    count = cursor.fetchone()[0]

    if count == 0:
        default_transcript = [
            {"en": "Welcome to your selected lesson in Fares English Academy.", "ar": "مرحباً بك في الدرس المختار في أكاديمية فارس."},
            {"en": "You can now add and manage any number of custom lessons easily.", "ar": "يمكنك الآن إضافة وإدارة أي عدد من الدروس بسهولة."}
        ]
        default_templates = [
            {"phrase": "Practice makes perfect", "meaning": "الممارسة تقود للإتقان", "example": "Always practice speaking English."}
        ]

        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        for lvl in levels:
            title = f"{lvl} - Foundation Track"
            cursor.execute('''
                INSERT INTO lessons (level, episode_num, title, youtube_id, description, transcript, templates, lesson_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (lvl, 1, title, "jNQXAC9IVRw", f"هذا هو الدرس الأول للمستوى {lvl}.", json.dumps(default_transcript), json.dumps(default_templates), 1))
        
        conn.commit()
        
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # الترتيب تصاعدياً حسب المستوى ثم حسب رقم الـ lesson_order ثم الـ id
    cursor.execute('SELECT id, level, episode_num, title, lesson_order FROM lessons ORDER BY level ASC, lesson_order ASC, id ASC')
    all_lessons = cursor.fetchall()
    
    level_structure = {}
    lesson_ids = []
    for l in all_lessons:
        lid, lvl, ep, title, lorder = l
        lesson_ids.append(lid)
        if lvl not in level_structure:
            level_structure[lvl] = []
        level_structure[lvl].append({"id": lid, "title": title, "ep": ep, "order": lorder})

    selected_id = request.args.get('lesson_id', type=int)
    if not selected_id and lesson_ids:
        selected_id = lesson_ids[0]

    cursor.execute('SELECT id, level, episode_num, title, youtube_id, description, transcript, templates, lesson_order FROM lessons WHERE id = ?', (selected_id,))
    row = cursor.fetchone()
    conn.close()

    current_lesson = None
    prev_id, next_id = None, None

    if row:
        current_lesson = {
            "id": row[0],
            "level": row[1],
            "episode_num": row[2],
            "title": row[3],
            "youtube_id": row[4],
            "description": row[5],
            "transcript": json.loads(row[6]),
            "templates": json.loads(row[7]),
            "order": row[8]
        }
        idx = lesson_ids.index(selected_id)
        if idx > 0:
            prev_id = lesson_ids[idx - 1]
        if idx < len(lesson_ids) - 1:
            next_id = lesson_ids[idx + 1]

    return render_template('index.html', 
                           level_structure=level_structure, 
                           current_lesson=current_lesson,
                           prev_id=prev_id, 
                           next_id=next_id)

if __name__ == '__main__':
    print("--- Fares English Academy v16 (Custom Lesson Ordering Mode) Started ---")
    app.run(host='0.0.0.0', port=5000)

# --- Certificate Route ---
from flask import request, render_template_string
from datetime import datetime

@app.route('/certificate')
def certificate():
    student_name = request.args.get('name', 'الطالب المتميز')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    cert_html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>شهادة إتمام - Fares English Academy</title>
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Cairo', sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
            .certificate-container { width: 850px; padding: 40px; background: #fff; border: 12px solid #1a2a3a; outline: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.15); text-align: center; position: relative; box-sizing: border-box; border-radius: 8px; }
            .badge { width: 70px; height: 70px; background: #d4af37; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 32px; }
            h1 { font-family: 'Amiri', serif; font-size: 40px; color: #1a2a3a; margin-bottom: 5px; }
            h2 { font-size: 20px; color: #d4af37; margin-top: 0; letter-spacing: 1px; }
            p { font-size: 18px; color: #555; margin: 15px 0; }
            .student-name { font-size: 34px; color: #1a2a3a; font-weight: 900; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 25px 5px; margin: 15px 0; }
            .footer-info { margin-top: 40px; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; }
            .signature { font-weight: bold; color: #333; font-size: 16px; }
            .btn-print { margin-top: 25px; padding: 12px 28px; background-color: #1a2a3a; color: #fff; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-family: 'Cairo', sans-serif; font-weight: bold; }
            .btn-print:hover { background-color: #d4af37; }
            @media print { .btn-print { display: none; } body { background: white; padding: 0; } .certificate-container { box-shadow: none; width: 100%; } }
        </style>
    </head>
    <body>
        <div class="certificate-container">
            <div class="badge">🎓</div>
            <h2>Fares English Academy</h2>
            <h1>شهادة إتمام دورة تدريبية</h1>
            <p>تتشرف الأكاديمية بمنح هذه الشهادة للـطالب/ـة:</p>
            <div class="student-name">{{ student_name }}</div>
            <p>وذلك لإتمامه كافة الدروس والأجزاء التدريبية بنجاح.</p>
            <div class="footer-info">
                <div class="signature">التاريخ: {{ date }}</div>
                <div class="signature">إدارة أكاديمية فارس</div>
            </div>
            <button class="btn-print" onclick="window.print()">🖨️ طباعة / حفظ الشهادة PDF</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(cert_html, student_name=student_name, date=current_date)

# --- Certificate Route ---
from flask import request, render_template_string
from datetime import datetime

@app.route('/certificate')
def certificate():
    student_name = request.args.get('name', 'الطالب المتميز')
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    cert_html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>شهادة إتمام - Fares English Academy</title>
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Cairo', sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
            .certificate-container { width: 850px; padding: 40px; background: #fff; border: 12px solid #1a2a3a; outline: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.15); text-align: center; position: relative; box-sizing: border-box; border-radius: 8px; }
            .badge { width: 70px; height: 70px; background: #d4af37; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 32px; }
            h1 { font-family: 'Amiri', serif; font-size: 40px; color: #1a2a3a; margin-bottom: 5px; }
            h2 { font-size: 20px; color: #d4af37; margin-top: 0; letter-spacing: 1px; }
            p { font-size: 18px; color: #555; margin: 15px 0; }
            .student-name { font-size: 34px; color: #1a2a3a; font-weight: 900; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 25px 5px; margin: 15px 0; }
            .footer-info { margin-top: 40px; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; }
            .signature { font-weight: bold; color: #333; font-size: 16px; }
            .btn-print { margin-top: 25px; padding: 12px 28px; background-color: #1a2a3a; color: #fff; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-family: 'Cairo', sans-serif; font-weight: bold; }
            .btn-print:hover { background-color: #d4af37; }
            @media print { .btn-print { display: none; } body { background: white; padding: 0; } .certificate-container { box-shadow: none; width: 100%; } }
        </style>
    </head>
    <body>
        <div class="certificate-container">
            <div class="badge">🎓</div>
            <h2>Fares English Academy</h2>
            <h1>شهادة إتمام دورة تدريبية</h1>
            <p>تتشرف الأكاديمية بمنح هذه الشهادة للـطالب/ـة:</p>
            <div class="student-name">{{ student_name }}</div>
            <p>وذلك لإتمامه كافة الدروس والأجزاء التدريبية بنجاح.</p>
            <div class="footer-info">
                <div class="signature">التاريخ: {{ date }}</div>
                <div class="signature">إدارة أكاديمية فارس</div>
            </div>
            <button class="btn-print" onclick="window.print()">🖨️ طباعة / حفظ الشهادة PDF</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(cert_html, student_name=student_name, date=current_date)
