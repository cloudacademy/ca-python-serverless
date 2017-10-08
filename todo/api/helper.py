import json


def respond(err, res=None):
    # In a real app error messages shouldn't be sent to the end user.
    # This is a security concern. However, in a demo, for debugging, it's okay.
    body = {}
    if err:
        body = json.dumps({'error': err})
    else:
        body = json.dumps(res)
    return {
        'statusCode': '400' if err else '200',
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

def parse_username_from_claims(event):
    return event['requestContext']['authorizer']['claims']['cognito:username']