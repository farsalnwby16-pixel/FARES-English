import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Lesson(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    level = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    youtube_url = db.Column(db.String(300), nullable=False)

DEFAULT_LESSONS = [
    # مستوى A1
    ("a1_1", "A1", "الدرس 1: نطق الحروف والأصوات الأساسية (Phonics)", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("a1_2", "A1", "الدرس 2: تكوين الجملة الإنجليزية الصحيحة", 2, "https://www.youtube.com/embed/36yT2G228vA"),
    ("a1_3", "A1", "الدرس 3: محادثات التحية والتعارف اليومي", 3, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("a1_4", "A1", "الدرس 4: قواعد الضمائر وفعل الكينونة To Be", 4, "https://www.youtube.com/embed/36yT2G228vA"),
    ("a1_5", "A1", "الدرس 5: أهم 100 كلمة شائعة لبداية قوية", 5, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("a1_6", "A1", "الدرس 6: الروتين اليومي والسؤال عن الوقت", 6, "https://www.youtube.com/embed/36yT2G228vA"),

    # مستوى A2
    ("a2_1", "A2", "الدرس 1: الماضي البسيط وذكريات الطفولة", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("a2_2", "A2", "الدرس 2: خطط المستقبل واستخدام Going to", 2, "https://www.youtube.com/embed/36yT2G228vA"),
    ("a2_3", "A2", "الدرس 3: محادثات التسوق والشراء بطلاقة", 3, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("a2_4", "A2", "الدرس 4: التحدث عن الهوايات وأوقات الفراغ", 4, "https://www.youtube.com/embed/36yT2G228vA"),
    ("a2_5", "A2", "الدرس 5: وصف الأشخاص والمقارنات", 5, "https://www.youtube.com/embed/36yT2G228vA"),
    ("a2_6", "A2", "الدرس 6: الاستماع اليومي وقصص المبتدئين", 6, "https://www.youtube.com/embed/36yT2G228vA"),

    # مستوى B1
    ("b1_1", "B1", "الدرس 1: المضارع التام (Present Perfect)", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b1_2", "B1", "الدرس 2: الجمل الشرطية (If Conditionals)", 2, "https://www.youtube.com/embed/36yT2G228vA"),
    ("b1_3", "B1", "الدرس 3: التعبير عن الرأي والنقاشات الحية", 3, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b1_4", "B1", "الدرس 4: إنجليزية العمل والمقابلات الشخصية", 4, "https://www.youtube.com/embed/36yT2G228vA"),
    ("b1_5", "B1", "الدرس 5: السفر وحجز الفنادق في المطار", 5, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b1_6", "B1", "الدرس 6: ممارسة الاستماع المتقدم قليلاً", 6, "https://www.youtube.com/embed/36yT2G228vA"),

    # مستوى B2
    ("b2_1", "B2", "الدرس 1: المجهول في اللغة (Passive Voice)", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b2_2", "B2", "الدرس 2: العبارات الاصطلاحية (Phrasal Verbs)", 2, "https://www.youtube.com/embed/36yT2G228vA"),
    ("b2_3", "B2", "الدرس 3: إدارة النقاشات المعقدة", 3, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b2_4", "B2", "الدرس 4: إنجليزية الأعمال وكتابة الإيميلات", 4, "https://www.youtube.com/embed/36yT2G228vA"),
    ("b2_5", "B2", "الدرس 5: تقنية Shadowing لفهم الأفلام", 5, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("b2_6", "B2", "الدرس 6: سرد القصص والمواقف باحترافية", 6, "https://www.youtube.com/embed/36yT2G228vA"),

    # مستوى C1
    ("c1_1", "C1", "الدرس 1: القراءة الأكاديمية والبودكاست", 1, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("c1_2", "C1", "الدرس 2: مفردات المستوى المتقدم (C1 Vocabulary)", 2, "https://www.youtube.com/embed/36yT2G228vA"),
    ("c1_3", "C1", "الدرس 3: التحدث بنبرة المتحدث الأصلي تماماً", 3, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("c1_4", "C1", "الدرس 4: تقديم العروض والخطب الاحترافية", 4, "https://www.youtube.com/embed/36yT2G228vA"),
    ("c1_5", "C1", "الدرس 5: تحليل النصوص المعقدة ودلالاتها", 5, "https://www.youtube.com/embed/gR_4m2b_sC4"),
    ("c1_6", "C1", "الدرس 6: اختبار القياس والإتقان التام للغة", 6, "https://www.youtube.com/embed/36yT2G228vA")
]

with app.app_context():
    db.create_all()
    for lid, lvl, title, ord_num, url in DEFAULT_LESSONS:
        if not Lesson.query.get(lid):
            db.session.add(Lesson(id=lid, level=lvl, title=title, order=ord_num, youtube_url=url))
    db.session.commit()

@app.route('/')
def index():
    lesson_id = request.args.get('lesson', 'a1_1')
    current_lesson = Lesson.query.get(lesson_id) or Lesson.query.first()
    lessons = Lesson.query.order_by(Lesson.level, Lesson.order).all()
    
    levels_data = {}
    for l in lessons:
        if l.level not in levels_data:
            levels_data[l.level] = []
        levels_data[l.level].append(l)

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>أكاديمية فارس</title>
        <style>
            body { font-family: Tahoma, sans-serif; background: #121212; color: #fff; margin: 0; display: flex; }
            .sidebar { width: 300px; background: #1e1e1e; height: 100vh; overflow-y: auto; padding: 20px; border-left: 1px solid #333; }
            .main { flex: 1; padding: 30px; }
            .level-title { color: #4CAF50; margin-top: 20px; font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 5px; }
            .lesson-link { display: block; padding: 8px 10px; margin: 5px 0; color: #ccc; text-decoration: none; border-radius: 4px; background: #2a2a2a; }
            .lesson-link:hover, .lesson-link.active { background: #4CAF50; color: #fff; }
            .video-container { position: relative; width: 100%; padding-bottom: 56.25%; height: 0; background: #000; border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
            .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
            .admin-box { background: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333; margin-top: 20px; }
            input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; background: #2a2a2a; color: #fff; border: 1px solid #444; border-radius: 4px; }
            button { background: #4CAF50; border: none; cursor: pointer; font-weight: bold; }
            button:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>🎓 أكاديمية فارس</h2>
            {% for lvl, l_list in levels.items() %}
                <div class="level-title">المستوى {{ lvl }}</div>
                {% for l in l_list %}
                    <a href="/?lesson={{ l.id }}" class="lesson-link {% if l.id == current.id %}active{% endif %}">{{ l.title }}</a>
                {% endfor %}
            {% endfor %}
        </div>
        <div class="main">
            <h1>{{ current.title }} (المستوى {{ current.level }})</h1>
            <div class="video-container">
                <iframe src="{{ current.youtube_url }}" allowfullscreen></iframe>
            </div>
            
            <div class="admin-box">
                <h3>⚙️ لوحة تعديل وتحديث الدرس الحالي</h3>
                <form method="POST" action="/update">
                    <input type="hidden" name="lesson_id" value="{{ current.id }}">
                    <label>عنوان الدرس:</label>
                    <input type="text" name="title" value="{{ current.title }}" required>
                    <label>رابط اليوتيوب (Embed):</label>
                    <input type="text" name="youtube_url" value="{{ current.youtube_url }}" required>
                    <button type="submit">حفظ التعديلات</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(HTML_TEMPLATE, current=current_lesson, levels=levels_data)

@app.route('/update', methods=['POST'])
def update():
    lesson_id = request.form.get('lesson_id')
    lesson = Lesson.query.get(lesson_id)
    if lesson:
        lesson.title = request.form.get('title')
        lesson.youtube_url = request.form.get('youtube_url')
        db.session.commit()
    return redirect(url_for('index', lesson=lesson_id))

if __name__ == '__main__':
    app.run(debug=True)
