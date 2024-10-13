import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('class_party_support.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS Supplies')
    cursor.execute('DROP TABLE IF EXISTS Party')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Party (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            party_date TEXT,
            supplies_due_date TEXT,
            parent_note TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Supplies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER,
            name TEXT,
            claimed BOOLEAN DEFAULT 0,
            received BOOLEAN DEFAULT 0,
            FOREIGN KEY (party_id) REFERENCES Party (id)
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/create_party', methods=['POST'])
def create_party():
    party_name = request.form['party_name']
    party_date = request.form['party_date']
    supplies_due_date = request.form['supplies_due_date']
    parent_note = request.form['parent_note']
    supplies = request.form['supplies'].split(',')

    conn = sqlite3.connect('class_party_support.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Party (name, party_date, supplies_due_date, parent_note) VALUES (?, ?, ?, ?)', (party_name, party_date, supplies_due_date, parent_note))
    party_id = cursor.lastrowid

    for supply in supplies:
        cursor.execute('INSERT INTO Supplies (party_id, name) VALUES (?, ?)', (party_id, supply.strip()))
    
    conn.commit()
    conn.close()
    return redirect(url_for('party_list', party_id=party_id))

@app.route('/party_list/<int:party_id>')
def party_list(party_id):
    conn = sqlite3.connect('class_party_support.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Party WHERE id = ?', (party_id,))
    party = cursor.fetchone()

    cursor.execute('SELECT id, name, claimed, received FROM Supplies WHERE party_id = ?', (party_id,))
    supplies = cursor.fetchall()

    conn.close()

    if party:
        return render_template('results.html', party=party, supplies=supplies)
    else:
        return "Party not found!", 404

@app.route('/claim/<int:supply_id>', methods=['POST'])
def claim_supply(supply_id):
    conn = sqlite3.connect('class_party_support.db')
    cursor = conn.cursor()
    cursor.execute('SELECT party_id, claimed FROM Supplies WHERE id = ?', (supply_id,))
    result = cursor.fetchone()
    if result is None:
        return "Supply not found!", 404
    party_id, claimed = result
    new_claimed_status = 0 if claimed == 1 else 1
    cursor.execute('UPDATE Supplies SET claimed = ? WHERE id = ?', (new_claimed_status, supply_id))
    conn.commit()
    conn.close()
    return redirect(url_for('party_list', party_id=party_id))

@app.route('/receive/<int:supply_id>', methods=['POST'])
def receive_supply(supply_id):
    conn = sqlite3.connect('class_party_support.db')
    cursor = conn.cursor()
    cursor.execute('SELECT party_id, received FROM Supplies WHERE id = ?', (supply_id,))
    result = cursor.fetchone()
    if result is None:
        return "Supply not found!", 404
    party_id, received = result
    new_received_status = 0 if received == 1 else 1
    cursor.execute('UPDATE Supplies SET received = ? WHERE id = ?', (new_received_status, supply_id))
    conn.commit()
    conn.close()
    return redirect(url_for('party_list', party_id=party_id))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)