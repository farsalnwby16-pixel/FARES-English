from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# --- الصفحة الرئيسية مع القائمة الجانبية ونظام التقدم ---
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fares English Academy</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Cairo', sans-serif; background-color: #f8f9fa; color: #333; display: flex; min-height: 100vh; }
        
        /* القائمة الجانبية */
        .sidebar { width: 280px; background-color: #1a2a3a; color: white; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; }
        .sidebar h2 { color: #d4af37; font-size: 22px; margin-bottom: 25px; text-align: center; font-weight: 900; }
        .menu-item { display: block; padding: 12px 15px; color: #e0e0e0; text-decoration: none; border-radius: 6px; margin-bottom: 8px; transition: 0.3s; font-weight: 600; }
        .menu-item:hover, .menu-item.active { background-color: #d4af37; color: #1a2a3a; }
        
        /* قسم الشهادة في القائمة الجانبية */
        .cert-section { background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center; }
        .cert-section h4 { color: #d4af37; margin-bottom: 8px; }
        .cert-btn { display: inline-block; width: 100%; padding: 10px; background-color: #d4af37; color: #1a2a3a; text-decoration: none; font-weight: bold; border-radius: 5px; border: none; cursor: pointer; transition: 0.3s; }
        .cert-btn:hover { background-color: #f39c12; }
        
        /* المحتوى الرئيسي */
        .main-content { flex: 1; padding: 30px; overflow-y: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px; }
        .progress-bar-container { width: 200px; background-color: #e0e0e0; height: 12px; border-radius: 6px; overflow: hidden; }
        .progress-bar { width: 0%; height: 100%; background-color: #27ae60; transition: 0.5s; }

        /* كروت الدروس */
        .lessons-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .lesson-card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); padding: 20px; }
        .lesson-card h3 { margin-bottom: 10px; color: #1a2a3a; }
        .complete-btn { margin-top: 15px; width: 100%; padding: 8px; background-color: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .complete-btn.done { background-color: #27ae60; }
    </style>
</head>
<body>

    <!-- القائمة الجانبية -->
    <div class="sidebar">
        <div>
            <h2>🎓 Fares Academy</h2>
            <a href="#" class="menu-item active">المستوى A1 - الأساسيات</a>
            <a href="#" class="menu-item">المستوى A2 - المبتدئ</a>
            <a href="#" class="menu-item">المستوى B1 - المتوسط</a>
            <a href="#" class="menu-item">المستوى B2 - فوق المتوسط</a>
            <a href="#" class="menu-item">المستوى C1 - المتقدم</a>
            <a href="#" class="menu-item">المستوى C2 - الاحترافي</a>
        </div>

        <!-- خيار الشهادة بعد المستويات -->
        <div class="cert-section">
            <h4>🏅 شهادة الإتمام</h4>
            <p style="font-size: 12px; margin-bottom: 10px; color: #ccc;">أكمل كافة الدروس للحصول على الشهادة</p>
            <input type="text" id="studentNameInput" placeholder="اكتب اسمك للشهادة" style="width: 100%; padding: 6px; margin-bottom: 8px; border-radius: 4px; border: none; font-family: 'Cairo'; text-align: center;">
            <button onclick="openCertificate()" class="cert-btn">📜 معاينة / استخراج الشهادة</button>
        </div>
    </div>

    <!-- المحتوى الرئيسي -->
    <div class="main-content">
        <div class="header">
            <h2>المستوى A1: القواعد الأساسية والمحادثة</h2>
            <div>
                <span id="progressText" style="font-weight: bold;">نسبة الإنجاز: 0%</span>
                <div class="progress-bar-container" style="margin-top: 5px;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
            </div>
        </div>

        <h3>دروس المستوى الحالي:</h3>
        <br>
        <div class="lessons-grid">
            <div class="lesson-card">
                <h3>الدرس 1: Verb to Be</h3>
                <p>تعلم استخدام am, is, are في الجمل الأساسية.</p>
                <button class="complete-btn" onclick="toggleLesson(this)">إكمال الدرس ❌</button>
            </div>
            <div class="lesson-card">
                <h3>الدرس 2: Present Simple</h3>
                <p>شرح زمن المضارع البسيط واستخداماته اليومية.</p>
                <button class="complete-btn" onclick="toggleLesson(this)">إكمال الدرس ❌</button>
            </div>
            <div class="lesson-card">
                <h3>الدرس 3: Daily Vocabulary</h3>
                <p>أهم 50 كلمة ومصطلح للانجليزية اليومية.</p>
                <button class="complete-btn" onclick="toggleLesson(this)">إكمال الدرس ❌</button>
            </div>
        </div>
    </div>

    <script>
        let completedCount = 0;
        const totalLessons = 3;

        function toggleLesson(btn) {
            if (!btn.classList.contains('done')) {
                btn.classList.add('done');
                btn.innerText = 'تم الإكمال ✅';
                completedCount++;
            } else {
                btn.classList.remove('done');
                btn.innerText = 'إكمال الدرس ❌';
                completedCount--;
            }
            updateProgress();
        }

        function updateProgress() {
            let percent = Math.round((completedCount / totalLessons) * 100);
            document.getElementById('progressBar').style.width = percent + '%';
            document.getElementById('progressText').innerText = 'نسبة الإنجاز: ' + percent + '%';
        }

        function openCertificate() {
            let name = document.getElementById('studentNameInput').value.trim();
            if (!name) {
                alert('يرجى كتابة اسمك أولاً ليظهر في الشهادة!');
                return;
            }
            window.location.href = '/certificate?name=' + encodeURIComponent(name);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return MAIN_PAGE_HTML

# --- مسار توليد الشهادة ---
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
            .btn-back { margin-top: 25px; margin-right: 10px; padding: 12px 28px; background-color: #7f8c8d; color: #fff; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-family: 'Cairo', sans-serif; text-decoration: none; display: inline-block; }
            @media print { .btn-print, .btn-back { display: none; } body { background: white; padding: 0; } .certificate-container { box-shadow: none; width: 100%; } }
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
            <a href="/" class="btn-back">⬅️ العودة للمنصة</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(cert_html, student_name=student_name, date=current_date)

if __name__ == '__main__':
    app.run()
