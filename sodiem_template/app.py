from flask import Flask, request, url_for, abort, redirect, make_response, render_template
from werkzeug.routing import BaseConverter

app = Flask(__name__)

class MSSVConverter(BaseConverter):
    regex = r"\d{2}T\d{7}"

app.url_map.converters["mssv"] = MSSVConverter

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
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
    return render_template("index.html", 
                           total_students=total_students, 
                           total_classes=len(unique_classes), 
                           unique_classes=unique_classes)

@app.route("/students")
def get_students():
    selected_class = request.args.get("lop", "").strip()
    unique_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    
    # Lọc sinh viên và tính luôn điểm TB để truyền ra template
    filtered_students = []
    for mssv, info in STUDENTS.items():
        if not selected_class or info["lop"].upper() == selected_class.upper():
            dtb, xep_loai = tinh_dtb_va_xep_loai(info.get("scores", {}))
            filtered_students.append({
                "mssv": mssv, "name": info["name"], "lop": info["lop"], 
                "dtb": dtb, "xep_loai": xep_loai
            })
            
    return render_template("students.html", 
                           students=filtered_students, 
                           unique_classes=unique_classes, 
                           selected_class=selected_class.upper())

@app.route("/students/<mssv:mssv>")
def student_detail(mssv):
    student = STUDENTS.get(mssv)
    if not student:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    dtb, xep_loai = tinh_dtb_va_xep_loai(student.get("scores", {}))
    return render_template("detail.html", 
                           mssv=mssv, 
                           student=student, 
                           dtb=dtb, 
                           xep_loai=xep_loai)

@app.route("/students/<mssv:mssv>/export")
def export_csv(mssv):
    student = STUDENTS.get(mssv)
    if not student:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
        
    csv_lines = ["hoc_phan,diem"]
    for mon, diem in student.get("scores", {}).items():
        csv_lines.append(f"{mon},{diem}")
    
    response = make_response("\n".join(csv_lines))
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response

@app.route("/sv/<mssv:mssv>")
def redirect_student(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    
    results = []
    if query:
        query_lower = query.lower()
        for mssv, info in STUDENTS.items():
            if query_lower in info["name"].lower() or query_lower in mssv.lower():
                results.append({"mssv": mssv, "info": info})
                
    return render_template("search.html", query=query, results=results)

@app.route("/api/students")
def api_students():
    return {"status": "success", "data": STUDENTS}

if __name__ == "__main__":
    app.run(debug=True, port=8000)