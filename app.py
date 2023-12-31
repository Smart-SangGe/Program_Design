from hashlib import sha256
from flask import Flask, get_flashed_messages, render_template, redirect, url_for, flash, request, session, jsonify
from flask_wtf import FlaskForm
from flask_socketio import SocketIO
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from db_model import db, User, Message, FriendRequest, friendship
import sqlalchemy.exc
from datetime import datetime

app = Flask(__name__)

app.config.from_object('config')
socketio = SocketIO(app)

#初始化
login_manager = LoginManager()
login_manager.init_app(app)

# 初始化数据库
db.init_app(app)
with app.app_context():
    db.create_all()


user_sockets = {}


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
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,max=20),\
        Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', message='密码必须包含至少一个小写字母、一个大写字母和一个数字。')])
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
            flash("注册成功")
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
    data = get_flashed_messages()
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            encpass = sha256(form.password.data.encode()).hexdigest()
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.password == encpass:
                # 如果用户存在并且密码正确
                login_user(user)
                session['user_id'] = user.id
                flash(f"欢迎回来，{user.username}!")
                return redirect(url_for('chat'))
            else:
                flash('登录失败。请检查用户名和密码是否正确。', 'danger')
        
    return render_template('login.html', title='Login', form=form)


# 处理消息
@socketio.on('new_message')
def handle_message(data):
    message_content = data['message']
    receiver_id = data['receiver_id']  # 从前端发送的数据中获取接收者的ID
    if receiver_id == None:
        return

    # 创建一个新的消息对象
    new_message = Message(
        content=message_content,
        sender_id=current_user.id,  #type: ignore
        receiver_id=receiver_id,
        timestamp=datetime.utcnow() 
    )
    # 添加到数据库会话并提交
    db.session.add(new_message)
    db.session.commit()

    socketio.emit('new_message', {
        'message': new_message.content, 
        'sender_id': new_message.sender_id,
        'receiver_id': new_message.receiver_id
    })
    
    
    
# 聊天页
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    friends_list = current_user.friends.all() #type: ignore
    user_id = current_user.id #type: ignore
    return render_template("chat.html", title="ChatRoom", friends=friends_list, user_id=user_id)

# 获取聊天记录
@app.route('/getChatHistory', methods=['GET'])
@login_required
def get_chat_history():
    
    friend_id = request.args.get('friend_id', type=int)
    
    current_user_id = current_user.id #type: ignore

    # 从数据库中查询与特定好友的聊天记录
    messages_from_db = Message.query.filter(
        (Message.sender_id == current_user_id) & (Message.receiver_id == friend_id) |
        (Message.sender_id == friend_id) & (Message.receiver_id == current_user_id)
    ).order_by(Message.timestamp).all()

    # 将数据库中的记录转换为你所需要的格式
    messages = [{
        "content": message.content,
        "sent_by_me": True if message.sender_id == current_user_id else False
    } for message in messages_from_db]

    return jsonify({"messages": messages})


# 添加好友
@app.route('/sendFriendRequest', methods=['POST'])
@login_required
def sendFriendRequest():
    friend_username = request.form.get('username')
    
    # 查询数据库，查找该 username 对应的用户
    friend = User.query.filter_by(username=friend_username).first()
    
    if not friend:
        return jsonify(status="error", error="该用户不存在")

    # 创建好友请求记录
    
    if current_user.id == friend.id: #type: ignore
        return jsonify(status="error", error="无法添加自己为好友")
    
    friend_request = FriendRequest(sender_id=current_user.id, receiver_id=friend.id) #type: ignore
    db.session.add(friend_request)
    db.session.commit()
    
    return jsonify(status="success", message="好友请求已发送")

# 好友申请列表
@app.route('/friendRequests', methods=['GET'])
@login_required
def friendRequests():

    # 从数据库中获取所有未处理的好友请求
    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id).all() #type: ignore
    
    # 这里可以直接将它们传递给前端模板来展示
    return render_template('friend_requests.html', requests=pending_requests)

# 同意好友申请
@app.route('/acceptFriendRequest', methods=['POST'])
@login_required
def acceptFriendRequest():
    request_id = request.form.get('requestId')
    
    # 从数据库中找到这个好友请求
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request:
        return jsonify(status="error", error="请求不存在")

    # 获取双方的用户对象
    sender = User.query.get(friend_request.sender_id)
    receiver = User.query.get(friend_request.receiver_id)
    
    if not sender or not receiver:
        return jsonify(status="error", error="用户不存在")

    # 在friendship表中创建新的记录
    # 添加第一条记录
    db.session.execute(friendship.insert().values(user_id=sender.id, friend_id=receiver.id))
    # 添加第二条记录
    db.session.execute(friendship.insert().values(user_id=receiver.id, friend_id=sender.id))

    # 删除原始的FriendRequest记录
    db.session.delete(friend_request)
    # 提交数据库更改
    db.session.commit()
    return jsonify(status="success", message="好友已添加")

# 拒绝好友申请
@app.route('/rejectFriendRequest', methods=['POST'])
@login_required
def rejectFriendRequest():
    request_id = request.form.get('requestId')
    
    # 从数据库中找到这个好友请求
    friend_request = FriendRequest.query.get(request_id)

    if not friend_request:
        return jsonify(status="error", error="请求不存在")

    # 删除原始的FriendRequest记录
    db.session.delete(friend_request)

    # 提交数据库更改
    db.session.commit()

    return jsonify(status="success", message="已拒绝好友请求")

# 删除好友页面
@app.route('/deleteFriend', methods=['GET'])
@login_required
def deleteFriend():
    # 从数据库中获取所有好友
    friends_list = current_user.friends.all() #type: ignore
    
    # 这里可以直接将它们传递给前端模板来展示
    return render_template('delete_friends.html', friends_list=friends_list)

# 删除好友
@app.route('/comfirmDeleteFriend', methods=['POST'])
@login_required
def comfirmDeleteFriend():
    friend_id = request.form.get('friendId')
    # 获取当前用户ID
    current_user_id = current_user.id #type: ignore

    # 查找friendship表中的好友关系
    friendship_1 = db.session.query(friendship).filter(
        friendship.c.user_id == current_user_id,
        friendship.c.friend_id == friend_id
    ).delete()

    friendship_2 = db.session.query(friendship).filter(
        friendship.c.user_id == friend_id,
        friendship.c.friend_id == current_user_id
    ).delete()
    
    

    if not friendship_1 and not friendship_2:
        return jsonify(status="error", error="Friendship not found")
    
    # 查找与该好友的所有聊天记录
    messages = db.session.query(Message).filter(
        db.or_(
            db.and_(Message.sender_id == current_user_id, Message.receiver_id == friend_id),
            db.and_(Message.sender_id == friend_id, Message.receiver_id == current_user_id)
        )
    ).delete()

    if not friendship_1 and not friendship_2:
        return jsonify(status="error", error="Friendship not found")
    # 提交数据库更改
    db.session.commit()

    return jsonify(status="success", message="已删除好友并清除聊天记录")

# 退出登录
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))  # 重定向到登录页面或主页


if __name__ == '__main__':
    
    socketio.run(app, host="0.0.0.0", debug=True)