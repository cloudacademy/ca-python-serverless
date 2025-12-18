#!/bin/bash

BUCKET=bucket
REGION=us-west-2
ACCOUNT_ID=account
STACK_NAME=TodoServerlessAPI

cat > ./s3_policy.json <<EOM
{
    "Version": "2012-10-17",
    "Id": "123",
    "Statement": [
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": "arn:aws:s3:::$BUCKET/*"
      }
    ]
 }
EOM

# Package SAM template
# Takes the local code, bundles it and then uploads it to S3
# then creates a new template with the updated code uri to deploy.
sam package --template-file template.yaml --s3-bucket $BUCKET --output-template-file packaged.yaml --region $REGION

# Deploy packaged SAM template
sam deploy --template-file ./packaged.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_IAM --region $REGION
