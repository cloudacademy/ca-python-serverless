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
from todo.api.get import get_all, get_one, handler
from dbconfig import init


class TestGetAPI(unittest.TestCase):
    @mock_dynamodb2
    def test_get_one_function(self):
        client, table = init()
        item = {'item': 'I need to finish this test!', 'completed': True}

        todo = create(client, '1', item, table.table_name,
                      ['completed', 'item'])
        todo_from_get = get_one(client, '1', todo['todoId'], table.table_name)

        # Verify not null
        assert todo_from_get

        # Verify the record is correct
        assert todo_from_get['todoId'] == todo['todoId']
        assert todo_from_get['item'] == todo['item']
        assert todo_from_get['completed'] == todo['completed']
        assert todo_from_get['userId'] == todo['userId']

    @mock_dynamodb2
    def test_get_all_function(self):
        client, table = init()
        items = [{
            'item': 'A',
            'completed': True
        }, {
            'item': 'B',
            'completed': False
        }, {
            'item': 'C',
            'completed': True
        }]
        # The first two will be created for user '1' the third for '2'
        create(client, '1', items[0], table.table_name, ['completed', 'item'])
        create(client, '1', items[1], table.table_name, ['completed', 'item'])
        create(client, '2', items[2], table.table_name, ['completed', 'item'])

        todo_items = get_all(client, '1', table.table_name)

        assert len(todo_items) == 2
        # Verify items with content A or B are returned.
        assert all([i['item'] in ['A', 'B'] for i in todo_items])

    @mock_dynamodb2
    def test_get_handler_one(self):
        client, table = init()

        item = {'item': 'I need to finish this test!', 'completed': True}
        created = create(client, '1', item, table.table_name,
                         ['completed', 'item'])

        event = {
            'params': {
                'querystring': {
                    'id': created['todoId']
                }
            },
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:username': '1'
                    }
                }
            }
        }

        results = handler(event,
                          {})  # not using the context, so no need to mock it.
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
        assert body['item'] == created['item']
        assert body['completed']

    @mock_dynamodb2
    def test_get_handler_all(self):
        client, table = init()

        items = [{
            'item': 'A',
            'completed': True
        }, {
            'item': 'B',
            'completed': False
        }, {
            'item': 'C',
            'completed': True
        }]

        # The first two will be created for user '1' the third for '2'
        create(client, '1', items[0], table.table_name, ['completed', 'item'])
        create(client, '1', items[1], table.table_name, ['completed', 'item'])
        create(client, '2', items[2], table.table_name, ['completed', 'item'])

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:username': '1'
                    }
                }
            }
        }

        results = handler(event,
                          {})  # not using the context, so no need to mock it.
        # Verify the results are not null
        assert results
        # Verify the status code is '200'
        assert 'statusCode' in results and results['statusCode'] == '200'
        # Verify the contents of the body
        assert 'body' in results
        body = json.loads(results['body'])
        assert len(body) == 2
        # Verify that the correct records are returned
        assert all([i['userId'] == '1' for i in body])
        assert all([len(i['todoId']) == 36 for i in body])


if __name__ == '__main__':
    unittest.main()