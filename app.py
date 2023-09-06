from hashlib import sha256
from operator import methodcaller
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from flask_socketio import SocketIO
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
from flask_login import LoginManager, current_user, login_required, login_user, UserMixin
from db_model import db, User, Message, FriendRequest
import sqlalchemy.exc


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secure_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
socketio = SocketIO()
socketio.init_app(app)

#初始化
login_manager = LoginManager()
login_manager.init_app(app)

# 初始化数据库
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 主页
@app.route('/', methods=['GET'])
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')
    

# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=20),Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', message='密码必须包含至少一个小写字母、一个大写字母和一个数字。')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password',message='两次输入的密码必须匹配。')])
    submit = SubmitField('Sign Up')

# 注册页
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        encpass = sha256(form.password.data.encode()).hexdigest()
        user = User(username=form.username.data, password=encpass)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except sqlalchemy.exc.DBAPIError:
            db.session.rollback()
            flash('用户名已存在，请选择其他用户名。', 'danger')        
    return render_template('register.html', title='Register', form=form)

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    
# 登录页
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        encpass = sha256(form.password.data.encode()).hexdigest()
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.password == encpass:
            # 如果用户存在并且密码正确
            login_user(user)
            return redirect(url_for('chat')) 
        else:
            flash('登录失败。请检查用户名和密码是否正确。', 'danger')
    return render_template('login.html', title='Login', form=form)

# 聊天页
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    
    return render_template("chat.html", title="ChatRoom")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库表
    app.run(debug=True)
