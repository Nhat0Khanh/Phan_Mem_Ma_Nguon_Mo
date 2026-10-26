from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)