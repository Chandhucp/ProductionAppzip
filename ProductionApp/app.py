from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import csv
from datetime import datetime, timedelta
from io import StringIO

app = Flask(__name__)

# Database file
DATABASE = 'production.db'

# Function to get a connection to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    success_message = None  # Define a variable to store success messages
    
    if request.method == 'POST':
        category = request.form['category']
        received_time_est = request.form['received_time_est']
        received_time_ist = (datetime.fromisoformat(received_time_est) + timedelta(hours=9, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        pims_id = request.form['pims_id']
        completed_time_est = request.form['completed_time_est']
        completed_time_ist = (datetime.fromisoformat(completed_time_est) + timedelta(hours=9, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        completed_by = request.form['completed_by']

        # Insert data into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO production_data (category, received_time_est, received_time_ist, pims_id, completed_time_est, completed_time_ist, completed_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, received_time_est, received_time_ist, pims_id, completed_time_est, completed_time_ist, completed_by))
        conn.commit()
        conn.close()

        # Pass a success message to the template
        success_message = 'Data submitted successfully!'
        return render_template('form.html', success_message=success_message)

    return render_template('form.html', success_message=success_message)


@app.route('/download_report', methods=['GET'])
def download_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM production_data
            WHERE DATE(received_time_est) >= ? AND DATE(received_time_est) <= ?
        ''', (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()

        # Create a CSV file in memory
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Category', 'Received Time (EST)', 'Received Time (IST)', 'PIMS ID', 'Completed Time (EST)', 'Completed Time (IST)', 'Completed By'])
        
        for row in rows:
            writer.writerow([row['id'], row['category'], row['received_time_est'], row['received_time_ist'], row['pims_id'], row['completed_time_est'], row['completed_time_ist'], row['completed_by']])
        
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, attachment_filename=f'Report_{start_date}_to_{end_date}.csv')
    
    return redirect(url_for('index'))


@app.route('/live_report', methods=['GET'])
def live_report():
    today = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM production_data WHERE DATE(received_time_est) = ?
    ''', (today,))
    rows = cursor.fetchall()
    conn.close()

    return render_template('live_report.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
