from flask import Flask, render_template
import os

app = Flask(__name__, 
    template_folder='src/dashboard/templates',
    static_folder='src/dashboard/static'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
