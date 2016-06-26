from flask import render_template, request,flash, redirect, url_for, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
import json
import psycopg2
import sqlalchemy
import pyotp
import logging
from model import Account, addAccount, session_commit
from app import app
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)

auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'loopme':
        return 'loopme'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 3,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task


@app.route('/')
def root():
    return app.send_static_file('index.html')


#READ
@app.route('/accounts' )
def account_all():
    accounts = Account.query.all()
    return jsonify([account.as_dict() for account in accounts])


# CREATE account
@app.route('/v1/otp' , methods=['POST'])
def otp_send():
    if not request.json.get('mobile'):
        abort(400)
    else:
        user_id = request.json.get('mobile')
        otp = pyotp.TOTP('base32secret3232').now()
        try:
            act = Account(user_id, otp)
            account_added = addAccount(act)
            if account_added:
                return jsonify({'result': 'created'})
            else:
                act_cur = Account.query.filter_by(user_id=user_id).first()
                print act_cur.as_dict()
                act_cur.otp = otp
                session_commit()
                return jsonify({'result': 'modified'})
        except Exception,e:
            print str(e)

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    return jsonify({'tasks': map(make_public_task, tasks)})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    return jsonify({'task': make_public_task(task[0])})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': make_public_task(task)}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': make_public_task(task[0])})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


