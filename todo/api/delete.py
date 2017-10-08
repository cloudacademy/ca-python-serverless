import os
import json
import uuid
import datetime
import boto3
from boto3.dynamodb.conditions import Key
from .helper import respond, parse_username_from_claims


def handler(event, context):
    ''' The delete handler '''
    table_name = os.getenv('TODO_TABLE',
                           'todo_test')  # Table from env vars or todo_test
    region_name = os.getenv('AWS_REGION',
                            'us-east-1')  # Region from env vars or east 1
    client = boto3.resource('dynamodb', region_name=region_name)
    # User id is set by API Gateway once a user is authenticated.
    # The user can't fake this setting...in theory.
    # Meaning this should be the actual logged in user.
    # Never trust a userID supplied by a user for security reasons.
    # Assume all users are malicious haxors looking to 'pwn all ur nodes'
    user_id = parse_username_from_claims(event)
    todo_id = None
    
    try:
        event['queryStringParameters']['id']
    except:
        return respond('Missing the todo item id', None)        

    delete(client, user_id, todo_id, table_name)

    return respond(None, {'deleted': True})


def delete(client, user_id, todo_id, table_name):
    ''' client is the dynamodb client
        user id is the id for the user that owns the record to update
        todo_id is the id for the todo list item
        table_name is the name of the dynamodb table where records are stored
    '''
    table = client.Table(table_name)
    table.delete_item(Key={'userId': user_id, 'todoId': todo_id})
