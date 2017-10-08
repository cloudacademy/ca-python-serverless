from __future__ import unicode_literals, print_function
import unittest
import boto3
import sys
import os
import uuid
import json
from os.path import dirname, join
from moto import mock_dynamodb2

from todo.api.create import create
from todo.api.update import update, handler
from todo.api.get import get_one
from dbconfig import init


class TestUpdateAPI(unittest.TestCase):
    @mock_dynamodb2
    def test_update_function(self):
        client, table = init()
        item = {'item': 'I need to finish this test!', 'completed': True}

        todo = create(client, '1', item, 'todo_test', ['completed', 'item'])
        todo['completed'] = False
        todo['item'] = 'Make all the tests!'

        update(client, '1', todo, table.table_name)
        todo_from_get = get_one(client, '1', todo['todoId'], table.table_name)

        # Verify it's not complete
        assert not todo_from_get['completed']
        assert todo_from_get['item'] == 'Make all the tests!'

    @mock_dynamodb2
    def test_update_handler(self):
        client, table = init()

        item = {
            'item': 'I need to finish this test!',
            'completed': True
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:username': '1'
                    }
                }
            }
        }

        todo = create(client, '1', item, 'todo_test', ['completed', 'item'])

        # make a change to the item
        todo['item'] = todo['item'] + '!!'
        # Set the body to the todo item.
        event['body'] = json.dumps(todo)

        results = handler(event, {})

        # Verify the results are not null
        assert results
        # Verify the status code is '200'
        assert 'statusCode' in results and results['statusCode'] == '200'
        # Verify the contents of the body
        assert 'body' in results
        body = json.loads(results['body'])
        # Verify that the UUIDs were set
        assert body['userId'] == '1'
        assert body['todoId'] and len(body['todoId']) == 36
        # Verify the items that a user can set were set correctly.
        assert body['item'] == json.loads(event['body'])['item']
        assert body['completed']


if __name__ == '__main__':
    unittest.main()