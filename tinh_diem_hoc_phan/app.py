from flask import Flask, render_template, request

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)