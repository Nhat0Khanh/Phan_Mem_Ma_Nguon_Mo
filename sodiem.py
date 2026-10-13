from flask import Flask, request, url_for, abort, redirect, make_response
from werkzeug.routing import BaseConverter
from markupsafe import escape

app = Flask(__name__)

class MSSVConverter(BaseConverter):
    regex = r"\d{2}T\d{7}"

app.url_map.converters["mssv"] = MSSVConverter

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A",
        "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def tinh_dtb_va_xep_loai(scores):
    if not scores:
        return "-", "-"
    dtb = sum(scores.values()) / len(scores)
    if dtb >= 8.5:
        xep_loai = "Xuất sắc"
    elif dtb >= 8.0:
        xep_loai = "Giỏi"
    elif dtb >= 6.5:
        xep_loai = "Khá"
    elif dtb >= 5.0:
        xep_loai = "Trung bình"
    else:
        xep_loai = "Yếu"
    return f"{dtb:.2f}", xep_loai

@app.route("/")
def index():
    total_students = len(STUDENTS)
    unique_classes = set(student["lop"] for student in STUDENTS.values())
    total_classes = len(unique_classes)
    
    return f"""
    <h1>Trang chủ</h1>
    <ul>
        <li>Tổng số sinh viên: <strong>{total_students}</strong></li>
        <li>Số lớp: <strong>{total_classes}</strong> <em>({', '.join(unique_classes)})</em></li>
    </ul>
    <h3>Các liên kết:</h3>
    <ul>
        <li><a href="{url_for('get_students')}">Xem danh sách sinh viên (/students)</a></li>
        <li><a href="{url_for('search')}">Tìm kiếm sinh viên (/search)</a></li>
        <li><a href="{url_for('api_students')}">API danh sách sinh viên (/api/students)</a></li>
    </ul>
    """

@app.route("/students")
def get_students():
    selected_class = request.args.get("lop", "").strip()
    unique_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    
    filter_links = [f'<a href="{url_for("get_students")}">Tất cả</a>']
    for c in unique_classes:
        filter_links.append(f'<a href="{url_for("get_students", lop=c)}">{c}</a>')
    
    filter_bar = " | ".join(filter_links)
    
    filtered_students = {}
    for mssv, info in STUDENTS.items():
        if not selected_class or info["lop"].upper() == selected_class.upper():
            filtered_students[mssv] = info
            
    if not filtered_students:
        content = "<p>Không có sinh viên phù hợp</p>"
    else:
        rows = ""
        for mssv, info in filtered_students.items():
            dtb, xep_loai = tinh_dtb_va_xep_loai(info.get("scores", {}))
            student_link = url_for("student_detail", mssv=mssv)
            rows += f"""
            <tr>
                <td><a href="{student_link}">{mssv}</a></td>
                <td>{info['name']}</td>
                <td>{info['lop']}</td>
                <td>{dtb}</td>
                <td>{xep_loai}</td>
            </tr>
            """
            
        content = f"""
        <table border="1" cellpadding="8" cellspacing="0">
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
        
    return f"""
    <h2>Danh sách sinh viên</h2>
    <div style="margin-bottom: 15px;">
        <strong>Lọc theo lớp:</strong> {filter_bar}
    </div>
    {content}
    <br><br>
    <a href="{url_for('index')}">← Trang chủ</a>
    """

@app.route("/students/<mssv:mssv>")
def student_detail(mssv):
    student = STUDENTS.get(mssv)
    if not student:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    dtb, xep_loai = tinh_dtb_va_xep_loai(student.get("scores", {}))
    class_filter_link = url_for("get_students", lop=student["lop"])
    
    short_url = url_for("redirect_student", mssv=mssv)
    export_csv_url = url_for("export_csv", mssv=mssv)
    
    scores = student.get("scores", {})
    if not scores:
        scores_table = "<p><em>Chưa có điểm học phần nào.</em></p>"
    else:
        score_rows = "".join([f"<tr><td>{mon}</td><td>{diem}</td></tr>" for mon, diem in scores.items()])
        scores_table = f"""
        <table border="1" cellpadding="6" cellspacing="0">
            <thead>
                <tr><th>Học phần</th><th>Điểm</th></tr>
            </thead>
            <tbody>{score_rows}</tbody>
        </table>
        """
        
    return f"""
    <h2>Thông tin chi tiết sinh viên</h2>
    <p><strong>MSSV:</strong> {mssv}</p>
    <p><strong>Họ tên:</strong> {student['name']}</p>
    <p><strong>Lớp:</strong> <a href="{class_filter_link}">{student['lop']}</a></p>
    <p><strong>Điểm TB:</strong> {dtb}</p>
    <p><strong>Xếp loại:</strong> {xep_loai}</p>
    
    <h3>Bảng điểm từng học phần</h3>
    {scores_table}
    <br>
    <a href="{export_csv_url}" style="padding: 6px 12px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px;">
        Tải bảng điểm (CSV)
    </a>
    
    <br><br>
    <a href="{url_for('get_students')}">← Quay lại danh sách sinh viên</a>
    """

@app.route("/students/<mssv:mssv>/export")
def export_csv(mssv):
    student = STUDENTS.get(mssv)
    if not student:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    csv_lines = ["hoc_phan,diem"]
    for mon, diem in student.get("scores", {}).items():
        csv_lines.append(f"{mon},{diem}")
    csv_data = "\n".join(csv_lines)
    
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    
    return response

@app.route("/sv/<mssv:mssv>")
def redirect_student(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)

@app.route("/search")
def search():
    raw_query = request.args.get("q", "").strip()
    safe_query = escape(raw_query)
    
    results = []
    if raw_query:
        query_lower = raw_query.lower()
        for mssv, info in STUDENTS.items():
            if query_lower in info["name"].lower() or query_lower in mssv.lower():
                results.append((mssv, info))
                
    if not raw_query:
        result_content = ""
    elif not results:
        result_content = f"<p>Tìm thấy 0 kết quả cho \"{safe_query}\"</p>"
    else:
        items = "".join([f"<li><a href=\"{url_for('student_detail', mssv=mssv)}\">{mssv} - {info['name']}</a> ({info['lop']})</li>" for mssv, info in results])
        result_content = f"""
        <p>Tìm thấy <strong>{len(results)}</strong> kết quả cho "<strong>{safe_query}</strong>":</p>
        <ul>{items}</ul>
        """
        
    return f"""
    <h2>Tìm kiếm sinh viên</h2>
    <form action="{url_for('search')}" method="GET">
        <input type="text" name="q" value="{safe_query}" placeholder="Nhập tên hoặc MSSV..." size="30">
        <button type="submit">Tìm kiếm</button>
    </form>
    <br>
    {result_content}
    <br>
    <a href="{url_for('index')}">← Trang chủ</a>
    """

@app.route("/api/students")
def api_students():
    return {"status": "success", "data": STUDENTS}

if __name__ == "__main__":
    app.run(debug=True, port=8000)