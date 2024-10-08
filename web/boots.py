from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/album.html')
def album():
    return render_template('album.html')

@app.route('/album2.html')
def album2():
    return render_template('album2.html')

if __name__ == '__main__':
    app.run(debug=True)
