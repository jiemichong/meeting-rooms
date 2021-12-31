import json
import pytest


def call(client, path, method='GET', body=None):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PUT':
        response = client.put(path, data=json.dumps(body), headers=headers)
    elif method == 'PATCH':
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == 'DELETE':
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode('utf-8')),
        "code": response.status_code
    }


@pytest.mark.dependency()
def test_health(client):
    result = call(client, 'health')
    assert result['code'] == 200


@pytest.mark.dependency()
def test_get_all(client):
    result = call(client, 'rooms')
    assert result['code'] == 200
    assert result['json']['data']['rooms'] == [
        {
            "room_id": 1,
            "capacity": 5,
            "price": 100.0,
            "floor": 1
        },
        {
            "room_id": 2,
            "capacity": 20,
            "price": 200.0,
            "floor": 1
        },
        {
            "room_id": 3,
            "capacity": 20,
            "price": 200.0,
            "floor": 2
        },
        {
            "room_id": 4,
            "capacity": 50,
            "price": 300.0,
            "floor": 1
        },
        {
            "room_id": 5,
            "capacity": 5,
            "price": 100.0,
            "floor": 4
        }
    ]


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_valid(client):
    result = call(client, 'rooms/2')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "room_id": 2,
        "capacity": 20,
        "price": 200.0,
        "floor": 1
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_one_invalid(client):
    result = call(client, 'rooms/55')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Meeting room not found."
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_existing_room(client):
    result = call(client, 'rooms/1', 'PATCH', {
        "price": 88.0
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "room_id": 1,
        "capacity": 5,
        "price": 88.0,
        "floor": 1
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_update_nonexisting_room(client):
    result = call(client, 'rooms/555', 'PATCH', {
        "capacity": 2
    })
    assert result['code'] == 404


@pytest.mark.dependency(depends=['test_get_all'])
def test_create_no_body(client):
    result = call(client, 'rooms', 'POST', {})
    assert result['code'] == 500


@pytest.mark.dependency(depends=['test_get_all', 'test_create_no_body'])
def test_create_one_room(client):
    result = call(client, 'rooms', 'POST', {
        "capacity": 15,
        "price": 150.0,
        "floor": 3
    })
    assert result['code'] == 201
    assert result['json']['data'] == {
        "room_id": 6,
        "capacity": 15,
        "price": 150.0,
        "floor": 3
    }


@pytest.mark.dependency(depends=['test_create_one_room'])
def test_update_new_room(client):
    call(client, 'rooms', 'POST', {
        "capacity": 15,
        "price": 150.0,
        "floor": 3
    })
    result = call(client, 'rooms/6', 'PATCH', {
        "capacity": 100,
        "price": 130.0
    })
    assert result['code'] == 200
    assert result['json']['data'] == {
        "room_id": 6,
        "capacity": 100,
        "price": 130.0,
        "floor": 3
    }


@pytest.mark.dependency(depends=['test_get_all'])
def test_delete_room(client):
    result = call(client, 'rooms/2', 'DELETE')
    assert result['code'] == 200
    assert result['json']['data'] == {
        "room_id": 2
    }


@pytest.mark.dependency(depends=['test_delete_room'])
def test_deleted_room(client):
    call(client, 'rooms/2', 'DELETE')
    result = call(client, 'rooms/2', 'GET')
    assert result['code'] == 404
    assert result['json'] == {
        "message": "Meeting room not found."
    }
