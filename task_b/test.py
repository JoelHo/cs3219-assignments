import pytest
import json
import os
from main import app, db, entry, delete_entry
db.create_all()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get(client):
    res = client.get('entry')

    response = json.loads(res.data)

    assert 'entries' in response

    assert len(response['entries']) == 0


def test_post(client):
    res = client.post('entry', json={
        'id': 1,
        'author': 'a',
        'title': 'b',
        'content': 'c'
    })

    response = json.loads(res.data)
    assert 'entry' in response
    assert 'message' in response
    assert 'new entry created' in response['message']

    assert 'id' in response['entry']
    assert '1' == response['entry']['id']

    assert 'author' in response['entry']
    assert 'a' == response['entry']['author']

    assert 'title' in response['entry']
    assert 'b' == response['entry']['title']

    assert 'content' in response['entry']
    assert 'c' == response['entry']['content']

    res = client.get('entry')
    response = json.loads(res.data)

    assert 'entries' in response

    assert 'id' in response['entries'][0]
    assert '1' == response['entries'][0]['id']

    assert 'author' in response['entries'][0]
    assert 'a' == response['entries'][0]['author']

    assert 'title' in response['entries'][0]
    assert 'b' == response['entries'][0]['title']

    assert 'content' in response['entries'][0]
    assert 'c' == response['entries'][0]['content']


def test_put(client):
    res = client.put('entry/1', json={
        'author': 'd',
        'title': 'e',
        'content': 'f'
    })

    response = json.loads(res.data)
    assert 'message' in response
    assert 'Updated fields author, title, content' in response['message']


def test_delete(client):
    res = client.get('entry')

    response = json.loads(res.data)

    assert len(response['entries']) == 1

    res = client.delete('entry/1')

    response = json.loads(res.data)
    assert 'message' in response
    assert 'entry deleted' in response['message']
