from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return (
        f'Hawaii Climate Page<br/>'
        f'Routes:<br/>'
        f'<br/>'
        f'Precipitation with Dates:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'<br/>'
    )