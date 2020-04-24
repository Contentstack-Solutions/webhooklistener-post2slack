# Lambda Webhook Listener - Posts to Slack
## POC in Python

Using Python 3.7 on [AWS Lambda](https://aws.amazon.com/lambda/).

1. Create a Lambda function and an API Gateway in AWS Lambda. Based on these documentation articles:
   * [TUTORIAL: Build an API Gateway API with Lambda Non-Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started-lambda-non-proxy-integration.html).
    * We recommend enabling authentication on the API endpoint.
   * [AWS Lambda Deployment Package in Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
   * Create a test in Lambda, using e.g. the contents of the `webhookExample_WorkflowChange.json`.

2. Create a Slack app. Define where to post the message from the Webhook Listener:
  * When creating this POC, I used a private message to my Slack user. Verified it with `curl` before integrating with this script.

3. Environmental variables needed:
  * `SLACK_WEBHOOK_URL` -> The URL you can post directly to.


4. It's good to update both code and configuration in Lambda with `awscli`.
   * To update code via `awscli`:
    * install pip modules into a subdirectory like this:
      * `pip install --target ./package requests`.
    * Add all files and folders from the `package` folder into a zip file with the `lambda_function.py` and upload to Lambda like this:
      * `aws lambda update-function-code --function-name ContentstackSlackPOC --zip-file fileb://function.zip`

5. Create a webhook in Contentstack, pointing to the API Gateway defined in step 1. For this example, the webhook should trigger on any changes in workflow stages.
