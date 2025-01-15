from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

import statistics

# Hitung statistik tambahan
def calculate_extended_stats():
    conn = get_db_connection()
    rows = conn.execute('SELECT score FROM students').fetchall()
    conn.close()

    scores = [row['score'] for row in rows]
    if not scores:
        return {
            "average": 0,
            "median": 0,
            "max": 0,
            "min": 0,
            "std_dev": 0,
            "mode": "Tidak ada",
            "distribution": {"A": 0, "B": 0, "C": 0, "D": 0}
        }

    average = sum(scores) / len(scores)
    median = statistics.median(scores)
    max_score = max(scores)
    min_score = min(scores)
    std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
    try:
        mode = statistics.mode(scores)
    except statistics.StatisticsError:
        mode = "Tidak ada"

    distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
    for score in scores:
        if score >= 85:
            distribution["A"] += 1
        elif score >= 70:
            distribution["B"] += 1
        elif score >= 55:
            distribution["C"] += 1
        else:
            distribution["D"] += 1

    return {
        "average": average,
        "median": median,
        "max": max_score,
        "min": min_score,
        "std_dev": std_dev,
        "mode": mode,
        "distribution": distribution
    }

@app.route('/')
def index():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    stats = calculate_extended_stats()
    return render_template('index.html', students=students, stats=stats)


# Koneksi database
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inisialisasi database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Hitung rata-rata dan distribusi nilai
def calculate_stats():
    conn = get_db_connection()
    rows = conn.execute('SELECT score FROM students').fetchall()
    conn.close()

    scores = [row['score'] for row in rows]
    if not scores:
        return {"average": 0, "distribution": {"A": 0, "B": 0, "C": 0, "D": 0}}

    average = sum(scores) / len(scores)
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0}

    for score in scores:
        if score >= 85:
            distribution["A"] += 1
        elif score >= 70:
            distribution["B"] += 1
        elif score >= 55:
            distribution["C"] += 1
        else:
            distribution["D"] += 1

    return {"average": average, "distribution": distribution}


@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        name = request.form['name']
        score = float(request.form['score'])

        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, score) VALUES (?, ?)', (name, score))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        score = float(request.form['score'])

        conn.execute('UPDATE students SET name = ?, score = ? WHERE id = ?', (name, score, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', student=student)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
