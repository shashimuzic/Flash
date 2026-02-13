# Imported all the necessary the tools in this Python file.

from flask import Flask, render_template, render_template_string, request, redirect, send_from_directory, session, url_for, abort, send_file
import os, shutil, mimetypes, zipfile
from werkzeug.utils import secure_filename
from functools import wraps
import socket, qrcode

app = Flask(__name__)
app.secret_key = 'termux_secret'

BASE_DIR = "C:/Users/shash/Downloads"
DEFAULT_DIR = os.path.join(BASE_DIR, "Downloads")
MAX_PREVIEW_SIZE = 100 * 1024 * 1024  # 100MB

# You can edit this by your choice.

USERNAME = "SK2121"
PASSWORD = "2121"

# For Login Details.
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# formatting file size numbers into human readable form
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

# Setting route of Dashboard Page after verification. 
@app.route("/", methods=["GET"])
def index():
    return redirect("/dashboard")

# Verification & Redirected to Dashboard Page.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"
    from flask import render_template
    return render_template("login.html")

# After Logout message will be shown.
@app.route("/logout")
def logout():
    session.clear()
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return "Server shutting down..."

# Giving access to the file manager after verification. 
@app.route("/dashboard", defaults={'req_path': ''})
@app.route("/dashboard/<path:req_path>")
@login_required
def dashboard(req_path):
    abs_path = os.path.join(BASE_DIR, req_path)
    if not os.path.exists(abs_path):
        return abort(404)

    if os.path.isfile(abs_path):
        return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

    files = []
    folders = []
    for item in os.listdir(abs_path):
        full_path = os.path.join(abs_path, item)
        if os.path.isdir(full_path):
            folders.append(item)
        else:
            size = os.path.getsize(full_path)
            files.append({
                "name": item,
                "size": size,
                "size_str": sizeof_fmt(size),
            })

    rel_path = os.path.relpath(abs_path, BASE_DIR)
    rel_path = "" if rel_path == "." else rel_path + "/"

    return render_template("dashboard.html",files=files,folders=folders,rel_path=rel_path)

# For sending (there is upload option) we will choose the file and upload them.
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        return "No file uploaded", 400
    files = request.files.getlist('file')
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            dest_path = os.path.join(DEFAULT_DIR, filename)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            file.save(dest_path)
    return redirect(url_for("dashboard"))

# Setting route of downloaded file
@app.route("/download/<path:filename>")
@login_required
def download(filename):
    file_path = os.path.join(BASE_DIR, filename)

    if os.path.isdir(file_path):
        zip_path = file_path + ".zip"
        shutil.make_archive(file_path, 'zip', file_path)

        def generate():
            with open(zip_path, 'rb') as f:
                yield from f
            os.remove(zip_path)  # Auto-delete after download

        return app.response_class(generate(), mimetype='application/zip',
            headers={"Content-Disposition": f"attachment;filename={os.path.basename(zip_path)}"})

    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)


@app.route("/view/<path:filename>")
@login_required
def view_file(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) < MAX_PREVIEW_SIZE:
        mime_type, _ = mimetypes.guess_type(file_path)
        return send_file(file_path, mimetype=mime_type)
    return "File too large to preview or doesn't exist."

@app.route("/delete/<path:filename>")
@login_required
def delete_file(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # Detect local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    url = f"http://{ip}:2121"

    # Generate QR code image
    img = qrcode.make(url)
    img.show()  # This will pop up the QR code in default viewer

    print(f"\n📡 Shareable Link: {url}\n")
    print("Scan the QR code to access the file manager.\n")
    app.run(host="0.0.0.0", port=2121)   # you can change the port here.