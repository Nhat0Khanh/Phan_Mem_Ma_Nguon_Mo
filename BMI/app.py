from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/bmi', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)