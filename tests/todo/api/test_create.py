from __future__ import unicode_literals, print_function
import unittest
import boto3
import sys
import os
import uuid
import json
from os.path import dirname, join
from moto import mock_dynamodb2

from todo.api.create import create, handler
from dbconfig import init


class TestCreateAPI(unittest.TestCase):
    @mock_dynamodb2
    def test_create_function(self):
        client, table = init()
        item = {
            'item': 'I need to finish this test!',
            'completed': True,
            'fake': 8675309
        }

        results = create(client, '1', item, table.table_name,
                         ['completed', 'item'])

        # Verify the results are not null
        assert results
        # Verify that the UUIDs were set
        assert results['userId'] == '1'
        assert results['todoId'] and len(results['todoId']) == 36
        # Verify the items that a user can set were set correctly.
        assert results['item'] == item['item']
        assert results['completed']
        # Verify that the fake attribute is removed by the whitelist
        assert 'fake' not in results

    @mock_dynamodb2
    def test_create_function_error(self):
        client, table = init()
        # Verify todo items with no item raise an error
        with self.assertRaises(ValueError):
            create(client, '1', {}, table.table_name, ['completed', 'item'])

    @mock_dynamodb2
    def test_create_handler(self):
        client, table = init()

        event = {
            'body':
            json.dumps({
                'item': 'I need to finish this test!',
                'completed': True,
                'fake': 8675309
            }),
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
        assert body['item'] == json.loads(event['body'])['item']
        assert body['completed']
        # Verify that the fake attribute is removed by the whitelist
        assert 'fake' not in body


if __name__ == '__main__':
    unittest.main()