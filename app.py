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