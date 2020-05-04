import os
import json
import requests

'''
Simple POC.

A webhook listener for Contentstack that sends to Slack.

Can be extended to do whatever, but in this case it sends a message based on workflow change.

Go to Slack. Create an app that posts to channel or user. Define an environmental variable SLACK_URL.

SLACK_URL = https://hooks.slack.com/services/<something>

Note: US region is hardcoded in link.

'''

url = os.getenv('SLACK_URL')

def returnStatement(httpStatus=200, body='OK'):
    return {
        "statusCode": httpStatus,
        "body": json.dumps(body)
    }

def postToSlack(msg):
    text = {'text': msg}
    res = requests.post(url, data=json.dumps(text))
    if res.status_code == 200:
        return returnStatement
    return returnStatement(400, res.text)

def constructMessage(event):
    eventType = event['event']
    contentType = event['data']['workflow']['content_type']['title']
    contentTypeUID = event['data']['workflow']['content_type']['uid']
    entryTitle = event['data']['workflow']['entry']['title']
    entryUid = event['data']['workflow']['entry']['uid']
    locale = event['data']['workflow']['locale']['code']
    workflowName = event['data']['workflow']['log']['name']
    triggerTime = event['triggered_at']
    stack = event['api_key']

    link = 'https://app.contentstack.com/#!/stack/{stack}/content-type/{contentTypeUID}/{locale}/entry/{entryUid}/edit'.format(stack=stack, contentTypeUID=contentTypeUID, locale=locale, entryUid=entryUid)

    linkMsg = '<{link}|{entryTitle}>'.format(link=link, entryTitle=entryTitle)

    msg = '*Workflow {eventType}*\n\n{contentType} entry: {linkMsg} ({entryUid})\nLocale: {locale}\nChanged to workflow stage *{workflowName}*\nTrigger time: {triggerTime})'
    msg = msg.format(eventType=eventType, contentType=contentType, linkMsg=linkMsg, entryUid=entryUid, locale=locale, workflowName=workflowName, triggerTime=triggerTime)

    return msg

def lambda_handler(event, context):
    '''
    This function receives webhooks from Contentstack.
    '''
    try:
        msg = constructMessage(event)
        postToSlack(msg)
        return returnStatement()
    except Exception as e:
        return returnStatement(400, str(e))
