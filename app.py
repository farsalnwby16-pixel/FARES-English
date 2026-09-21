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
    try:
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
        
        # قائمة كاملة بجميع الدروس والفيديوهات المعتمدة
        default_lessons = [
            # المستوى A1
            ("a1_1", "A1", "الدرس 1: التأسيس الشامل وبداية التعارف والضمائر", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
            ("a1_2", "A1", "الدرس 2: الروتين اليومي والسؤال عن الوقت", 2, "https://www.youtube.com/embed/36yT2G228vA"),
            ("a1_3", "A1", "الدرس 3: العائلة والأقارب وصفات الأشخاص", 3, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            
            # المستوى A2
            ("a2_1", "A2", "الدرس 1: إدارة الحوارات الكاملة في المطاعم والمقاهي", 1, "https://www.youtube.com/embed/L9A1Nfl_P_w"),
            ("a2_2", "A2", "الدرس 2: التسوق والمساومة والتعبير عن الآراء", 2, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            
            # المستوى B1
            ("b1_1", "B1", "الدرس 1: التخطيط للعطلات ومناقشة وجهات السفر", 1, "https://www.youtube.com/embed/uG_7S86t6Dk"),
            ("b1_2", "B1", "الدرس 2: مقابلات العمل وصياغة السيرة الذاتية", 2, "https://www.youtube.com/embed/S32Y_Jm34sY"),
            
            # المستوى B2
            ("b2_1", "B2", "الدرس 1: إدارة اجتماعات العمل وتقديم العروض التقديمية", 1, "https://www.youtube.com/embed/S32Y_Jm34sY"),
            ("b2_2", "B2", "الدرس 2: النقاشات الأكاديمية والتحليل النظري", 2, "https://www.youtube.com/embed/36yT2G228vA"),
            
            # المستوى C1
            ("c1_1", "C1", "الدرس 1: الخطاب الأكاديمي وصياغة الحجج المنطقية", 1, "https://www.youtube.com/embed/36yT2G228vA")
        ]

        for lesson in default_lessons:
            cursor.execute('''
                INSERT OR REPLACE INTO lessons (id, level, title, order_num, video_url)
                VALUES (?, ?, ?, ?, ?)
            ''', lesson)

        conn.commit()
        conn.close()
    except Exception as e:
        pass

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
        body { background-color: #f1f5f9; color: #0f172a; min-height: 100vh; overflow-x: hidden; }

        header { background: #1e293b; color: white; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 90; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .open-sidebar-btn { background: #d4af37; color: #1e293b; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; }

        .backdrop { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 998; backdrop-filter: blur(3px); }
        .backdrop.active { display: block; }

        .sidebar { position: fixed; top: 0; right: -320px; width: 300px; max-width: 85vw; height: 100vh; background-color: #1e293b; color: white; padding: 20px; overflow-y: auto; z-index: 999; transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: -5px 0 25px rgba(0,0,0,0.3); }
        .sidebar.active { right: 0; }
        
        .sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
        .brand { font-size: 18px; font-weight: 900; color: #d4af37; }
        .close-btn { background: none; border: none; color: #94a3b8; font-size: 24px; cursor: pointer; }
        
        .level-title { font-size: 14px; font-weight: 800; color: #f59e0b; margin-top: 18px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; }
        .lesson-link { display: block; padding: 10px 12px; color: #cbd5e1; text-decoration: none; border-radius: 8px; font-size: 12px; margin-bottom: 6px; font-weight: 600; background: rgba(255,255,255,0.03); transition: all 0.2s; }
        .lesson-link:hover, .lesson-link.active { background-color: #d4af37; color: #1e293b; font-weight: 800; transform: translateX(-3px); }

        .cert-card { background: linear-gradient(135deg, rgba(212, 175, 55, 0.15), rgba(245, 158, 11, 0.05)); border: 1px solid #d4af37; padding: 16px; border-radius: 12px; margin-top: 25px; text-align: center; }
        .cert-card h4 { color: #d4af37; margin-bottom: 8px; font-size: 14px; font-weight: 800; }
        .cert-input { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 6px; border: 1px solid #cbd5e1; text-align: center; font-size: 12px; font-weight: 700; outline: none; }
        .cert-btn { width: 100%; padding: 10px; background-color: #d4af37; color: #1e293b; font-weight: 800; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; transition: 0.2s; }
        .cert-btn:hover { background-color: #f59e0b; }

        .main-content { max-width: 950px; margin: 0 auto; padding: 20px 15px; }
        .card { background: white; border-radius: 14px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; border: 1px solid #e2e8f0; }
        .lesson-heading { text-align: center; font-size: 20px; font-weight: 900; color: #1e293b; margin-bottom: 16px; }

        .video-box { width: 100%; height: 440px; background: #000; border-radius: 12px; overflow: hidden; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .video-box iframe { width: 100%; height: 100%; border: none; }
        .yt-btn { display: block; text-align: center; background: #ef4444; color: white; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: bold; margin-bottom: 20px; }

        .admin-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px; }
        @media (max-width: 768px) {
            .admin-grid { grid-template-columns: 1fr; }
            .video-box { height: 240px; }
        }

        .admin-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; }
        .admin-box.add-box { background: #f0fdf4; border-color: #86efac; }
        .admin-box h4 { font-size: 14px; margin-bottom: 12px; font-weight: 800; }
        .admin-box.add-box h4 { color: #166534; }
        .admin-box.edit-box h4 { color: #0369a1; }

        .form-group { margin-bottom: 10px; }
        .form-group label { display: block; font-size: 11px; font-weight: 800; margin-bottom: 4px; color: #334155; }
        .form-control { width: 100%; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 12px; outline: none; background: white; }
        
        .btn-green { width: 100%; background-color: #16a34a; color: white; border: none; padding: 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .btn-blue { width: 100%; background-color: #0284c7; color: white; border: none; padding: 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .btn-delete { width: 100%; background-color: #dc2626; color: white; border: none; padding: 8px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer; margin-top: 8px; }
    </style>
</head>
<body>

    <header>
        <button class="open-sidebar-btn" onclick="openSidebar()">☰ القائمة الجانبية والشهادة</button>
        <div style="font-weight: 900; color: #d4af37; font-size: 16px;">Fares Academy 🎓</div>
    </header>

    <div class="backdrop" id="backdrop" onclick="closeSidebar()"></div>

    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="brand">🎓 أكاديمية فارس</span>
            <button class="close-btn" onclick="closeSidebar()">✕</button>
        </div>

        {% for level, lessons in data.items() %}
            {% if lessons %}
                <div class="level-title">
                    <span>المستوى {{ level }}</span>
                    <span style="font-size: 10px; background: rgba(212,175,55,0.2); padding: 2px 6px; border-radius: 10px; color: #d4af37;">{{ lessons|length }} دروس</span>
                </div>
                {% for lesson in lessons %}
                    <a href="/lesson/{{ lesson.id }}" class="lesson-link {% if lesson.id == current_lesson.id %}active{% endif %}">
                        {{ lesson.order }} - {{ lesson.title }}
                    </a>
                {% endfor %}
            {% endif %}
        {% endfor %}

        <div class="cert-card">
            <h4>🏅 شهادة الإتمام الرسمية</h4>
            <p style="font-size: 11px; color: #cbd5e1; margin-bottom: 10px;">أدخل اسمك كما تحب أن يظهر في الشهادة:</p>
            <input type="text" id="studentNameInput" class="cert-input" placeholder="اسمك الثلاثي باللغة العربية">
            <button onclick="openCertificate()" class="cert-btn">📜 عرض وإصدار الشهادة</button>
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
                
                <div class="admin-box add-box">
                    <h4>➕ إضافة فيديو / درس جديد لأي مستوى</h4>
                    <form action="/add_lesson" method="POST">
                        <div class="form-group">
                            <label>اختر المستوى المراد إضافته له:</label>
                            <select name="level" class="form-control">
                                <option value="A1">المستوى A1</option>
                                <option value="A2">المستوى A2</option>
                                <option value="B1">المستوى B1</option>
                                <option value="B2">المستوى B2</option>
                                <option value="C1">المستوى C1</option>
                                <option value="C2">المستوى C2</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" placeholder="مثال: الدرس 3: القواعد الأساسية" required>
                        </div>
                        <div class="form-group">
                            <label>رقم الترتيب:</label>
                            <input type="number" name="order" class="form-control" value="1" required>
                        </div>
                        <div class="form-group">
                            <label>رابط يوتيوب (العادي أو Embed):</label>
                            <input type="text" name="video" class="form-control" placeholder="https://www.youtube.com/watch?v=..." required>
                        </div>
                        <button type="submit" class="btn-green">➕ إضافة الدرس للمستوى</button>
                    </form>
                </div>

                <div class="admin-box edit-box">
                    <h4>⚙️ تعديل الدرس الحالي ({{ current_lesson.title }})</h4>
                    <form action="/update/{{ current_lesson.id }}" method="POST">
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" value="{{ current_lesson.title }}">
                        </div>
                        <div class="form-group">
                            <label>رقم الترتيب في المستوى:</label>
                            <input type="number" name="order" class="form-control" value="{{ current_lesson.order }}">
                        </div>
                        <div class="form-group">
                            <label>رابط فيديو يوتيوب:</label>
                            <input type="text" name="video" class="form-control" value="{{ current_lesson.video }}">
                        </div>
                        <button type="submit" class="btn-blue">💾 حفظ التعديلات</button>
                    </form>
                    <form action="/delete/{{ current_lesson.id }}" method="POST" onsubmit="return confirm('هل أنت تأكد من حذف هذا الدرس؟')">
                        <button type="submit" class="btn-delete">🗑️ حذف هذا الدرس</button>
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
            if (!name) { alert('الرجاء كتابة الاسم أولاً لإصداره على الشهادة!'); return; }
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>شهادة إتمام - أكاديمية فارس</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Amiri:wght@700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #1e293b; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; font-family: 'Cairo', sans-serif; }
        
        .cert-container { width: 850px; background: #fff; padding: 40px; border-radius: 15px; border: 12px double #d4af37; box-shadow: 0 10px 40px rgba(0,0,0,0.5); position: relative; text-align: center; }
        
        .cert-header { color: #1e293b; font-size: 28px; font-weight: 900; margin-bottom: 5px; font-family: 'Amiri', serif; }
        .cert-subtitle { color: #d4af37; font-size: 16px; font-weight: 800; letter-spacing: 2px; margin-bottom: 25px; text-transform: uppercase; }
        
        .cert-body { margin: 25px 0; line-height: 1.8; color: #334155; }
        .student-name { font-size: 32px; font-weight: 900; color: #1e293b; margin: 15px 0; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 30px 5px 30px; font-family: 'Amiri', serif; }
        
        .badge { width: 90px; height: 90px; background: #d4af37; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 40px; margin: 20px auto; box-shadow: 0 4px 10px rgba(212,175,55,0.4); }
        
        .cert-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
        .signature { font-size: 14px; font-weight: 800; color: #1e293b; }
        
        .no-print-bar { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; z-index: 999; }
        .print-btn { background: #d4af37; color: #1e293b; border: none; padding: 12px 25px; border-radius: 30px; font-weight: 800; font-size: 14px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .back-btn { background: #334155; color: white; border: none; padding: 12px 25px; border-radius: 30px; font-weight: 800; font-size: 14px; cursor: pointer; text-decoration: none; }

        @media print {
            body { background: white; padding: 0; }
            .cert-container { border: 10px double #d4af37; box-shadow: none; width: 100%; }
            .no-print-bar { display: none !important; }
        }
    </style>
</head>
<body>

    <div class="cert-container">
        <div class="cert-header">أكاديمية فارس لتعلم الإنجليزية</div>
        <div class="cert-subtitle">Fares Academy for English Learning</div>
        
        <div class="badge">🏅</div>

        <div class="cert-body">
            <p style="font-size: 16px;">تشهد إدارة الأكاديمية بأن الطالب / الطالبة:</p>
            <div class="student-name">{{ name }}</div>
            <p style="font-size: 15px; max-width: 650px; margin: 15px auto;">
                قد أتم بنجاح كافة المستويات التعليمية والتطبيقات التفاعلية المقررة واجتاز اختبارات الكفاءة والطلاقة بنجاح بتقدير <strong>ممتاز (Excellent)</strong>.
            </p>
        </div>

        <div class="cert-footer">
            <div class="signature">
                <p style="color: #94a3b8; font-size: 11px;">اعتماد الأكاديمية</p>
                <p>إدارة أكاديمية فارس 🎓</p>
            </div>
            <div class="signature">
                <p style="color: #94a3b8; font-size: 11px;">كود الشهادة</p>
                <p style="font-family: monospace; color: #d4af37;">FA-{{ cert_id }}</p>
            </div>
        </div>
    </div>

    <div class="no-print-bar">
        <button onclick="window.print()" class="print-btn">🖨️ طباعة الشهادة / حفظ PDF</button>
        <a href="/" class="back-btn">⬅️ العودة للمنصة</a>
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
    raw_video = request.form.get('video', '')
    video_url = fix_youtube_url(raw_video)
    lesson_id = f"{level.lower()}_{uuid.uuid4().hex[:6]}"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (id, level, title, order_num, video_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (lesson_id, level, title, order_num, video_url))
        conn.commit()
        conn.close()
    except Exception:
        pass
    
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

@app.route('/update/<lesson_id>', methods=['POST'])
def update_lesson(lesson_id):
    new_title = request.form.get('title')
    new_order = int(request.form.get('order', 1))
    new_video = fix_youtube_url(request.form.get('video'))
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE lessons 
            SET title = ?, order_num = ?, video_url = ?
            WHERE id = ?
        ''', (new_title, new_order, new_video, lesson_id))
        conn.commit()
        conn.close()
    except Exception:
        pass
    
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

@app.route('/delete/<lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass
    return redirect('/')

@app.route('/certificate')
def certificate():
    name = request.args.get('name', 'طالب الأكاديمية')
    cert_id = uuid.uuid4().hex[:8].upper()
    return render_template_string(CERTIFICATE_TEMPLATE, name=name, cert_id=cert_id)

if __name__ == '__main__':
    app.run()
