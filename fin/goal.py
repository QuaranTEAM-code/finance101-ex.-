from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort

from fin.auth import child_login_required
from fin.db import get_db

bp = Blueprint('goal', __name__ , url_prefix ='/goal')


@bp.route('/account')
def account():
    db = get_db()
    goals = db.execute(
            'SELECT go.goal_id , income_amt , goal_amt , saving_amt , emergency_amt , author_id , goal_name , child_username , time_left ,personal_amt, created '
            ' FROM goal go JOIN child c ON go.author_id = c.child_id'
            ' ORDER BY created DESC'
            ).fetchall()
    return render_template('goal/account.html' , goals=goals)


@bp.route('/create' , methods = ('GET' , 'POST'))
@child_login_required
def create():
    if request.method == 'POST':
        income_amt = int(request.form['income_amt'])
        goal_amt = int(request.form['goal_amt'])
        goal_name = (request.form['goal_name'])
        saving_amt = int(request.form['saving_amt'])
        #print(saving_amt)
        emergency_amt = int(request.form['emergency_amt'])
        


        error = None
        time_left = 0
        personal_amt = income_amt - (saving_amt + emergency_amt)

        if(income_amt < saving_amt):
            error = "Income Amount has to be greater than Saving Amount"

        if(income_amt < emergency_amt):
            error = "Income Amount has to be greater than Emergency Amount"

        db = get_db()

        if not goal_name:
            error = "GOAL NAME REQUIRED"

        elif db.execute(
                'SELECT goal_id FROM goal WHERE goal_name = ?',(goal_name,)).fetchone() is not None:
                error = 'Goal  {} is already registered'.format(goal_name)
    

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                    "INSERT INTO goal (income_amt , goal_amt , goal_name , saving_amt , emergency_amt , author_id , time_left , personal_amt)"
                    ' VALUES (? , ? , ? , ? , ? , ? , ? , ?)',
                    (income_amt , goal_amt , goal_name , saving_amt , emergency_amt , g.child['child_id'] ,time_left , personal_amt )
                    )
            db.commit()
            return redirect(url_for('goal.account'))

    return render_template('goal/create.html')




def get_goal(goal_id , check_author = True ):
    goals = get_db().execute(
        'SELECT go.goal_id, income_amt , goal_amt , saving_amt , emergency_amt , author_id , goal_name , child_username , time_left ,personal_amt, created'
        ' FROM goal go JOIN child c ON go.author_id = c.child_id'
        ' WHERE go.goal_id = ?',
        (goal_id, )
    ).fetchone()

    if goals is None:
        abort(404, "Goal id {0} doesn't exist.".format(goal_id))
    
    if check_author and goals['author_id'] != g.child['child_id']:
        abort(403)
    
    return goals



@bp.route('/<int:goal_id>/update', methods=('GET', 'POST'))
@child_login_required
def update(goal_id):
    goals = get_goal(goal_id)

    if request.method == 'POST':
        income_amt = int(request.form['income_amt'])
        goal_amt = int(request.form['goal_amt'])
        goal_name = (request.form['goal_name'])
        saving_amt = int(request.form['saving_amt'])
        #print(saving_amt)
        emergency_amt = int(request.form['emergency_amt'])
        


        error = None
        time_left = 0
        personal_amt = income_amt - (saving_amt + emergency_amt)

        if(income_amt < saving_amt):
            error = "Income Amount has to be greater than Saving Amount"

        if(income_amt < emergency_amt):
            error = "Income Amount has to be greater than Emergency Amount"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE goal SET income_amt = ?, goal_amt = ?, goal_name = ?, saving_amt = ?, emergency_amt = ? , time_left = ? , personal_amt = ?'
                ' WHERE goal_id = ?',
                (income_amt, goal_amt, goal_name , saving_amt , emergency_amt ,time_left , personal_amt , goal_id )
            )
            db.commit()
            return redirect(url_for('goal.account'))

    return render_template('goal/update.html', goals=goals)




@bp.route('/<int:goal_id>/delete', methods=('POST',))
@child_login_required
def delete(goal_id):
    get_goal(goal_id)
    db = get_db()
    db.execute('DELETE FROM goal WHERE goal_id = ?', (goal_id,))
    db.commit()
    return redirect(url_for('goal.account'))





