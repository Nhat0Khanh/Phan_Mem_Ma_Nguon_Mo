import os
from datetime import date, timedelta
from flask import Flask, render_template, request, session, flash, redirect, url_for
from forms import RegistrationForm

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-chi-dung-khi-phat-trien')

app.permanent_session_lifetime = timedelta(days=7)

USERS = {
    "admin": "admin123",
    "an": "an123456"
}

@app.context_processor
def inject_helpers():
    def is_active(path):
        return "active" if request.path == path else ""
    return {"is_active": is_active}


@app.route('/')
def about():
    return render_template('about.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    errors = {}
    result = None
    color_class = "success"  
    
    h_str = ""
    w_str = ""
    
    if request.method == 'POST':
        h_str = request.form.get('height', '').strip()
        w_str = request.form.get('weight', '').strip()
        
        h_val = None
        if not h_str:
            errors['height'] = "Vui lòng nhập một số."
        else:
            try:
                h_val = float(h_str.replace(',', '.'))
                if h_val < 50 or h_val > 250:
                    errors['height'] = "Giá trị phải từ 50 đến 250. (nhập mét thay vì cm)"
            except ValueError:
                errors['height'] = "Vui lòng nhập một số."

        w_val = None
        if not w_str:
            errors['weight'] = "Vui lòng nhập một số."
        else:
            try:
                w_val = float(w_str.replace(',', '.'))
                if w_val < 10 or w_val > 300:
                    errors['weight'] = "Lỗi ô cân nặng: Giá trị phải từ 10 đến 300."
            except ValueError:
                errors['weight'] = "Vui lòng nhập một số."

        if not errors:
            h_m = h_val / 100.0
            
            bmi_val = round(w_val / (h_m ** 2), 1)
            
            if bmi_val < 18.5:
                category = "Thiếu cân"
                color_class = "warning"  
            elif bmi_val < 23.0:
                category = "Bình thường"
                color_class = "success"  
            elif bmi_val < 25.0:
                category = "Thừa cân"
                color_class = "warning"  
            else:
                category = "Béo phì"
                color_class = "danger"  
                
            w_min = round(18.5 * (h_m ** 2), 1)
            w_max = round(22.9 * (h_m ** 2), 1)
            
            result = f"{bmi_val} - {category}; nên có {w_min} - {w_max} kg"

    return render_template(
        'bmi.html',
        height=h_str,
        weight=w_str,
        errors=errors,
        result=result,
        color_class=color_class
    )

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    error = {}
    result = None

    a_str= ""
    b_str= ""
    op= "+"
    if request.method == 'POST':
        a_str = request.form.get('a', '').strip()
        b_str = request.form.get('b', '').strip()
        op = request.form.get('op', '').strip()

        try:
            a = float(a_str.replace(',', '.'))
        except ValueError:
            error['a'] = 'Lỗi ô a: Vui lòng nhập một số.'

        try:
            b = float(b_str.replace(',', '.'))
        except ValueError:
            error['b'] = 'Lỗi ô b: Vui lòng nhập một số.'

        op = request.form.get('op', '+').strip()
        
        valid_ops = ['+', '-', '*', '/']
        if op not in valid_ops:
            error['op'] = 'Phép toán không hợp lệ.'

        if 'b' not in error and op == '/' and b == 0:
            error['b'] = 'Lỗi ô b: Không thể chia cho 0.'

        if not error:
            if op == '+':
                result = a + b
            elif op == '-':
                result = a - b
            elif op == '*':
                result = a * b
            elif op == '/':
                if b != 0:
                    result = a / b
                else:
                    error['b'] = 'Lỗi ô b: Không thể chia cho 0.'
        

            def clean_num(n):
                return int(n) if n.is_integer() else n

            result = f"{clean_num(a)} {op} {clean_num(b)} = {clean_num(result)}"

    return render_template(
        'calculator.html',
        a=a_str,
        b=b_str,
        op=op,
        errors=error,
        result=result
    )

def validate_score(val_str):
    if not val_str:
        return None, "Lỗi cả 3 ô"
    
    clean_str = val_str.replace(',', '.')
    try:
        score = float(clean_str)
    except ValueError:
        return None, "Lỗi ô CC:Vui lòng nhập một số."
    
    if score < 0 or score > 10:
        return None, "Lỗi ô CC: Điểm phải từ 0 đến 10."
        
    return score, None

@app.route('/diem', methods=['GET', 'POST'])
def grade():
    errors = {}
    result = None
    
    cc_str = ""
    gk_str = ""
    ck_str = ""
    
    if request.method == 'POST':
        cc_str = request.form.get('cc', '').strip()
        gk_str = request.form.get('gk', '').strip()
        ck_str = request.form.get('ck', '').strip()
        
        cc_val, errors['cc'] = validate_score(cc_str)
        gk_val, errors['gk'] = validate_score(gk_str)
        ck_val, errors['ck'] = validate_score(ck_str)
        
        errors = {k: v for k, v in errors.items() if v is not None}
        
        if not errors:
            total = round(cc_val * 0.1 + gk_val * 0.3 + ck_val * 0.6, 1)
            
            if ck_val < 1:
                letter = "F (điểm thi dưới 1)"
            elif total >= 8.5:
                letter = "A"
            elif total >= 7.0:
                letter = "B"
            elif total >= 5.5:
                letter = "C"
            elif total >= 4.0:
                letter = "D"
            else:
                letter = "F"
                
            result = f"{total} - {letter}"
            
    return render_template(
        'diem.html',
        cc=cc_str,
        gk=gk_str,
        ck=ck_str,
        errors=errors,
        result=result
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('bmi'))

    username = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip() 
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        if username in USERS and USERS[username] == password:
            session['user'] = username
            if remember:
                session.permanent = True
                
            flash(f'Đăng nhập thành công. Xin chào {username}!', 'success')
            return redirect(url_for('bmi')) 
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu.', 'danger')

    return render_template('login.html', username=username)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để xem hồ sơ.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(users_dict=USERS)
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        USERS[username] = password
        
        flash('Đăng ký thành công.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, port=5000)