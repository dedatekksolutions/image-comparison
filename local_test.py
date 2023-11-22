import json
from lambda_function import lambda_handler  # Import your Lambda function

# Simulate the Lambda event
event = {
    'body': json.dumps({
        'filename': ['01d98274-4d64-437d-8c77-bdb21be97804']
    })
}

# Simulate the Lambda context (can be an empty dictionary for this example)
context = {}

# Invoke the Lambda function
result = lambda_handler(event, context)

# Print the result
print(result)

