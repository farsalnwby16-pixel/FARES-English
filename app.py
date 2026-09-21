from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'academy.db'

# إنشاء قاعدة البيانات وقراءة الدروس منها (SQLite)
def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    
    # التأكد من وجود البيانات الأساسية إذا كانت القاعدة فارغة
    cursor.execute("SELECT COUNT(*) FROM lessons")
    if cursor.fetchone()[0] == 0:
        default_lessons = [
            ("a1_1", "A1", "نطق الحروف 1", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
            ("a1_2", "A1", "تعلم النطق 2", 2, "https://www.youtube.com/embed/36yT2G228vA"),
            ("a1_3", "A1", "تكوين جملة 3", 3, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            ("a1_4", "A1", "Grammar 4", 4, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            ("a2_1", "A2", "تقديم نفسك 1", 1, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            ("b1_1", "B1", "ممارسة الاستماع 1", 1, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            ("b2_1", "B2", "Shadowing 1", 1, "https://www.youtube.com/embed/S32Y_Jm34sY"),
            ("c1_4", "C1", "اختبر مستواك", 4, "https://www.youtube.com/embed/36yT2G228vA")
        ]
        cursor.executemany("INSERT INTO lessons VALUES (?, ?, ?, ?, ?)", default_lessons)
        conn.commit()
    conn.close()

def get_all_lessons():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, level, title, order_num, video_url FROM lessons ORDER BY level, order_num")
    rows = cursor.fetchall()
    conn.close()
    
    data = {}
    for r in rows:
        level = r[1]
        if level not in data:
            data[level] = []
        data[level].append({"id": r[0], "title": r[2], "order": r[3], "video": r[4]})
    return data

init_db()

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

        /* الهيدر العلوي */
        header { background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 90; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
        .open-sidebar-btn { background: #1e293b; color: #d4af37; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }

        /* خلفية تعتيم عند فتح القائمة للموبايل */
        .backdrop { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); z-index: 998; backdrop-filter: blur(2px); }
        .backdrop.active { display: block; }

        /* القائمة الجانبية المنزلقة المضبوطة (Drawer) */
        .sidebar { position: fixed; top: 0; right: -320px; width: 290px; max-width: 85vw; height: 100vh; background-color: #1e293b; color: white; padding: 20px; overflow-y: auto; z-index: 999; transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: -5px 0 20px rgba(0,0,0,0.25); }
        .sidebar.active { right: 0; }
        
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
        .brand { font-size: 18px; font-weight: 800; color: #d4af37; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 22px; cursor: pointer; }
        
        .level-title { font-size: 13px; font-weight: 800; color: #f59e0b; margin-top: 15px; margin-bottom: 8px; display: flex; justify-content: space-between; }
        .lesson-link { display: block; padding: 9px 12px; color: #cbd5e1; text-decoration: none; border-radius: 6px; font-size: 13px; margin-bottom: 4px; font-weight: 600; background: rgba(255,255,255,0.02); }
        .lesson-link:hover, .lesson-link.active { background-color: #d4af37; color: #1e293b; font-weight: 700; }

        /* قسم الشهادة داخل القائمة */
        .cert-card { background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; padding: 15px; border-radius: 10px; margin-top: 25px; text-align: center; }
        .cert-card h4 { color: #d4af37; margin-bottom: 6px; font-size: 13px; }
        .cert-input { width: 100%; padding: 8px; margin-bottom: 10px; border-radius: 6px; border: none; text-align: center; font-size: 12px; outline: none; }
        .cert-btn { width: 100%; padding: 9px; background-color: #d4af37; color: #1e293b; font-weight: bold; border-radius: 6px; border: none; cursor: pointer; font-size: 12px; }

        /* المحتوى الرئيسي */
        .main-content { max-width: 900px; margin: 0 auto; padding: 20px 15px; }
        .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .lesson-heading { text-align: center; font-size: 20px; font-weight: 800; color: #1e293b; margin-bottom: 15px; }

        /* مشغل الفيديو */
        .video-box { width: 100%; height: 420px; background: #000; border-radius: 10px; overflow: hidden; margin-bottom: 10px; }
        .video-box iframe { width: 100%; height: 100%; border: none; }
        .yt-btn { display: block; text-align: center; background: #ef4444; color: white; text-decoration: none; padding: 8px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-bottom: 15px; }

        /* لوحة التعديل للأدمن */
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
        <button class="open-sidebar-btn" onclick="openSidebar()">☰ القائمة الجانبية</button>
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
            <div class="level-title">
                <span>المستوى {{ level }}</span>
            </div>
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

    <!-- المحتوى الرئيسي -->
    <div class="main-content">
        <div class="card">
            <div class="lesson-heading">{{ current_lesson.title }}</div>

            <div class="video-box">
                <iframe src="{{ current_lesson.video }}" allowfullscreen></iframe>
            </div>
            <a href="{{ current_lesson.video }}" target="_blank" class="yt-btn">🔴 مشاهدة الفيديو مباشرة على يوتيوب</a>

            <!-- لوحة التعديل المسجلة بـ SQLite -->
            <div class="admin-box">
                <h4>⚙️ تعديل بيانات الفيديو (محفوظة في SQLite)</h4>
                <form action="/update/{{ current_lesson.id }}" method="POST">
                    <div class="form-row">
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" value="{{ current_lesson.title }}">
                        </div>
                        <div class="form-group">
                            <label>رقم الترتيب:</label>
                            <input type="number" name="order" class="form-control" value="{{ current_lesson.order }}">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 10px;">
                        <label>رابط الفيديو الجديد (Embed / YouTube):</label>
                        <input type="text" name="video" class="form-control" value="{{ current_lesson.video }}">
                    </div>
                    <button type="submit" class="save-btn">💾 حفظ التغييرات في قاعدة البيانات SQLite</button>
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
    return redirect('/lesson/c1_4')

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
        current = {"id": "c1_4", "title": "اختبر مستواك", "order": 4, "video": "https://www.youtube.com/embed/36yT2G228vA"}
    return render_template_string(HTML_TEMPLATE, data=data, current_lesson=current)

@app.route('/update/<lesson_id>', methods=['POST'])
def update_lesson(lesson_id):
    new_title = request.form.get('title')
    new_order = request.form.get('order')
    new_video = request.form.get('video')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lessons 
        SET title = ?, order_num = ?, video_url = ?
        WHERE id = ?
    ''', (new_title, int(new_order), new_video, lesson_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

if __name__ == '__main__':
    app.run()
