from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os
import uuid

app = Flask(__name__)

BASE_DIR = '/tmp' if os.path.exists('/tmp') else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'academy.db')

def fix_youtube_url(url):
    if not url:
        return "https://www.youtube.com/embed/gR_4m2b_sC4"
    url = url.strip()
    if "youtube.com/embed/" in url:
        return url
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    return url

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id TEXT PRIMARY KEY,
            level TEXT,
            title TEXT,
            order_num INTEGER,
            video_url TEXT
        )
    ''')
    
    # التأكد من وجود الدروس دائماً
    cursor.execute("SELECT COUNT(*) FROM lessons")
    if cursor.fetchone()[0] == 0:
        default_lessons = [
            ("a1_1", "A1", "الدرس 1: التأسيس الشامل والضمائر", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
            ("a1_2", "A1", "الدرس 2: الروتين اليومي والسؤال عن الوقت", 2, "https://www.youtube.com/embed/36yT2G228vA"),
            ("a1_3", "A1", "الدرس 3: العائلة والأقارب وصفات الأشخاص", 3, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            ("a2_1", "A2", "الدرس 1: المحادثة في المطاعم والمقاهي", 1, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            ("a2_2", "A2", "الدرس 2: التسوق والتعبير عن الرأي", 2, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            ("b1_1", "B1", "الدرس 1: التخطيط للعطلات والسفر", 1, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            ("b1_2", "B1", "الدرس 2: مقابلات العمل والسيرة الذاتية", 2, "https://www.youtube.com/embed/S32Y_Jm34sY"),
            ("b2_1", "B2", "الدرس 1: اجتماعات العمل والعروض التقديمية", 1, "https://www.youtube.com/embed/S32Y_Jm34sY"),
            ("c1_1", "C1", "الدرس 1: الخطاب الأكاديمي والحجج المنطقية", 1, "https://www.youtube.com/embed/36yT2G228vA")
        ]
        cursor.executemany('''
            INSERT INTO lessons (id, level, title, order_num, video_url)
            VALUES (?, ?, ?, ?, ?)
        ''', default_lessons)

    conn.commit()
    conn.close()

def get_all_lessons():
    init_db()
    data = {"A1": [], "A2": [], "B1": [], "B2": [], "C1": [], "C2": []}
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, level, title, order_num, video_url FROM lessons ORDER BY level ASC, order_num ASC")
        rows = cursor.fetchall()
        conn.close()
        for r in rows:
            lvl = r[1]
            if lvl not in data:
                data[lvl] = []
            data[lvl].append({"id": r[0], "level": r[1], "title": r[2], "order": r[3], "video": r[4]})
    except Exception:
        pass
    return data

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fares Academy - أكاديمية فارس</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: #f1f5f9; color: #0f172a; min-height: 100vh; }
        header { background: #1e293b; color: white; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; }
        .open-sidebar-btn { background: #d4af37; color: #1e293b; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; cursor: pointer; }
        .backdrop { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 998; }
        .backdrop.active { display: block; }
        .sidebar { position: fixed; top: 0; right: -320px; width: 300px; height: 100vh; background-color: #1e293b; color: white; padding: 20px; overflow-y: auto; z-index: 999; transition: right 0.3s; }
        .sidebar.active { right: 0; }
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
        .brand { font-size: 18px; font-weight: 900; color: #d4af37; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 24px; cursor: pointer; }
        .level-title { font-size: 14px; font-weight: 800; color: #f59e0b; margin-top: 18px; margin-bottom: 8px; }
        .lesson-link { display: block; padding: 10px; color: #cbd5e1; text-decoration: none; border-radius: 8px; font-size: 12px; margin-bottom: 6px; background: rgba(255,255,255,0.03); }
        .lesson-link:hover, .lesson-link.active { background-color: #d4af37; color: #1e293b; font-weight: 800; }
        .cert-card { background: rgba(212, 175, 55, 0.15); border: 1px solid #d4af37; padding: 16px; border-radius: 12px; margin-top: 25px; text-align: center; }
        .cert-card h4 { color: #d4af37; margin-bottom: 8px; font-size: 14px; }
        .cert-input { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 6px; border: 1px solid #cbd5e1; text-align: center; }
        .cert-btn { width: 100%; padding: 10px; background-color: #d4af37; color: #1e293b; font-weight: 800; border-radius: 6px; border: none; cursor: pointer; }
        .main-content { max-width: 950px; margin: 0 auto; padding: 20px 15px; }
        .card { background: white; border-radius: 14px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; }
        .lesson-heading { text-align: center; font-size: 20px; font-weight: 900; margin-bottom: 16px; }
        .video-box { width: 100%; height: 440px; background: #000; border-radius: 12px; overflow: hidden; margin-bottom: 12px; }
        .video-box iframe { width: 100%; height: 100%; border: none; }
        .yt-btn { display: block; text-align: center; background: #ef4444; color: white; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: bold; margin-bottom: 20px; }
        .admin-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        @media (max-width: 768px) { .admin-grid { grid-template-columns: 1fr; } .video-box { height: 240px; } }
        .admin-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; }
        .form-group { margin-bottom: 10px; }
        .form-group label { display: block; font-size: 11px; font-weight: 800; margin-bottom: 4px; }
        .form-control { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; }
        .btn-green { width: 100%; background-color: #16a34a; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .btn-blue { width: 100%; background-color: #0284c7; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .btn-delete { width: 100%; background-color: #dc2626; color: white; border: none; padding: 8px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 8px; }
    </style>
</head>
<body>
    <header>
        <button class="open-sidebar-btn" onclick="openSidebar()">☰ الدروس والشهادة</button>
        <div style="font-weight: 900; color: #d4af37;">Fares Academy 🎓</div>
    </header>

    <div class="backdrop" id="backdrop" onclick="closeSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="brand">🎓 أكاديمية فارس</span>
            <button class="close-btn" onclick="closeSidebar()">✕</button>
        </div>

        {% for level, lessons in data.items() %}
            {% if lessons %}
                <div class="level-title">المستوى {{ level }} ({{ lessons|length }} دروس)</div>
                {% for lesson in lessons %}
                    <a href="/lesson/{{ lesson.id }}" class="lesson-link {% if lesson.id == current_lesson.id %}active{% endif %}">
                        {{ lesson.order }} - {{ lesson.title }}
                    </a>
                {% endfor %}
            {% endif %}
        {% endfor %}

        <div class="cert-card">
            <h4>🏅 شهادة الإتمام</h4>
            <input type="text" id="studentNameInput" class="cert-input" placeholder="اسمك الثلاثي باللغة العربية">
            <button onclick="openCertificate()" class="cert-btn">📜 عرض الشهادة</button>
        </div>
    </div>

    <div class="main-content">
        <div class="card">
            <div class="lesson-heading">مستوى {{ current_lesson.level }} | {{ current_lesson.title }}</div>
            <div class="video-box">
                <iframe src="{{ current_lesson.video }}" allowfullscreen></iframe>
            </div>
            <a href="{{ current_lesson.video }}" target="_blank" class="yt-btn">🔴 فتح الفيديو في تطبيق YouTube</a>

            <div class="admin-grid">
                <div class="admin-box">
                    <h4>➕ إضافة فيديو / درس جديد</h4>
                    <form action="/add_lesson" method="POST">
                        <div class="form-group">
                            <label>المستوى:</label>
                            <select name="level" class="form-control">
                                <option value="A1">A1</option><option value="A2">A2</option>
                                <option value="B1">B1</option><option value="B2">B2</option>
                                <option value="C1">C1</option><option value="C2">C2</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label>الترتيب:</label>
                            <input type="number" name="order" class="form-control" value="1" required>
                        </div>
                        <div class="form-group">
                            <label>رابط الفيديو:</label>
                            <input type="text" name="video" class="form-control" required>
                        </div>
                        <button type="submit" class="btn-green">➕ إضافة</button>
                    </form>
                </div>

                <div class="admin-box">
                    <h4>⚙️ تعديل الدرس الحالي</h4>
                    <form action="/update/{{ current_lesson.id }}" method="POST">
                        <div class="form-group">
                            <label>العنوان:</label>
                            <input type="text" name="title" class="form-control" value="{{ current_lesson.title }}">
                        </div>
                        <div class="form-group">
                            <label>الترتيب:</label>
                            <input type="number" name="order" class="form-control" value="{{ current_lesson.order }}">
                        </div>
                        <div class="form-group">
                            <label>الرابط:</label>
                            <input type="text" name="video" class="form-control" value="{{ current_lesson.video }}">
                        </div>
                        <button type="submit" class="btn-blue">💾 حفظ التعديلات</button>
                    </form>
                    <form action="/delete/{{ current_lesson.id }}" method="POST" onsubmit="return confirm('حذف الدرس؟')">
                        <button type="submit" class="btn-delete">🗑️ حذف الدرس</button>
                    </form>
                </div>
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
            if (!name) { alert('اكتب اسمك أولاً'); return; }
            window.location.href = '/certificate?name=' + encodeURIComponent(name);
        }
    </script>
</body>
</html>
"""

CERTIFICATE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>شهادة إتمام - أكاديمية فارس</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700;900&family=Amiri:wght@700&display=swap" rel="stylesheet">
    <style>
        body { background: #1e293b; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; font-family: 'Cairo', sans-serif; }
        .cert-container { width: 800px; background: #fff; padding: 40px; border-radius: 15px; border: 10px double #d4af37; text-align: center; }
        .cert-header { color: #1e293b; font-size: 28px; font-weight: 900; font-family: 'Amiri', serif; }
        .cert-subtitle { color: #d4af37; font-size: 16px; font-weight: 800; margin-bottom: 25px; }
        .student-name { font-size: 32px; font-weight: 900; color: #1e293b; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 20px 5px; font-family: 'Amiri', serif; }
        .print-btn { background: #d4af37; color: #1e293b; border: none; padding: 12px 25px; border-radius: 30px; font-weight: 800; cursor: pointer; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="cert-container">
        <div class="cert-header">أكاديمية فارس لتعلم الإنجليزية</div>
        <div class="cert-subtitle">Fares Academy</div>
        <p>تشهد الأكاديمية بأن الطالب:</p>
        <div class="student-name">{{ name }}</div>
        <p style="margin-top: 15px;">قد أتم المستويات التعليمية والتطبيقات المقررة بنجاح.</p>
        <button onclick="window.print()" class="print-btn">🖨️ طباعة الشهادة</button>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    data = get_all_lessons()
    for lvl in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        if data.get(lvl):
            return redirect(f'/lesson/{data[lvl][0]["id"]}')
    return redirect('/lesson/a1_1')

@app.route('/lesson/<lesson_id>')
def show_lesson(lesson_id):
    data = get_all_lessons()
    current = None
    for level, lessons in data.items():
        for l in lessons:
            if l['id'] == lesson_id:
                current = l
                break
    if not current:
        current = {"id": lesson_id, "level": "A1", "title": "درس جديد", "order": 1, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"}
    return render_template_string(MAIN_TEMPLATE, data=data, current_lesson=current)

@app.route('/add_lesson', methods=['POST'])
def add_lesson():
    level = request.form.get('level', 'A1')
    title = request.form.get('title', 'درس جديد')
    order_num = int(request.form.get('order', 1))
    video_url = fix_youtube_url(request.form.get('video', ''))
    lesson_id = f"{level.lower()}_{uuid.uuid4().hex[:6]}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lessons (id, level, title, order_num, video_url) VALUES (?, ?, ?, ?, ?)',
                   (lesson_id, level, title, order_num, video_url))
    conn.commit()
    conn.close()
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

@app.route('/update/<lesson_id>', methods=['POST'])
def update_lesson(lesson_id):
    new_title = request.form.get('title')
    new_order = int(request.form.get('order', 1))
    new_video = fix_youtube_url(request.form.get('video'))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE lessons SET title = ?, order_num = ?, video_url = ? WHERE id = ?',
                   (new_title, new_order, new_video, lesson_id))
    conn.commit()
    conn.close()
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

@app.route('/delete/<lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/certificate')
def certificate():
    name = request.args.get('name', 'طالب الأكاديمية')
    return render_template_string(CERTIFICATE_TEMPLATE, name=name)

if __name__ == '__main__':
    app.run()
