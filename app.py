from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, URL
import string
import random
import validators

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SECRET_KEY'] = 'secret123'

db.init_app(app)

with app.app_context():
    db.create_all()

# Generate random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None

    if request.method == 'POST':
        original_url = request.form['url']

        # URL validation
        if not validators.url(original_url):
            flash("❌ Invalid URL. Please enter a valid one.", "danger")
            return redirect(url_for('index'))

        short_code = generate_short_code()
        new_url = URL(original_url=original_url, short_code=short_code)

        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + short_code

    return render_template('index.html', short_url=short_url)


@app.route('/history')
def history():
    urls = URL.query.order_by(URL.created_at.desc()).all()
    return render_template('history.html', urls=urls)


@app.route('/<short_code>')
def redirect_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first_or_404()
    return redirect(url.original_url)


if __name__ == '__main__':
    app.run(debug=True)
