from exts import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phonenumber = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    block = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    commentnum = db.Column(db.Integer, nullable=False)

    author = db.relationship('User', backref=db.backref('articles'))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime,default=datetime.now)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    article = db.relationship('Article', backref=db.backref('comments', order_by=id.desc()))
    author = db.relationship('User', backref=db.backref('comments'))
