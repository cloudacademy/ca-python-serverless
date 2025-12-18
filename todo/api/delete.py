import boto3
import os
from .helper import respond, parse_username_from_claims

def delete(client, user_id, todo_id, table_name):
    table = client.Table(table_name)
    table.delete_item(Key={'userId': user_id, 'todoId': todo_id})
    return {}

def handler(event, context):
    table_name = os.getenv('TODO_TABLE', 'todo_test')
    client = boto3.resource('dynamodb')
    
    user_id = parse_username_from_claims(event)
    todo_id = None

    # EXTRACTION
    if event:
        qs = event.get('queryStringParameters')
        if qs and 'id' in qs:
            todo_id = qs['id']
        
        if not todo_id:
            pp = event.get('pathParameters')
            if pp and 'id' in pp:
                todo_id = pp['id']

        if not todo_id:
            try:
                todo_id = event['params']['querystring']['id']
            except (KeyError, TypeError):
                pass

    if todo_id:
        delete(client, user_id, todo_id, table_name)
    
    return respond(None, {})