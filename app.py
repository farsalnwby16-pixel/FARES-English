from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fares English Academy</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f8f9fa; }
            h1 { color: #1a2a3a; }
            a { display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #d4af37; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>مرحباً بك في Fares English Academy 🎓</h1>
        <p>المنصة التعليمية تعمل الآن بنجاح!</p>
        <a href="/certificate?name=فارس_النوبي">معاينة الشهادة الاحترافية</a>
    </body>
    </html>
    """

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

if __name__ == '__main__':
    app.run()
