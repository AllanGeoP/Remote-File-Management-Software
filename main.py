import os
import shutil
import urllib.request
import pathlib
import socket
import json
import sys
from waitress import serve
from flask import Flask, render_template, request, redirect, make_response, send_file
from werkzeug.utils import secure_filename


def folder(path,filename):
    if filename!='':
        filename+='\\'
    var='['
    for i in os.listdir(path):
        if os.path.isfile(path + r'\\' + i):
            var +='{"name":"'+i+'","size":'+str(os.path.getsize(path + r'\\' + i))+',"type":"'+pathlib.Path(path + r'\\' + i).suffix+'","path":"openfile/'+filename+i+'"},'
        else:
            var +='{"name":"'+i+'","size":'+str(os.path.getsize(path + r'\\' + i))+',"type":"folder","path":"filedata/'+i+'"},'
    var+='{"name":"no"}]'
    return var


if os.path.exists('user_details.txt') and os.path.exists('MainDirectory.txt') and os.path.exists('main_path.txt'):
    print("CriticalFileCheck")
else:
    input("MissingFiles")
    sys.exit()
f = open('user_details.txt')
user_details = json.load(f)
f.close()
f = open('main_path.txt', 'r')
main_path = r'' + f.read()
f.close()
if os.path.exists(main_path):
    print("StorageDirectoryExists")
else:
    input("StorageDirectoryMissing")
    sys.exit()
Sessions = []
f = open('MainDirectory.txt', 'r')
template_dir = r'' + f.read()
print(f"MainDirectory={template_dir}")
template_dir = os.path.join(template_dir, 'templates')
print(f"TemplateDirectory={template_dir}")

app = Flask(__name__, template_folder=template_dir)

user = "Admin"
password = "Password"


@app.route('/', methods=["GET"])
def home():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        return redirect('/dashboard')
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET'])
def login0():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        return redirect('/dashboard')
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login1():
    usr = request.form['uname']
    psw = request.form['psw']
    log = {'user': usr, 'password': psw}
    if log in user_details:
        global Sessions
        Sessions.append(usr)
        resp = make_response(redirect('/dashboard'))
        resp.set_cookie('user', usr)
        return resp
    else:
        return "Incorrect User Name or password Try Again"


@app.route('/signup', methods=['GET'])
def signup0():
    return render_template('sin.html')


@app.route('/signup', methods=['POST'])
def signup1():
    usr = request.form['uname']
    psw = request.form['psw']
    global user_details
    user_details.append({"user": usr, "password": psw})
    f = open('user_details.txt', 'w')
    json.dump(user_details, f)
    f.close()
    os.mkdir(path=main_path + r'\\' + usr)
    return redirect('/login')


@app.route('/filedata/<path:filename>')
def filedata(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user
        var=folder(path,filename)
        return var
    else:
        return "ERROR"


@app.route('/filedata')
def filedat():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user
        var=folder(path,'')
        return var
    else:
        return "ERROR"


@app.route('/dashboard')
def dashboard():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        return render_template('/dashboard.html')
    else:
        return redirect('/login')


@app.route('/uploadfolder', methods=['GET'])
def upload0():
    return render_template('upload.html')


@app.route('/uploadfolder', methods=['POST'])
def upload1():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\'
        f = request.files.getlist('folder')
        var=[]
        for file in f:
            vari=file.filename
            vari =vari.replace('/','\\')
            varit=vari.rsplit('\\',1)
            varity=varit[len(varit)-2]
            if os.path.exists(path+varity):
                file.save(path+vari)
            else:
                os.mkdir(path+varity)
                file.save(path + vari)
        return redirect('/dashboard')
    else:
        return 'ERROR'


@app.route('/uploadfile', methods=['GET'])
def upload2():
    return render_template('uploadfile.html')


@app.route('/uploadfile', methods=['POST'])
def upload3():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user
        f = request.files['file']
        f.save(os.path.join(path, secure_filename(f.filename)))
        return redirect('/dashboard')
    else:
        return 'ERROR'


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\' + filename
        return send_file(path, as_attachment=True)
    else:
        return "ERROR"


@app.route('/signout', methods=['GET'])
def signout():
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        Sessions.remove(get_user)
        resp = make_response(redirect('/login'))
        resp.set_cookie('user', '', expires=0)
        return resp
    else:
        return redirect('/login')


@app.route('/delete/<path:filename>', methods=['GET', 'POST'])
def delete(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\' + filename
        os.remove(path)
        return redirect('/dashboard')
    else:
        return "ERROR"


@app.route('/deletefolder/<path:filename>', methods=['GET', 'POST'])
def deletefolder(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\' + filename
        shutil.rmtree(path)
        return redirect('/dashboard')
    else:
        return "ERROR"


@app.route('/compress/<path:filename>', methods=['GET', 'POST'])
def compress(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\' + filename
        shutil.make_archive(path, 'zip', path)
        return redirect('/dashboard')
    else:
        return "ERROR"


@app.route('/openfile/<path:filename>', methods=['GET', 'POST'])
def openfile(filename):
    get_user = request.cookies.get('user')
    if get_user in Sessions:
        path = main_path + r'\\' + get_user + r'\\' + filename
        return send_file(path)
    else:
        return "ERROR"


external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

print(f"Serving on public ip http://{external_ip}")

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        port = 80

    print(f"Server is running on http://{ip}")
    serve(app, host='0.0.0.0', port=80, max_request_body_size=2 * 1024 * 1024 * 1024)
