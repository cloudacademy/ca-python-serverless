#!/bin/bash

REGION=us-west-2
STACK_NAME=TodoServerlessAPI
BUCKET=`aws s3api list-buckets --output json --query Buckets[*].Name --output text | tr '\t' '\n' | grep sambucket`
EXECUTION_ROLE=`aws iam list-roles --query Roles[*].Arn --output text | tr '\t' '\n' | grep SamExecutionRole`

# Set the account Id and execution role in the SAM template
sed -i "s#\[EXECUTION_ROLE\]#$EXECUTION_ROLE#g" template.yaml

# Package SAM template
# Takes the local code, bundles it and then uploads it to S3
# then creates a new template with the updated code uri to deploy.
sam package --template-file template.yaml --s3-bucket $BUCKET --output-template-file packaged.yaml --region $REGION

# Deploy packaged SAM template
sam deploy --template-file ./packaged.yaml --stack-name $STACK_NAME --capabilities CAPABILITY_IAM --region $REGION