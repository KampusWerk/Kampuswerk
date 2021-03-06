from flask import render_template, request, flash, redirect, url_for, Blueprint, jsonify
from datetime import datetime, timedelta 
from flask_login import UserMixin, login_user, logout_user, current_user, login_required
#luke new imports###########################################################
from .oauth import OAuthSignIn
from .models import User, Bodyweight, HangboardWerk, KampusWerkout, CircuitMoves, Routes, Blocs
from app import db
from .forms import KampusForm, HangboardForm, CircuitForm, BlocForm, BodyweightForm, RoutesForm

import flask_excel as excel
from sqlalchemy import and_
#luke new imports end#####################################################

views = Blueprint("", __name__)

###################################################################################################

# @views.route('/kampustest', methods=['GET', 'POST'])
# def function():
#     return render_template('KAMPUSWERK.html')

# @views.route("/test", methods=['GET'])
# def test():
#     return "This is a Test!"

@views.route('/', methods=["GET","POST"])
def index():
    return render_template('index.html')

@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.index'))

@views.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@views.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('.index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('.index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('.index'))
######################################################################################################################

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


#############################################
############# VIEWS #########################
#############################################


@views.route("/circuits", methods=["GET", "POST"])
@login_required
def Circuit():
    form = CircuitForm()
    if form.validate_on_submit():
        timestamp=datetime.utcnow()

        circuitmove = CircuitMoves(current_user.nickname,  request.form['numberofmoves'], request.form['intensity'], request.form['werktime'], request.form['grade'], request.form['comments'], timestamp, current_user.id)
        db.session.add(circuitmove)
        db.session.commit()
        flash('You have successfully logged your circuit')

    else:
        flash_errors(form)

    return render_template("circuits.html", title="Time to get strong", form=form, circuit=CircuitMoves.query.all())
##########################################################


@views.route("/hangboard", methods=["GET", "POST"])
@login_required
def Hangboard():
    form = HangboardForm()
    if form.validate_on_submit():
        timestamp=datetime.utcnow()
        werk = HangboardWerk(current_user.nickname, request.form['board'], request.form['holds_used'], request.form['reps'], request.form['sets'], request.form['setrest'], request.form['arm_used'], request.form['hangtime'], request.form['resttime'], request.form['weight_kg'], timestamp, current_user.id)
        db.session.add(werk)
        db.session.commit()
        return "OK", 201
    else:
        flash_errors(form)
        return render_template("hangboard.html", title="Time to get strong", form=form, hangboard=HangboardWerk.query.all())


#part of the hangboard pages
@views.route("/timerwerk", methods=["GET","POST"])
def timer():
    return render_template("timerwerk.html")
#################################################################
@views.route("/climbing", methods=["GET", "POST"])
@login_required
def Climbing():
    form = RoutesForm()
    if form.validate_on_submit():
        timestamp=datetime.utcnow()

        routes = Routes(current_user.nickname, request.form['height'], request.form['intensity'], request.form['werktime'], request.form['grade'], request.form['angle'], request.form['venue'], request.form['style'], request.form['comments'],  timestamp, current_user.id)
        db.session.add(routes)
        db.session.commit()
        flash('You have successfully logged your route')

    else:
        flash_errors(form
)
    return render_template("climbing.html", title="Time to get strong", form=form, routes=Routes.query.all())
##########################################################
@views.route("/bouldering", methods=["GET", "POST"])
@login_required
def Bouldering():
    form = BlocForm()
    if form.validate_on_submit():
        timestamp=datetime.utcnow()

        blocs = Blocs(current_user.nickname, request.form['intensity'], request.form['werktime'], request.form['grade'], request.form['angle'], request.form['venue'], request.form['style'], request.form['comments'],  timestamp, current_user.id)
        db.session.add(blocs)
        db.session.commit()
        flash('You have successfully logged your blocs')

    else:
        flash_errors(form)

    return render_template("bouldering.html", title="Time to get strong", form=form, blocs=Blocs.query.all())
##########################################################

@views.route("/profile", methods=["GET", "POST"])
@login_required
def Profile():


    return render_template("profile.html", kampus=KampusWerkout.query.filter_by(user_id=current_user.id).all(),
     hangboard=HangboardWerk.query.filter_by(user_id=current_user.id).all(),
         circuitmoves=CircuitMoves.query.filter_by(user_id=current_user.id).all(),
          routes=Routes.query.filter_by(user_id=current_user.id).all(),
           blocs=Blocs.query.filter_by(user_id=current_user.id).all() )

############################################################


@views.route("/kampus", methods=["GET", "POST"])
@login_required
def Kampus():
    if request.method == "POST":
        timestamp=datetime.utcnow()
        kampuswerkout = KampusWerkout(current_user.nickname, request.form['kampuslog'], timestamp, current_user.id)
        db.session.add(kampuswerkout)
        db.session.commit()
        return render_template("kampus.html", kampus=KampusWerkout.query.filter_by(user_id=current_user.id).all())
    return render_template("kampus.html") #, kampus=KampusWerkout.query.all())


############################################################
####  NOT USED YET ############
# Cool round timer ############
#################################
@views.route("/intervaltimer", methods=["GET","POST"])
def intervals():
    return render_template("intervaltimer.html")

