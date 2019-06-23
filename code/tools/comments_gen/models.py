from init import db
from datetime import datetime


class ComputeThinking(db.Model):
    __tablename__ = '计算思维'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class LogicThinking(db.Model):
    __tablename__ = '逻辑思维'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class ProblemAnalysis(db.Model):
    __tablename__ = '问题分析'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class Practice(db.Model):
    __tablename__ = '动手实践'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class Innovative(db.Model):
    __tablename__ = '创新思维'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class HomeWork(db.Model):
    __tablename__ = '作业情况'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class Performance(db.Model):
    __tablename__ = '课堂表现'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)


class Other(db.Model):
    __tablename__ = '其他'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=False)
