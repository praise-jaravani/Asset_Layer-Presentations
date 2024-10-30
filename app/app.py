# app.py
from flask import Flask, render_template, request, jsonify
from deadline_manager import DocumentDeadlineManager
from pathlib import Path
import os

app = Flask(__name__)
manager = DocumentDeadlineManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    # Save file temporarily
    content = file.read().decode('utf-8')
    
    # Process document
    manager.process_new_document(content, file.filename)
    
    # Get all deadlines
    deadlines = manager.get_all_deadlines()
    
    # Convert to dictionary for JSON response
    deadlines_dict = deadlines.to_dict('records')
    
    return jsonify({
        'success': True,
        'deadlines': deadlines_dict
    })

@app.route('/deadlines/<deadline_type>')
def get_deadlines(deadline_type):
    if deadline_type == 'upcoming':
        deadlines = manager.get_upcoming_deadlines()
    elif deadline_type == 'expired':
        deadlines = manager.get_expired_deadlines()
    else:
        deadlines = manager.get_all_deadlines()
        
    return jsonify(deadlines.to_dict('records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
