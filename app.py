from flask import Flask
from werkzeug.routing import BaseConverter
app = Flask(__name__)

class ListConverter(BaseConverter):
    regex = r'\d+(?:,\d+)*'

    def to_python(self, value):
        return [int(x) for x in value.split(',')]

    def to_url(self, values):
        return ','.join(str(x) for x in values)
app.url_map.converters['list'] = ListConverter

@app.route('/')
@app.route('/home')
@app.route('/index')
def hello():
    return "Hello, World!"




@app.route('/chia-nhom')
def chia_nhom():
    so_bai = 12
    so_nhom = 0
    rs = f"Mỗi nhóm làm {so_bai / so_nhom} bài"
    return rs

@app.route("/user/<user_name>")
def user_profile(user_name):
    rs = f"Trang cá nhân của {user_name}"
    return rs
    # return f"Trang cá nhân của {user_name}"

@app.route("/square/<int:n>")
def binh_phuong(n):
    rs = f"Bình phương của {n} là {n * n}"
    return rs

@app.route("/sum/<list:numbers>")
def sum_numbers(numbers):
    total = sum(numbers)
    return f'{{"numbers": {numbers}, "sum": {total}}}'

if __name__ == "__main__":
    app.run(debug=True, port=8000)