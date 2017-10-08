from __future__ import unicode_literals, print_function
import boto3
import os
from moto import mock_dynamodb2


def init():
    ''' Creates the databases and returns the client and the table 
    '''
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = os.getenv('TODO_TABLE', 'todo_test')

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'userId',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'todoId',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[{
            'AttributeName': 'userId',
            'AttributeType': 'S'
        }, {
            'AttributeName': 'todoId',
            'AttributeType': 'S'
        }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        })

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    assert table.table_status == 'ACTIVE'

    return dynamodb, table