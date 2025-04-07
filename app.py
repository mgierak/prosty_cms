from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'tajny_klucz'

DB = 'cms.db'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"pl\">
<head>
  <meta charset=\"UTF-8\">
  <title>Moja Strona</title>
</head>
<body>
  <h1>Moja Strona</h1>
  <nav>
    <a href=\"/\">Strona główna</a> |
    <a href=\"/login\">Admin</a>
  </nav>
  <hr>
  <h2>O nas</h2>
  <p>{{ about }}</p>

  <h2>Kontakt</h2>
  <p>{{ contact }}</p>
</body>
</html>
"""

ADMIN_PANEL = """
<!DOCTYPE html>
<html lang=\"pl\">
<head>
  <meta charset=\"UTF-8\">
  <title>Panel Admina</title>
</head>
<body>
  <h1>Panel Admina</h1>
  <form method=\"post\">
    <label>O nas:</label><br>
    <textarea name=\"about\" rows=\"5\" cols=\"60\">{{ about }}</textarea><br><br>
    <label>Kontakt:</label><br>
    <textarea name=\"contact\" rows=\"5\" cols=\"60\">{{ contact }}</textarea><br><br>
    <input type=\"submit\" value=\"Zapisz\">
  </form>
  <a href=\"/logout\">Wyloguj</a>
</body>
</html>
"""

LOGIN_PAGE = """
<form method=\"post\">
  <h2>Logowanie</h2>
  <input type=\"text\" name=\"username\" placeholder=\"Login\"><br>
  <input type=\"password\" name=\"password\" placeholder=\"Hasło\"><br>
  <input type=\"submit\" value=\"Zaloguj\">
</form>
"""

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS content (id INTEGER PRIMARY KEY, about TEXT, contact TEXT)''')
    c.execute('SELECT COUNT(*) FROM content')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO content (about, contact) VALUES (?, ?)", ("To jest tekst 'O nas'", "kontakt@strona.pl"))
    conn.commit()
    conn.close()

def get_content():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT about, contact FROM content WHERE id=1")
    content = c.fetchone()
    conn.close()
    return content

def update_content(about, contact):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE content SET about=?, contact=? WHERE id=1", (about, contact))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    about, contact = get_content()
    return render_template_string(HTML_TEMPLATE, about=about, contact=contact)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template_string(LOGIN_PAGE)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        update_content(request.form['about'], request.form['contact'])
        return redirect(url_for('admin'))

    about, contact = get_content()
    return render_template_string(ADMIN_PANEL, about=about, contact=contact)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
