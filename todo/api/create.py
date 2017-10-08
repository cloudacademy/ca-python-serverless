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

    # Make sure users don't add more properties than they should
    # A whitelist will ensure that any property non in this list is removed
    whitelist = ['completed', 'item']
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
    result = create(client, user_id, data, table_name, whitelist)

    return respond(None, result)


def create(client, user_id, data, table_name, whitelist):
    ''' client is the dynamodb client
        user id is the id for the user that owns the record to update
        data is a dict for properties to store in dynamodb.
        table_name is the name of the dynamodb table where records are stored
        whitelist is a list of properties that users are allowed to edit for their own records.
    '''
    if 'item' not in data:
        raise ValueError('The todo item is missing from the data dictionary.')

    table = client.Table(table_name)
    # Create a new dict that contains just whitelisted properties.
    whitelisted_data = {k: v for k, v in data.items() if k in whitelist}

    whitelisted_data['userId'] = user_id
    whitelisted_data['todoId'] = str(uuid.uuid4())
    whitelisted_data['created'] = str(datetime.datetime.utcnow())

    # Some people like to create items they've already completed
    # It's a way to show what they've already accomplished.
    # To each their own
    if 'completed' not in whitelisted_data:
        whitelisted_data['completed'] = False

    table.put_item(Item=whitelisted_data)

    return whitelisted_data