# Lambda Webhook Listener - Posts to Slack
## POC in Python

Using Python 3.7 on [AWS Lambda](https://aws.amazon.com/lambda/).

Receives webhooks from Contentstack and pushes information to Slack.

**Not officially supported by Contentstack**

Step by step:
1. Create a Lambda function and an API Gateway in AWS Lambda. Based on these documentation articles:
   * [TUTORIAL: Build an API Gateway API with Lambda Non-Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started-lambda-non-proxy-integration.html).
    * We recommend enabling authentication on the API endpoint.
   * [AWS Lambda Deployment Package in Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html)
   * (Optional) Create tests in Lambda, using the contents of the `LambdaTests` folder.

2. Create a Slack app. Define where to post the message from the Webhook Listener:
  * When creating this POC, I used a private message to my Slack user. Verified it with `curl` before integrating with this script.

3. Environmental variables needed:
  * `SLACK_WEBHOOK_URL` -> The URL you can post directly to.
  * (Optional)`SLACK_WEBHOOK_URL_DEBUG` -> If you run the Lambda tests it posts to this channel in stead, e.g. in a personal message.


4. It's good to update both code and configuration in Lambda with `awscli`.
   * To update code via `awscli`:
    * install pip modules into a subdirectory like this:
      * `pip install --target ./package requests`.
    * Add all files and folders from the `package` folder (not the `package` folder itself) into a zip file with the `lambda_function.py` and upload to Lambda like this:
      * `aws lambda update-function-code --function-name ContentstackSlackPOC --zip-file fileb://function.zip`

5. Create a webhook in Contentstack, pointing to the API Gateway defined in step 1.
    * Currently supports publish, unpublish, delete and changing workflow stages on entry level.
