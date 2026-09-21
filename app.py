from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# دالة البحث الآمن عن قاعدة البيانات وقراءة الدروس القديمة
def get_safe_lessons():
    db_candidates = [
        'academy_v14.db', 'fares_english_v13.db', 'fares_english_v10.db',
        'academy_v13.db', 'platform.db', 'academy.db'
    ]
    
    selected_db = None
    for db_name in db_candidates:
        path = os.path.join(BASE_DIR, db_name)
        if os.path.exists(path):
            selected_db = path
            break
            
    if not selected_db:
        selected_db = os.path.join(BASE_DIR, 'academy.db')

    try:
        conn = sqlite3.connect(selected_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
        
        if not tables:
            conn.close()
            return get_default_lessons(), selected_db

        table = 'lessons' if 'lessons' in tables else tables[0]
        
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        conn.close()
        
        data = {}
        for r in rows:
            if len(r) >= 5:
                l_id, level, title, order_num, video = str(r[0]), str(r[1]), str(r[2]), r[3], str(r[4])
            elif len(r) == 4:
                l_id, level, title, video = str(r[0]), str(r[1]), str(r[2]), str(r[3])
                order_num = 1
            else:
                continue
                
            if level not in data:
                data[level] = []
            data[level].append({
                "id": l_id,
                "title": title,
                "order": order_num,
                "video": video
            })
            
        if data:
            return data, selected_db
    except Exception:
        pass

    return get_default_lessons(), selected_db

def get_default_lessons():
    return {
        "A1": [
            {"id": "a1_1", "title": "نطق الحروف 1", "order": 1, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
            {"id": "a1_2", "title": "تعلم النطق 2", "order": 2, "video": "https://www.youtube.com/embed/36yT2G228vA"},
            {"id": "a1_3", "title": "تكوين جملة 3", "order": 3, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"}
        ],
        "C1": [
            {"id": "c1_4", "title": "اختبر مستواك", "order": 4, "video": "https://www.youtube.com/embed/36yT2G228vA"}
        ]
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fares Academy - أكاديمية فارس</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #f8fafc; color: #1e293b; min-height: 100vh; overflow-x: hidden; }

        header { background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 90; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
        .open-sidebar-btn { background: #1e293b; color: #d4af37; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }

        .backdrop { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); z-index: 998; backdrop-filter: blur(2px); }
        .backdrop.active { display: block; }

        /* القائمة الجانبية المضبوطة (عرض مناسب جداً لا يغطي الشاشة) */
        .sidebar { position: fixed; top: 0; right: -320px; width: 280px; max-width: 80vw; height: 100vh; background-color: #1e293b; color: white; padding: 20px; overflow-y: auto; z-index: 999; transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: -5px 0 20px rgba(0,0,0,0.25); }
        .sidebar.active { right: 0; }
        
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
        .brand { font-size: 18px; font-weight: 800; color: #d4af37; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 22px; cursor: pointer; }
        
        .level-title { font-size: 13px; font-weight: 800; color: #f59e0b; margin-top: 15px; margin-bottom: 8px; }
        .lesson-link { display: block; padding: 9px 12px; color: #cbd5e1; text-decoration: none; border-radius: 6px; font-size: 13px; margin-bottom: 4px; font-weight: 600; background: rgba(255,255,255,0.02); }
        .lesson-link:hover, .lesson-link.active { background-color: #d4af37; color: #1e293b; font-weight: 700; }

        .cert-card { background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-top: 25px; text-align: center; }
        .cert-card h4 { color: #d4af37; margin-bottom: 6px; font-size: 13px; }
        .cert-input { width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 6px; border: none; text-align: center; font-size: 12px; outline: none; }
        .cert-btn { width: 100%; padding: 9px; background-color: #d4af37; color: #1e293b; font-weight: bold; border-radius: 6px; border: none; cursor: pointer; font-size: 12px; }

        .main-content { max-width: 900px; margin: 0 auto; padding: 20px 15px; }
        .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .lesson-heading { text-align: center; font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 15px; }

        .video-box { width: 100%; height: 420px; background: #000; border-radius: 10px; overflow: hidden; margin-bottom: 10px; }
        .video-box iframe { width: 100%; height: 100%; border: none; }
        .yt-btn { display: block; text-align: center; background: #ef4444; color: white; text-decoration: none; padding: 8px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-bottom: 15px; }

        .admin-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 15px; }
        .admin-box h4 { color: #0284c7; font-size: 13px; margin-bottom: 10px; font-weight: 800; }
        .form-row { display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 140px; }
        .form-group label { display: block; font-size: 11px; font-weight: bold; color: #0369a1; margin-bottom: 4px; }
        .form-control { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; outline: none; }
        .save-btn { width: 100%; background-color: #059669; color: white; border: none; padding: 9px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; }

        @media (max-width: 768px) {
            .video-box { height: 230px; }
        }
    </style>
</head>
<body>

    <header>
        <button class="open-sidebar-btn" onclick="openSidebar()">📁 إخفاء / إظهار القائمة الجانبية</button>
        <div style="font-weight: 800; color: #1e293b; font-size: 15px;">Fares Academy 🎓</div>
    </header>

    <div class="backdrop" id="backdrop" onclick="closeSidebar()"></div>

    <!-- القائمة الجانبية -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="brand">🎓 أكاديمية فارس</span>
            <button class="close-btn" onclick="closeSidebar()">✕</button>
        </div>

        {% for level, lessons in data.items() %}
            <div class="level-title">المستوى {{ level }}</div>
            {% for lesson in lessons %}
                <a href="/lesson/{{ lesson.id }}" class="lesson-link {% if lesson.id == current_lesson.id %}active{% endif %}">
                    {{ lesson.order }} - {{ lesson.title }}
                </a>
            {% endfor %}
        {% endfor %}

        <div class="cert-card">
            <h4>🏅 شهادة الإتمام الرسمية</h4>
            <input type="text" id="studentNameInput" class="cert-input" placeholder="اكتب اسمك الثلاثي">
            <button onclick="openCertificate()" class="cert-btn">📜 إصدار الشهادة</button>
        </div>
    </div>

    <div class="main-content">
        <div class="card">
            <div class="lesson-heading">{{ current_lesson.title }}</div>

            <div class="video-box">
                <iframe src="{{ current_lesson.video }}" allowfullscreen></iframe>
            </div>
            <a href="{{ current_lesson.video }}" target="_blank" class="yt-btn">🔴 مشاهدة الفيديو مباشرة على يوتيوب (لو ظهرت مشكلة في العرض)</a>

            <div class="admin-box">
                <h4>⚙️ لوحة الأدمن: تعديل عنوان وترتيب ورابط الفيديو</h4>
                <form action="/update/{{ current_lesson.id }}" method="POST">
                    <div class="form-row">
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" value="{{ current_lesson.title }}">
                        </div>
                        <div class="form-group">
                            <label>رقم الترتيب في القائمة:</label>
                            <input type="number" name="order" class="form-control" value="{{ current_lesson.order }}">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 10px;">
                        <label>رابط يوتيوب الجديد (اختياري):</label>
                        <input type="text" name="video" class="form-control" value="{{ current_lesson.video }}">
                    </div>
                    <button type="submit" class="save-btn">حفظ التعديلات والترتيب</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function openSidebar() {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('backdrop').classList.add('active');
        }

        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('backdrop').classList.remove('active');
        }

        function openCertificate() {
            let name = document.getElementById('studentNameInput').value.trim();
            if (!name) { alert('ادخل اسمك أولاً!'); return; }
            window.location.href = '/certificate?name=' + encodeURIComponent(name);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    data, db_path = get_safe_lessons()
    first_id = 'c1_4'
    for lvl, llist in data.items():
        if llist:
            first_id = llist[0]['id']
            break
    return redirect(f'/lesson/{first_id}')

@app.route('/lesson/<lesson_id>')
def show_lesson(lesson_id):
    data, db_path = get_safe_lessons()
    current = None
    for level, lessons in data.items():
        for l in lessons:
            if l['id'] == lesson_id:
                current = l
                break
    if not current:
        current = {"id": lesson_id, "title": "درس تعليمي", "order": 1, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"}
    return render_template_string(HTML_TEMPLATE, data=data, current_lesson=current)

@app.route('/update/<lesson_id>', methods=['POST'])
def update_lesson(lesson_id):
    new_title = request.form.get('title')
    new_order = request.form.get('order')
    new_video = request.form.get('video')
    
    data, db_path = get_safe_lessons()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
        if tables:
            table = 'lessons' if 'lessons' in tables else tables[0]
            cursor.execute(f'''
                UPDATE {table} 
                SET title = ?, video_url = ?
                WHERE id = ?
            ''', (new_title, new_video, lesson_id))
            conn.commit()
        conn.close()
    except Exception:
        pass
        
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

if __name__ == '__main__':
    app.run()
