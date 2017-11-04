#!/bin/bash

REGION=us-west-2
STACK_NAME=TodoServerlessAPI
BUCKET=`aws s3api list-buckets --output json --query Buckets[*].Name --output text | tr '\t' '\n' | grep sambucket`
ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`

# Set the account Id in the SAM template
sed -i "s/\[ACCOUNT_ID\]/$ACCOUNT_ID/g" template.yaml

# Package SAM template
# Takes the local code, bundles it and then uploads it to S3
# then creates a new template with the updated code uri to deploy.
sam package --template-file template.yaml --s3-bucket $BUCKET --output-template-file packaged.yaml --region $REGION

# Deploy packaged SAM template
sam deploy --template-file ./packaged.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_IAM --region $REGION