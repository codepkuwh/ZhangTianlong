from copy import deepcopy
from random import choice, shuffle

from flask import Flask, render_template, request

from init import app, db
from models import (ComputeThinking, HomeWork, Innovative, LogicThinking,
                    Other, Performance, Practice, ProblemAnalysis)


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""

    if request.method == "GET":
        return render_template("index.html")
    else:
        if request.form["type"] == "gen":
            # 填入的是评分，生成评价
            ct = ComputeThinking.query.filter_by(score=request.form["ComputeThinking"]).all()
            hw = HomeWork.query.filter_by(score=request.form["HomeWork"]).all()
            i = Innovative.query.filter_by(score=request.form["Innovative"]).all()
            lt = LogicThinking.query.filter_by(score=request.form["LogicThinking"]).all()
            # o = Other.query.filter_by(score=request.form["Other"]).all()
            pf = Performance.query.filter_by(score=request.form["Performance"]).all()
            pt = Practice.query.filter_by(score=request.form["Practice"]).all()
            pa = Practice.query.filter_by(score=request.form["ProblemAnalysis"]).all()

            ct = [i.comment for i in ct]
            hw = [i.comment for i in hw]
            lt = [i.comment for i in lt]
            i = [i.comment for i in i]
            pf = [i.comment for i in pf]
            pt = [i.comment for i in pt]
            pa = [i.comment for i in pa]

            output = [choice(ct), choice(hw), choice(i),
                      choice(pa), choice(pt), choice(pf), choice(lt)]
            shuffle(output)
            output = ", ".join(output)

        else:
            # 填入的是评价，存入数据库
            ct = ComputeThinking(score=request.form["ComputeThinkingScore"], comment=request.form["ComputeThinking"])
            hw = HomeWork(score=request.form["HomeWorkScore"], comment=request.form["HomeWork"])
            i = Innovative(score=request.form["InnovativeScore"], comment=request.form["Innovative"])
            lt = LogicThinking(score=request.form["LogicThinkingScore"], comment=request.form["LogicThinking"])
            o = Other(score=request.form["OtherScore"], comment=request.form["Other"])
            pf = Performance(score=request.form["PerformanceScore"], comment=request.form["Performance"])
            pt = Practice(score=request.form["PracticeScore"], comment=request.form["Practice"])
            pa = Practice(score=request.form["ProblemAnalysisScore"], comment=request.form["ProblemAnalysis"])
            comments = [ct, hw, i, lt, o, pf, pt, pa]
            comments = filter(lambda item: item.comment.strip(), comments)  # 空数据不提交
            # 拷贝一次，不然数据库里是空的，以后优化
            output = "提交成功, 您已提交: " + str([(c.score, c.comment) for c in deepcopy(comments)])
            db.session.add_all(comments)
            db.session.commit()

        return render_template("index.html", output=output)


# with app.app_context():
#     db.create_all()


app.run(debug=True)
