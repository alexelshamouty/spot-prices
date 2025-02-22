# Spot Lambda

This Python script retrieves and analyzes AWS EC2 spot instance prices, generates visualizations, and uploads the results to an S3 bucket.

## Features

- Retrieves EC2 instance types and filters for Graviton-based and spot instances.
- Fetches spot price history for the last 10 days.
- Generates line charts for all instances and instances with 4 or fewer vCPUs using Plotly.
- Uploads the generated HTML files to an S3 bucket.

## Functions

### `calculate_instances_price()`
- Retrieves instance types and spot price history.
- Generates and saves HTML visualizations of spot prices.

### `upload_to_s3()`
- Uploads the generated HTML files to a specified S3 bucket.

### `handler(event, context)`
- Lambda handler function that calls `calculate_instances_price()` and `upload_to_s3()`.

## Usage

Deploy this script as an AWS Lambda function. 
You need the serverless framework.

From there just sls deploy and the framework will take care of the rest.