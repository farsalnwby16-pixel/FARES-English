from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# قاعدة بيانات الدروس والمستويات كاملة كما في الصورة
DATA = {
    "A1": [
        {"id": "a1_1", "title": "نطق الحروف 1", "order": 1, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
        {"id": "a1_2", "title": "تعلم النطق 2", "order": 2, "video": "https://www.youtube.com/embed/36yT2G228vA"},
        {"id": "a1_3", "title": "تكوين جملة 3", "order": 3, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"},
        {"id": "a1_4", "title": "Grammar 4", "order": 4, "video": "https://www.youtube.com/embed/uG_7S86t6Dk"},
        {"id": "a1_5", "title": "تأسيس 5", "order": 5, "video": "https://www.youtube.com/embed/S32Y_Jm34sY"},
        {"id": "a1_6", "title": "حروف الجر 6", "order": 6, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"}
    ],
    "A2": [
        {"id": "a2_0", "title": "A2 - Foundation Track", "order": 0, "video": "https://www.youtube.com/embed/36yT2G228vA"},
        {"id": "a2_1", "title": "تقديم نفسك 1", "order": 1, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"},
        {"id": "a2_2", "title": "استماع يومي 2", "order": 2, "video": "https://www.youtube.com/embed/uG_7S86t6Dk"},
        {"id": "a2_3", "title": "تعارف 3", "order": 3, "video": "https://www.youtube.com/embed/S32Y_Jm34sY"},
        {"id": "a2_4", "title": "محادثات يومية 4", "order": 4, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
        {"id": "a2_5", "title": "محادثة 5", "order": 5, "video": "https://www.youtube.com/embed/36yT2G228vA"}
    ],
    "B1": [
        {"id": "b1_1", "title": "ممارسة الاستماع 1", "order": 1, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"},
        {"id": "b1_2", "title": "Grammar 2", "order": 2, "video": "https://www.youtube.com/embed/uG_7S86t6Dk"},
        {"id": "b1_3", "title": "الفرق بين المضارع التام والماضي البسيط 3", "order": 3, "video": "https://www.youtube.com/embed/S32Y_Jm34sY"},
        {"id": "b1_4", "title": "حالات if الاربعة 4", "order": 4, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
        {"id": "b1_5", "title": "الاستماع 5", "order": 5, "video": "https://www.youtube.com/embed/36yT2G228vA"}
    ],
    "B2": [
        {"id": "b2_1", "title": "Shadowing 1", "order": 1, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"},
        {"id": "b2_2", "title": "محادثة سفر 2", "order": 2, "video": "https://www.youtube.com/embed/uG_7S86t6Dk"},
        {"id": "b2_3", "title": "محادثة سفر 2 - الجزء الثاني 3", "order": 3, "video": "https://www.youtube.com/embed/S32Y_Jm34sY"},
        {"id": "b2_4", "title": "مقارنة الأشياء 4", "order": 4, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
        {"id": "b2_5", "title": "استماع 5", "order": 5, "video": "https://www.youtube.com/embed/36yT2G228vA"},
        {"id": "b2_6", "title": "محادثة تسوق 6", "order": 6, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"}
    ],
    "C1": [
        {"id": "c1_1", "title": "بودكاست 1", "order": 1, "video": "https://www.youtube.com/embed/uG_7S86t6Dk"},
        {"id": "c1_2", "title": "بودكاست 2", "order": 2, "video": "https://www.youtube.com/embed/S32Y_Jm34sY"},
        {"id": "c1_3", "title": "بودكاست 3", "order": 3, "video": "https://www.youtube.com/embed/gR_4m2b_sC4"},
        {"id": "c1_4", "title": "اختبر مستواك", "order": 4, "video": "https://www.youtube.com/embed/36yT2G228vA"}
    ],
    "C2": [
        {"id": "c2_0", "title": "C2 - Foundation Track", "order": 0, "video": "https://www.youtube.com/embed/L9A1Nfl_P_w"}
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أكاديمية فارس</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { display: flex; background-color: #f8fafc; color: #1e293b; min-height: 100vh; }

        /* القائمة الجانبية الداكنة */
        .sidebar { width: 280px; background-color: #1e293b; color: white; padding: 15px; overflow-y: auto; height: 100vh; position: sticky; top: 0; flex-shrink: 0; transition: margin-right 0.3s; }
        .sidebar.hidden { margin-right: -280px; }
        
        .brand { text-align: right; font-size: 20px; font-weight: 800; padding: 10px 5px 20px; border-bottom: 1px solid #334155; margin-bottom: 15px; color: #f8fafc; }
        
        .level-header { display: flex; justify-content: space-between; align-items: center; font-size: 16px; font-weight: 800; color: #f59e0b; margin-top: 15px; margin-bottom: 8px; padding: 0 5px; }
        .add-btn { background-color: #10b981; color: white; border: none; padding: 2px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; font-weight: bold; }
        
        .lesson-link { display: block; padding: 8px 12px; color: #cbd5e1; text-decoration: none; border-radius: 6px; font-size: 13px; margin-bottom: 4px; font-weight: 600; }
        .lesson-link:hover { background-color: #334155; color: white; }
        .lesson-link.active { background-color: #2563eb; color: white; font-weight: 700; }

        /* منطقة المحتوى الرئيسية */
        .main-wrapper { flex: 1; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .top-bar { width: 100%; max-width: 800px; margin-bottom: 15px; text-align: center; }
        .toggle-btn { background-color: #1e293b; color: #f8fafc; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; }

        .content-card { width: 100%; max-width: 800px; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
        
        .lesson-title { text-align: center; font-size: 22px; font-weight: 800; color: #334155; margin-bottom: 15px; }

        /* مشغل الفيديو */
        .video-box { width: 100%; height: 400px; background: #000; border-radius: 8px; overflow: hidden; margin-bottom: 12px; }
        .video-box iframe { width: 100%; height: 100%; border: none; }
        
        .yt-direct-btn { display: block; width: 100%; text-align: center; background-color: #ef4444; color: white; text-decoration: none; padding: 8px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-bottom: 20px; }

        /* لوحة الأدمن */
        .admin-panel { background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
        .admin-title { color: #0284c7; font-size: 14px; font-weight: 800; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
        .form-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 10px; }
        .form-group label { display: block; font-size: 12px; font-weight: 700; color: #0369a1; margin-bottom: 4px; }
        .form-control { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; }
        .save-btn { width: 100%; background-color: #059669; color: white; border: none; padding: 9px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; }

        /* زر الإشارة والتنقل */
        .nav-buttons { display: flex; justify-content: space-between; gap: 10px; margin-top: 15px; }
        .nav-btn { flex: 1; padding: 10px; border: 1px solid #cbd5e1; background: white; border-radius: 6px; font-size: 13px; font-weight: bold; color: #475569; cursor: pointer; text-align: center; text-decoration: none; }

        /* نصوص الاستماع والشادوينج */
        .audio-section { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; width: 100%; max-width: 800px; text-align: center; }
        .audio-title { font-size: 16px; font-weight: 800; color: #334155; margin-bottom: 15px; }
        .audio-item { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #e2e8f0; }
        .audio-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        audio { width: 100%; max-width: 350px; height: 35px; margin-bottom: 6px; }
        .text-en { font-weight: 700; color: #1e293b; font-size: 14px; }
        .text-ar { color: #64748b; font-size: 12px; margin-top: 2px; }

        @media (max-width: 768px) {
            .video-box { height: 220px; }
            .form-grid { grid-template-columns: 1fr; }
            .sidebar { position: fixed; z-index: 100; }
        }
    </style>
</head>
<body>

    <!-- القائمة الجانبية -->
    <div class="sidebar" id="sidebar">
        <div class="brand">🎓 أكاديمية فارس</div>
        
        {% for level, lessons in data.items() %}
            <div class="level-header">
                <span>{{ level }}</span>
                <button class="add-btn">+ إضافة</button>
            </div>
            {% for lesson in lessons %}
                <a href="/lesson/{{ lesson.id }}" class="lesson-link {% if lesson.id == current_lesson.id %}active{% endif %}">
                    {{ lesson.order }} {{ lesson.title }}
                </a>
            {% endfor %}
        {% endfor %}
    </div>

    <!-- المحتوى الرئيسي -->
    <div class="main-wrapper">
        <div class="top-bar">
            <button class="toggle-btn" onclick="toggleSidebar()">📁 إخفاء / إظهار القائمة الجانبية</button>
        </div>

        <div class="content-card">
            <div class="lesson-title">{{ current_lesson.title }}</div>

            <!-- مشغل الفيديو -->
            <div class="video-box">
                <iframe src="{{ current_lesson.video }}" allowfullscreen></iframe>
            </div>
            <a href="{{ current_lesson.video }}" target="_blank" class="yt-direct-btn">🔴 مشاهدة الفيديو مباشرة على يوتيوب (لو ظهرت مشكلة في العرض)</a>

            <!-- لوحة الأدمن -->
            <div class="admin-panel">
                <div class="admin-title">⚙️ لوحة الأدمن: تعديل عنوان وترتيب ورابط الفيديو</div>
                <form action="/update/{{ current_lesson.id }}" method="POST">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>عنوان الدرس:</label>
                            <input type="text" name="title" class="form-control" value="{{ current_lesson.title }}">
                        </div>
                        <div class="form-group">
                            <label>رقم الترتيب في القائمة:</label>
                            <input type="number" name="order" class="form-control" value="{{ current_lesson.order }}">
                            <span style="font-size: 10px; color: #64748b;">1 يكون اول درس، 2 الثاني وهكذا...</span>
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 12px;">
                        <label>رابط يوتيوب الجديد (اختياري لو عايز تغيره):</label>
                        <input type="text" name="video" class="form-control" placeholder="اتركه فارغاً لو مش عايز تغير الفيديو، أو اضع الرابط الجديد">
                    </div>
                    <button type="submit" class="save-btn">حفظ التعديلات والترتيب</button>
                </form>
            </div>

            <!-- زر الانتقال بين الدروس -->
            <div class="nav-buttons">
                <a href="#" class="nav-btn">➡️ الدرس التالي</a>
                <a href="#" class="nav-btn">الدرس السابق ⬅️</a>
            </div>
        </div>

        <!-- نصوص الاستماع والشادوينج -->
        <div class="audio-section">
            <div class="audio-title">🎧 نصوص الاستماع والشادوينج</div>
            
            <div class="audio-item">
                <audio controls src=""></audio>
                <div class="text-en">.Welcome to this new custom lesson</div>
                <div class="text-ar">مرحباً بك في هذا الدرس الجديد المخصص</div>
            </div>

            <div class="audio-item">
                <audio controls src=""></audio>
                <div class="text-en">Practice speaking and listening carefully.</div>
                <div class="text-ar">تدرب على الحديث والاستماع بعناية</div>
            </div>
        </div>
    </div>

    <script>
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('hidden');
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
    current = None
    for level, lessons in DATA.items():
        for l in lessons:
            if l['id'] == lesson_id:
                current = l
                break
    if not current:
        current = DATA["C1"][3] # افتراضي على اختبر مستواك
    return render_template_string(HTML_TEMPLATE, data=DATA, current_lesson=current)

@app.route('/update/<lesson_id>', methods=['POST'])
def update_lesson(lesson_id):
    new_title = request.form.get('title')
    new_order = request.form.get('order')
    new_video = request.form.get('video')
    
    for level, lessons in DATA.items():
        for l in lessons:
            if l['id'] == lesson_id:
                if new_title: l['title'] = new_title
                if new_order: l['order'] = int(new_order)
                if new_video and new_video.strip(): l['video'] = new_video.strip()
                break
    return redirect(url_for('show_lesson', lesson_id=lesson_id))

if __name__ == '__main__':
    app.run()