#### NOT USED YET - make benchmark page ##
##########################################
#need to create weight.html page~
@views.route("/weight", methods=["GET", "POST"])
@login_required
def Weight():
    form = BodyweightForm()
    if form.validate_on_submit():
        timestamp=datetime.utcnow()
        bodyweight = Bodyweight(current_user.nickname, request.form["bodyweight_kg"], request.form["notes"], timestamp, current_user.id)
        db.session.add(bodyweight)
        db.session.commit()
        flash('You have successfully logged your weight')
    else:
        flash_errors(form)
    return render_template("weight.html", form=form, bodyweight=Bodyweight.query.all())


############################################################

@views.route("/data/kampus", methods=["GET"])
@login_required
def Kampus_Data():
    data = [];
    for r in  KampusWerkout.query.filter_by(user_id=current_user.id).all():
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/kampus/7days", methods=["GET"])
@login_required
def Kampus_Data_7():

    data = [];
    for r in  KampusWerkout.query.filter(KampusWerkout.timestamp >= datetime.utcnow() -
     timedelta(weeks=1)).filter(KampusWerkout.user_id == current_user.id): 
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/hangboard", methods=["GET"])
@login_required
def Handboard_Data():
    data = [];
    for r in  HangboardWerk.query.filter_by(user_id=current_user.id).all():
        data.append(r.as_dict())
    return jsonify(data)



@views.route("/data/hangboard/7days", methods=["GET"])
@login_required
def Handboard_Data_7():

    data = [];
    for r in  HangboardWerk.query.filter(HangboardWerk.timestamp >= datetime.utcnow() -
     timedelta(weeks=1)).filter(HangboardWerk.user_id == current_user.id): 
        data.append(r.as_dict())
    return jsonify(data)





@views.route("/data/circuits", methods=["GET"])
@login_required
def Circuit_Data():
    data = [];
    for r in  CircuitMoves.query.filter_by(user_id=current_user.id).all():
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/circuits/7days", methods=["GET"])
@login_required
def Circuit_Data_7():

    data = [];
    for r in  CircuitMoves.query.filter(CircuitMoves.timestamp >= datetime.utcnow() -
     timedelta(weeks=1)).filter(CircuitMoves.user_id == current_user.id): 
        data.append(r.as_dict())
    return jsonify(data)


@views.route("/data/routes", methods=["GET"])
@login_required
def Route_Data():
    data = [];
    for r in  Routes.query.filter_by(user_id=current_user.id).all():
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/routes/7days", methods=["GET"])
@login_required
def Route_Data_7():

    data = [];
    for r in  Routes.query.filter(Routes.timestamp >= datetime.utcnow() -
     timedelta(weeks=1)).filter(Routes.user_id == current_user.id): 
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/blocs", methods=["GET"])
@login_required
def Blocs_Data():
    data = [];
    for r in  Blocs.query.filter_by(user_id=current_user.id).all():
        data.append(r.as_dict())
    return jsonify(data)

@views.route("/data/blocs/7days", methods=["GET"])
@login_required
def Bloc_Data_7():

    data = [];
    for r in  Blocs.query.filter(Blocs.timestamp >= datetime.utcnow() -
     timedelta(weeks=1)).filter(Blocs.user_id == current_user.id): 
        data.append(r.as_dict())
    return jsonify(data)

##########################################################
###failed excel port #####################################

@views.route("/charts")
@login_required
def charts():
    return render_template("charts.html")

@views.route("/export/hangboard", methods=['GET'])
@login_required
def doexport0():
    query_sets0 = HangboardWerk.query.filter_by(user_id=current_user.id).all()
    column_names0 = ['arm_used', 'board', 'hangtime', 'holds_used', 'name', 'reps', 'resttime', 'timestamp',   'user_id', 'weight_kg']
    return excel.make_response_from_query_sets(query_sets0, column_names0, "xls")

@views.route("/export/routes", methods=['GET'])
@login_required
def doexport1():
    query_sets1 = Routes.query.filter_by(user_id=current_user.id).all()
    column_names1 = ['angle', 'comments', 'grade', 'height', 'intensity', 'name', 'style', 'timestamp',   'user_id', 'venue', 'werktime']
    return excel.make_response_from_query_sets(query_sets1, column_names1, "xls")

@views.route("/export/kampus", methods=['GET'])
@login_required   
def doexport2():

    query_sets2 = KampusWerkout.query.filter_by(user_id=current_user.id).all()
    column_names2 = ['kampuslog', 'name', 'timestamp']
    return excel.make_response_from_query_sets(query_sets2, column_names2, "xls")

@views.route("/export/circuits", methods=['GET'])
@login_required
def doexport3():
    query_sets3 = CircuitMoves.query.filter_by(user_id=current_user.id).all()
    column_names3 = ['comments', 'grade', 'intensity', 'name', 'numberofmoves', 'timestamp',  'werktime']
    return excel.make_response_from_query_sets(query_sets3, column_names3, "xls")

@views.route("/export/blocs", methods=['GET']) 
@login_required
def doexport4():
    query_sets4 = Blocs.query.filter_by(user_id=current_user.id).all()
    column_names4 = ['angle', 'comments', 'grade', 'intensity', 'name', 'style', 'timestamp',   'venue', 'werktime']
    return excel.make_response_from_query_sets(query_sets4, column_names4, "xls")