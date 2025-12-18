import boto3
import os
import json
from .helper import respond, parse_username_from_claims

def update(client, user_id, data, table_name):
    table = client.Table(table_name)
    # Update the item
    table.update_item(
        Key={'userId': user_id, 'todoId': data['todoId']},
        UpdateExpression='SET #item_text = :item_text, #completed = :completed',
        ExpressionAttributeNames={
            '#item_text': 'item',
            '#completed': 'completed'
        },
        ExpressionAttributeValues={
            ':item_text': data['item'],
            ':completed': data['completed']
        }
    )
    # Fetch the updated item to return it
    response = table.get_item(Key={'userId': user_id, 'todoId': data['todoId']})
    return response.get('Item', {})

def handler(event, context):
    table_name = os.getenv('TODO_TABLE', 'todo_test')
    client = boto3.resource('dynamodb')
    
    user_id = parse_username_from_claims(event)
    todo_id = None
    data = {}

    # Parse Body immediately (ID might be here)
    if event.get('body'):
        try:
            data = json.loads(event['body'])
        except:
            pass

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
        
        # Check JSON Body
        if not todo_id:
            todo_id = data.get('id') or data.get('todoId')

    if todo_id:
        # Ensure todoId is in the data object passed to update()
        data['todoId'] = todo_id
        result = update(client, user_id, data, table_name)
        return respond(None, result)
    
    return respond(None, {})