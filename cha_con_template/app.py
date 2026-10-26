from datetime import date
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.routing import BaseConverter
app = Flask(__name__)

@app.context_processor
def inject_globals():
    return {
        "site_name": "MiniBlog",
        "current_year": date.today().year,
    }
@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        return "active" if request.endpoint == endpoint else ""
    
    return {
        "is_active": is_active
    }

@app.route("/")
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Lấy thông tin khi người dùng bấm nút Gửi tin nhắn
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # (Tại đây bạn có thể lưu vào CSDL hoặc gửi email thông báo)
        print(f"Nhận liên hệ từ {name} ({email}): {message}")
        
        # Sau khi gửi xong thì tải lại trang contact
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/gioithieu')
def gioithieu():
    return render_template('gioithieu.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)