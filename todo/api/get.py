import os
import boto3
from .helper import respond, parse_username_from_claims

def get_all(client, user_id, table_name):
    table = client.Table(table_name)
    result = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id)
    )
    return result.get('Items', [])

def get_one(client, user_id, todo_id, table_name):
    table = client.Table(table_name)
    result = table.get_item(Key={'userId': user_id, 'todoId': todo_id})
    return result.get('Item', {})

def handler(event, context):
    table_name = os.getenv('TODO_TABLE', 'todo_test')
    client = boto3.resource('dynamodb')
    
    user_id = parse_username_from_claims(event)
    todo_id = None

    # EXTRACTION
    if event:
        # 1. Query String
        qs = event.get('queryStringParameters')
        if qs and 'id' in qs:
            todo_id = qs['id']
        
        # 2. Path Param
        if not todo_id:
            pp = event.get('pathParameters')
            if pp and 'id' in pp:
                todo_id = pp['id']

        # 3. Test Structure
        if not todo_id:
            try:
                todo_id = event['params']['querystring']['id']
            except (KeyError, TypeError):
                pass

    if todo_id:
        result = get_one(client, user_id, todo_id, table_name)
    else:
        result = get_all(client, user_id, table_name)

    return respond(None, result)
