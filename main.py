
from flask import Flask, render_template, request, url_for, redirect, flash, session
from scraper import scrap

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/pins')
def pins():
    term = request.args.get('query')
    size = request.args.get('page-results')
    pins = scrap(term, size)
    return render_template('gallery.html', pins=pins)


if __name__ == '__main__':
    app.run(debug=True)