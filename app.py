from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import string,random
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(50),nullable=False)

class Url(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    long_url = db.Column(db.String(200),nullable=False)
    short_url = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

with app.app_context():
     db.create_all()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choices(characters,k=5)) 
    return short_url
@app.route('/',methods=['GET','POST'])
def home():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        if not request.form['url']:
            print('⚠️ Please enter a valid URL.', 'warning')
            return redirect(url_for('home'))
        long_url = request.form['url']
        print(f'Long URL submitted: {long_url}')  # Debugging statement
        short_url = generate_short_url()
        new_url = Url(long_url=long_url, short_url=short_url, user_id=session['user'])
        db.session.add(new_url)
        db.session.commit()
        return redirect(url_for('home'))
    all_urls = Url.query.filter_by(user_id=session['user']).all()
    return render_template('index.html', all_urls=all_urls)
@app.route('/delete/<short_url>')
def delete_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    db.session.delete(url)
    db.session.commit()
    return redirect(('/'))
@app.route('/<short_url>')
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url is None:
        return "URL not found"
    return redirect(url.long_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # check if user already exists
        user = User.query.filter_by(name=name).first()
        if user:
            print('⚠️ Username already exists. Please choose another one.', 'warning')
            return redirect(url_for('register'))

        # hash the password before storing
        hashed_password = generate_password_hash(password)

        # create new user
        new_user = User(name=name, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print('✅ Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # Fetch user from database
        user = User.query.filter_by(name=name).first()

        # Validate credentials using password hash
        if user and check_password_hash(user.password, password):
            session['user'] = user.id
            print(f'👋 Welcome back, {user.name}!', 'success')
            return redirect(url_for('home'))
        else:
            print ('❌ Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('user',None)
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(debug=True)



