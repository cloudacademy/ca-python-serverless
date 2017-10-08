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
from todo.api.delete import delete, handler
from todo.api.get import get_one
from dbconfig import init


class TestUpdateAPI(unittest.TestCase):
    @mock_dynamodb2
    def test_delete_function(self):
        client, table = init()
        item = {'item': 'I need to finish this test!', 'completed': True}

        todo = create(client, '1', item, 'todo_test', ['completed', 'item'])
        delete(client, '1', todo['todoId'], table.table_name)
        todo_from_get = get_one(client, '1', todo['todoId'], table.table_name)

        # Verify it's an empty dict
        assert not todo_from_get

    @mock_dynamodb2
    def test_delete_handler(self):
        client, table = init()
        item = {'item': 'I need to finish this test!', 'completed': True}

        todo = create(client, '1', item, 'todo_test', ['completed', 'item'])

        event = {
            'queryStringParameters': {
                'id': todo['todoId']
            },
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:username': '1'
                    }
                }
            }
        }

        handler(event, {})
        todo_from_get = get_one(client, '1', todo['todoId'], table.table_name)

        # Verify it's an empty dict
        assert not todo_from_get


if __name__ == '__main__':
    unittest.main()