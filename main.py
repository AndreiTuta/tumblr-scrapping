
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_caching import Cache
from scraper import scrap

app = Flask(__name__)

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/pins')
@cache.cached(timeout=600, query_string=True)
def pins():
    term = request.args.get('query')
    size = request.args.get('page-results')
    pins = scrap(term, size)
    return render_template('gallery.html', pins=pins)


if __name__ == '__main__':
    app.run()