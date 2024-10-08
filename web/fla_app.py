from flask import Flask, render_template
import datetime
import random

app = Flask(__name__)

def apply_styles(func):
    def wrapper():
        result = func()
        result = f"<b>{result}</b>"
        result = f"<em>{result}</em>"
        result = f"<u>{result}</u>"
        return result
    return wrapper

@app.route('/')
def hello_world():
    return '''
        <h1 style="text-align: center">Hello, World!</h1>
        <p style="text-align: left">This is a simple Flask app</p>
        <p><img src="static/dub.gif" alt="Animated GIF"></p>
        <iframe src="https://1drv.ms/v/c/a026266e59d33b42/IQOq9zErOSGLSYGhd4KkmjQnAUDXBEGmKynp4f3yizH0yuQ" 
            width="720" height="1280" frameborder="0" scrolling="no" allowfullscreen autoplay loop></iframe>
    '''
@app.route('/bye')
@apply_styles
def bye():
    return 'Goodbye, World!'

@app.route('/new') 
def home():
    random_number = random.randint(1, 10)
    current_year = datetime.datetime.now().year
    return render_template('index.html', num = random_number, year = current_year)

if __name__ == '__main__':
    app.run(debug=True)


