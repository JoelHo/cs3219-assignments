# Reference: https://realpython.com/token-based-authentication-with-flask/
# Reference: https://www.bacancytechnology.com/blog/flask-jwt-authentication

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SECRET_KEY'] = 'sOmEsEcReTkEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fakedb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.String, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(100))


@app.route('/entry', methods=['POST', 'GET'])
def entry():
    if request.method == 'POST':
        data = request.get_json()
        missing = []

        if 'id' not in data:
            missing.append('id')
        if 'author' not in data:
            missing.append('author')
        if 'title' not in data:
            missing.append('title')
        if 'content' not in data:
            missing.append('content')

        if len(missing) > 0:
            missing_str = ', '.join(missing)
            return make_response('Missing fields {}'.format(missing_str), 400, {
                'message': 'Missing fields {}'.format(missing_str)
            })

        new_entry = Entry(
            id=data['id'],
            author=data['author'],
            title=data['title'],
            content=data['content']

        )
        db.session.add(new_entry)
        try:
            db.session.commit()
            return jsonify({
                'message': 'new entry created',
                'entry': {
                    'id': new_entry.id,
                    'author': new_entry.author,
                    'title': new_entry.title,
                    'content': new_entry.content
                }
            })
        except IntegrityError:
            db.session.rollback()
            return make_response('Entry exists', 409, {
                'message': 'entry with id {id} already exists'.format(id=data['id'])
            })

    else:
        entries = Entry.query.all()

        output = [
            {
                'id': e.id,
                'author': e.author,
                'title': e.title,
                'content': e.content
            } for e in entries]

        return jsonify({'entries': output})


@app.route('/entry/<entry_id>', methods=['GET', 'PUT', 'DELETE'])
def delete_entry(entry_id):
    e = Entry.query.filter_by(id=entry_id).first()

    if not e:
        return jsonify({'message': 'entry does not exist'})

    if request.method == 'GET':
        return jsonify({
            'id': e.id,
            'author': e.author,
            'title': e.title,
            'content': e.content
        })
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return make_response('Missing fields to update', 400, {
                'message': 'Missing fields to update'
            })
        changed = []
        if 'id' in data:
            e.id = data['id']
            changed.append('id')
        if 'author' in data:
            e.author = data['author']
            changed.append('author')
        if 'title' in data:
            e.title = data['title']
            changed.append('title')
        if 'content' in data:
            e.content = data['content']
            changed.append('content')

        if len(changed) > 0:
            db.session.commit()
            changed_str = ', '.join(changed)
            return jsonify({'message': 'Updated fields {}'.format(changed_str)})
        else:
            return make_response('Missing fields to update', 400, {
                'message': 'Missing fields to update'
            })

    else:
        db.session.delete(e)
        db.session.commit()
        return jsonify({'message': 'entry deleted'})


if __name__ == '__main__':
    app.run(debug=True)
