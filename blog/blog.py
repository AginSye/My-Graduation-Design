# coding=utf-8
from flask import Flask, session, render_template, request, redirect, url_for
import config
from models import User, Article, Comment
from exts import db
from decorators import login_limited

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


# 主页
@app.route('/')
def index():
    context = {
        'articles': Article.query.order_by('-time').all()
    }
    return render_template('index.html', **context)


# 热门页面
@app.route('/hot/')
def hot():
    context = {
        'articles': Article.query.order_by('-commentnum').all()
    }
    return render_template('hot.html', **context)


# 搜索页面
@app.route('/search/<search_target>')
def search(search_target):
    context = {
        'articles': Article.query.order_by('-time').all()
    }
    return render_template('search.html', search_target=search_target, **context)


# 搜索功能
@app.route('/myserarch', methods=['POST'])
def mysearch():
    search_target = request.form.get('search_name')
    return redirect(url_for('search', search_target=search_target))


# 登录页面
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username, User.password == password).first()
        if user:
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'用户名或密码错误，请重新登录'


# 注册页面
@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        phonenumber = request.form.get('phonenumber')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user1 = User.query.filter(User.phonenumber == phonenumber).first()
        user2 = User.query.filter(User.username == username).first()
        if user1 or user2:
            return u'该号码已被注册，请使用其他号码注册'
        else:
            if password1 != password2:
                return u'两次密码不一致，请核对后重新注册'
            else:
                user = User(phonenumber=phonenumber, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


# 注销功能
@app.route('/logout/')
def logout():
    session.pop('user_id')
    # del seesion('user_id')
    # session.clear()
    return redirect(url_for('login'))


# 加入user变量
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return{'user': user}
    return {}


# 发表博客
@app.route('/post/', methods=['GET', 'POST'])
@login_limited
def post():
    if request.method == 'GET':
        return render_template('post.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        block = request.form.get('block')
        article = Article(title=title, content=content, block=block, commentnum=0)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        article.author = user
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))


# 评论功能
@app.route('/add_comment', methods=['POST'])
@login_limited
def add_comment():
    content = request.form.get('comment_added')
    article_id = request.form.get('article_id')

    comment = Comment(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    comment.author = user
    article = Article.query.filter(Article.id == article_id).first()
    article.commentnum += 1
    comment.article = article
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', article_id=article_id))


# 删除博客功能
@app.route('/delete/<article_id>', methods=['POST'])
def delete(article_id):
    article_target = Article.query.filter(Article.id == article_id).first()
    db.session.delete(article_target)
    db.session.commit()
    return redirect(url_for('index'))


# 删除评论功能
@app.route('/deletecomment/<article_id>/<comment_id>', methods=['POST'])
def deletecomment(article_id, comment_id):
    article = Article.query.filter(Article.id == article_id).first()
    comment_target = Comment.query.filter(Comment.id == comment_id).first()
    article.commentnum -= 1
    db.session.delete(comment_target)
    db.session.commit()
    return redirect(url_for('detail', article_id=article_id))


# 查看博客页面
@app.route('/detail/<article_id>')
def detail(article_id):
    article_target = Article.query.filter(Article.id == article_id).first()
    return render_template('detail.html', article=article_target)


# 查看个人主页
@app.route('/home/<owner_id>')
def home(owner_id):
    user_target = User.query.filter(User.id == owner_id).first()
    context = {
        'articles': Article.query.order_by('-time').all()
    }
    return render_template('home.html', owner=user_target, **context)


# 修改密码
@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'GET':
        return render_template('change.html')
    else:
        user_id = session['user_id']
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        oldpassword = request.form.get('password3')
        user = User.query.filter(User.id == user_id, User.password == oldpassword).first()
        if password1 != password2:
            return u'两次密码不一致，请重新填写'
        else:
            if user:
                user.password = password1
                db.session.commit()
                return render_template('home.html', owner=user)
            else:
                return u'密码错误'


if __name__ == '__main__':
    app.run()
