import os
import json
import requests

'''
Simple POC.

A webhook listener for Contentstack that sends to Slack.

Can be extended to do whatever, but in this case it sends a message based on workflow change.

Go to Slack. Create an app that posts to channel or user. Define an environmental variable SLACK_URL.

SLACK_URL = https://hooks.slack.com/services/<something>

'''

def getSlackUrl(event):
    if 'debug' in event:
        url = os.getenv('SLACK_URL_DEBUG')
    else:
        url = os.getenv('SLACK_URL')
    return url

regionMap = {
    'EU': 'https://eu-app.contentstack.com/#!/stack',
    'eu': 'https://eu-app.contentstack.com/#!/stack',
    'US': 'https://app.contentstack.com/#!/stack',
    'us': 'https://app.contentstack.com/#!/stack'
    }

def returnStatement(httpStatus=200, body='OK'):
    return {
        "statusCode": httpStatus,
        "body": json.dumps(body)
    }

def postToSlack(msg, url):
    text = {'text': msg}
    res = requests.post(url, data=json.dumps(text))
    if res.status_code == 200:
        return returnStatement
    return returnStatement(400, res.text)

def constructWorkflowMessage(event, region):
    eventType = event['event']
    contentType = event['data']['workflow']['content_type']['title']
    contentTypeUID = event['data']['workflow']['content_type']['uid']
    entryTitle = event['data']['workflow']['entry']['title']
    entryUid = event['data']['workflow']['entry']['uid']
    locale = event['data']['workflow']['locale']['code']
    workflowName = event['data']['workflow']['log']['name']
    triggerTime = event['triggered_at']
    stack = event['api_key']

    link = '{regionMap}/{stack}/content-type/{contentTypeUID}/{locale}/entry/{entryUid}/edit'.format(regionMap=regionMap[region], stack=stack, contentTypeUID=contentTypeUID, locale=locale, entryUid=entryUid)

    linkMsg = '<{link}|{entryTitle}>'.format(link=link, entryTitle=entryTitle)

    msg = '*Workflow {eventType}*\n\n{contentType} entry: {linkMsg} ({entryUid})\nLocale: {locale}\nChanged to workflow stage *{workflowName}*\nTrigger time: {triggerTime}'
    msg = msg.format(eventType=eventType, contentType=contentType, linkMsg=linkMsg, entryUid=entryUid, locale=locale, workflowName=workflowName, triggerTime=triggerTime)

    return msg

def constructEntryMessage(event, region):
    eventType = event['event']
    contentType = event['data']['content_type']['title']
    contentTypeUID = event['data']['content_type']['uid']
    entryTitle = event['data']['entry']['title']
    entryUid = event['data']['entry']['uid']
    locale = event['data']['entry']['locale']
    triggerTime = event['triggered_at']
    stack = event['api_key']

    if eventType == 'delete': # Entry deleted
        environmentName = None
        publishLocale = None
        link = '{regionMap}/{stack}/content-type/{contentTypeUID}/{locale}/entries'
        link = link.format(regionMap=regionMap[region], stack=stack, contentTypeUID=contentTypeUID, locale=locale)
    else: # Publish or unpublish
        environmentName = event['data']['environment']['name']
        publishLocale = event['data']['locale']
        link = '{regionMap}/{stack}/content-type/{contentTypeUID}/{locale}/entry/{entryUid}/edit'
        link = link.format(regionMap=regionMap[region], stack=stack, contentTypeUID=contentTypeUID, locale=locale, entryUid=entryUid)
    linkMsg = '<{link}|{entryTitle}>'.format(link=link, entryTitle=entryTitle)

    if environmentName: # Not delete entry (publish | unpublish)
        if publishLocale == locale:
            msg = '*Entry {eventType}*\n\n{contentType} entry: {linkMsg} ({entryUid})\nLocale: {locale}\nEnvironment: {environmentName}\nTrigger time: {triggerTime}'
            msg = msg.format(eventType=eventType, contentType=contentType, linkMsg=linkMsg, entryUid=entryUid, locale=locale, environmentName=environmentName, triggerTime=triggerTime)
        else:
            msg = '*Entry {eventType}*\n\n{contentType} entry: {linkMsg} ({entryUid})\nLocale: {locale} language has been published on {publishLocale}\nEnvironment: {environmentName}\nTrigger time: {triggerTime}'
            msg = msg.format(eventType=eventType, contentType=contentType, linkMsg=linkMsg, entryUid=entryUid, locale=locale, publishLocale=publishLocale, environmentName=environmentName, triggerTime=triggerTime)
    else: # Entry deleted
        msg = '*Entry {eventType}*\n\n{contentType} entry: {linkMsg} ({entryUid})\nLocale: {locale}\nEntry has been *DELETED*\nTrigger time: {triggerTime}'
        msg = msg.format(eventType=eventType, contentType=contentType, linkMsg=linkMsg, entryUid=entryUid, locale=locale, triggerTime=triggerTime)
    return msg

def constructMessage(event, region):
    module = event['module']
    if module == 'workflow':
        msg = constructWorkflowMessage(event, region)
    elif module == 'entry':
        msg = constructEntryMessage(event, region)
    else:
        msg = 'Unsupported webhook module.'

    return msg

def lambda_handler(event, context):
    '''
    This function receives webhooks from Contentstack.
    '''
    url = getSlackUrl(event)

    if 'region' in event['params']['header']:
        region = event['params']['header']['region']
    else:
        region = 'US'

    try:
        msg = constructMessage(event['body-json'], region)
        print(msg)
        print(url)
        postToSlack(msg, url)
        return returnStatement()
    except Exception as e:
        return returnStatement(400, str(e))
