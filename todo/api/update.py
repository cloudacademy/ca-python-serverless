import os
import json
import uuid
import datetime
import boto3
from .helper import respond, parse_username_from_claims


def handler(event, context):
    data = None

    try:
        data = json.loads(event['body'])
    except Exception as ex:
        return respond(ex.args[0], None)  # Bail out and return an error
    
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
    result = update(client, user_id, data, table_name)

    return respond(None, result)


def update(client, user_id, data, table_name):
    ''' client is the dynamodb client
        user id is the id for the user that owns the record to update
        data is a dict for properties to store in dynamodb.
        table_name is the name of the dynamodb table where records are stored
    '''
    
    if 'item' not in data or 'completed' not in data:
        raise ValueError(
            'Cannot find any values to set. Expecting item or data.')

    if 'todoId' not in data:
        raise ValueError('You must set the todoId in order to update an item.')

    
    ex_attr_name = {}
    ex_attr_value = {}
    update_exp_lst = []

    if 'item' in data:
        ex_attr_name['#item'] = 'item'
        ex_attr_value[':i'] = data['item']
        update_exp_lst.append('#item = :i')

    if 'completed' in data:
        ex_attr_name['#completed'] = 'completed'
        ex_attr_value[':c'] = data['completed']
        update_exp_lst.append('#completed = :c')

    table = client.Table(table_name)

    result = table.update_item(
        ReturnValues='UPDATED_NEW',
        ExpressionAttributeNames=ex_attr_name,
        ExpressionAttributeValues=ex_attr_value,
        Key={
            'userId': user_id,
            'todoId': data['todoId'],
        },
        UpdateExpression='SET {}'.format(', '.join(update_exp_lst)))

    return result.get('Attributes', {})