
from flask import Flask, render_template, request, url_for, redirect, flash, session, stream_with_context, Response, send_file
from flask_caching import Cache
from scraper import init

app = Flask(__name__)

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
# tell Flask to use the above defined config
app.config.from_mapping(config)
cache = Cache(app)

ph = init()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/pins')
@cache.cached(timeout=600, query_string=True)
def pins():
    term = request.args.get('query')
    size = request.args.get('page-results')
    pins = ph.scrap(term, size)
    return render_template('gallery.html', pins=pins, term=term)

@app.route('/get_pins/<term>')
def stream_data(term: str):
    ph.write_results(term)
    return send_file(f'results/{term}/temp.zip', attachment_filename='response.zip')


if __name__ == '__main__':
    app.run()