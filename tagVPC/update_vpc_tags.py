"""
Handles a tag change event to vpc.

If tag "Name" and/or "VPCname" changed, then set VPCname to Name. In addition,
set these other tags according to how defined in environment or the defaults
defined within this script:

    DataClassification
    ResourceOwner
    ProductFamily
    CustomerName

Name should not contain spaces.

Normal entry is via call to lambda_function(event, context), but can also be run for
debug purposes via command line.

Written by Ken Shaffer
"""
import logging
from pprint import pformat
import os
import boto3

###########################################################################
#   G L O B A L S
###########################################################################
myEnv = {}
logger = logging.getLogger()

HANDLED_TYPE = 'Tag Change on Resource'

"""defaultTagsHandled dict has keys which must match an environment variable if new value to be used."""
defaultTagsHandled = {
    'DataClassification': 'Company Confidential',
    'ResourceOwner': 'resource-owner@company.com',
    'ProductFamily': 'Product Family',
    'CustomerName': 'Customer Generic',
}
importantTags = set([ 'Name', 'VPCname'])

###########################################################################
def myDefaultEnv():
    """
    Returns dict of default environment variable settings
    """
    mydefaults = {}
    mydefaults.update(defaultTagsHandled)
    mydefaults.update({ 'LOGLEVEL': 'ERROR' })
    return mydefaults

###########################################################################
def setmyEnv(logLevel = None):
    """
    Fills global myEnv{} with defaults and current environment variable settings
    """
    # get default environment
    global myEnv
    myEnv.update(myDefaultEnv())

    # overlay with runtime environment
    myEnv.update(os.environ)

    # adjust LOGLEVEL if passed
    if logLevel:
        myEnv['LOGLEVEL'] = logLevel

###########################################################################
def mySampleEvent():
    """
    Return a sample event dict for debug purposes
    """
    sample = {
        "version": '0',
        "id": "deadbeef-dead-beef-dead-deadbeefdead",
        "detail-type": HANDLED_TYPE,
        "source": "aws.tag",
        "account": "012345678901",
        "time": "2018-09-25T00:46:47Z",
        "region": "us-west-2",
        "resources": [
            "arn:aws:ec2:us-west-2:123456789012:vpc/vpc-0123456789deadbeef"
        ],
        "detail": {
            "changed-tag-keys": [
                "xVPCname",
                "Name"
            ],
            "service": "ec2",
            "resource-type": "vpc",
            "version": 18.0,
            "tags": {
                'CustomerName': 'Customer Generic',
                'DataClassification': 'Company Confidential',
                'Name': 'my test vpc',
                'ProductFamily': 'Product Family',
                'ResourceOwner': 'resource-owner@company.com',
                'VPCname': 'overwritten-by-Name'
            }
        }
    }
    return sample

###########################################################################
class mySampleContext:
    """
    Return a sample context for debug purposes
    """
    def __init__(self):
        self.function_name = 'lambda_handler'
        self.function_version = '1.0'
        self.invoked_function_arn = "arn:aws:lambda:us-west-2:012345678901:function:myuserid-HelloWorld"
        self.memory_limit_in_mb = 128
        self.aws_request_id = 'deadbeef-dead-beef-dead-deadbeefdead'
        self.log_group_name = 'sample-log-group-name'
        self.log_stream_name = 'sample-log-stream-name'

    def get_remaining_time_in_millis(self, timeMillis=3000):
        return timeMillis

###########################################################################
def iCanHandle(event):
    """ Returns True if have an event that can be handled """
    logger.debug('got detail-type = %s' % str(event['detail-type']))
    return event['detail-type'] == HANDLED_TYPE and event['detail']['resource-type'] == 'vpc' and event['detail']['service'] == 'ec2'

###########################################################################
def setLogging():
    """ Turn on logging and set desired log level """
    logging_keys   = [ 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    logging_levels = [ logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL ]
    logging_levels_dict = dict( zip( logging_keys, logging_levels ))
    logging.basicConfig()
    if myEnv['LOGLEVEL'] not in logging_keys:
        myEnv.update({ 'LOGLEVEL': 'ERROR' })
        logger.error('Invalid LOGLEVEL passed in environment, use DEBUG, INFO, WARNING, ERROR, or CRITICAL')
    logger.setLevel(logging_levels_dict[myEnv['LOGLEVEL']])

###########################################################################
def logIfDebug(desc,someObj):
    """ Debug function to show dump of data passed """
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug(pformat([desc, someObj]))

###########################################################################
def getChangedTags(event):
    """ Return set of tags which changed that matter to us """
    myTags = importantTags
    changedTags = set(event['detail']['changed-tag-keys'])
    logIfDebug('Changed tags:',changedTags)
    return myTags.intersection(changedTags)

###########################################################################
def setNameVPCInEnv(event):
    """ Updates environment variables Name and VPCname with current value of Name tag """
    global myEnv

    tagName = 'CHANGE-ME'
    try:
        tagName = str(event['detail']['tags']['Name'])
    except Exception as e:
        logger.error('"Name" tag not present but is expected to be')

    newName = tagName.replace(' ', '-')
    myEnv['Name'] = newName
    myEnv['VPCname'] = newName

###########################################################################
def getTagKeys():
    """ get the tag names we later need to set """
    return importantTags.union(defaultTagsHandled.keys())

###########################################################################
def getKeyValueFromEnv(tags):
    """ get list of key/value dict from environment based on tags """
    keyValueList = []
    for key in tags:
        value = myEnv[key]
        keyValue = { 'Key': key, 'Value': value }
        keyValueList.append(keyValue)
    return keyValueList

###########################################################################
def getIdFromVpcArn(resources):
    """ given a vpc arn, strip off all but the id """
    vpcStr = 'vpc/'
    ids = []
    for resource in resources:
        if vpcStr in resource:
            index = resource.rfind(vpcStr)
            id = resource[index+len(vpcStr):]
            ids.append(id)
    return ids

###########################################################################
def writeTags(event, tags):
    """ write the tags to the aws resource """
    tagsAsKeyValue = getKeyValueFromEnv(tags)
    logIfDebug('Tags to change:',tagsAsKeyValue)
    try:
        ec2_client = boto3.client('ec2', region_name=event['region'])
        response = ec2_client.create_tags(
            DryRun=False,
            Resources=getIdFromVpcArn(event['resources']),
            Tags=tagsAsKeyValue
        )
        logIfDebug('create_tags response', response)
    except Exception as e:
        logger.error('writeTags: ' + e.message)

###########################################################################
def updateTags(event):
    """ Update the tags per defaults and/or environment """
    setNameVPCInEnv(event)
    tagKeys = getTagKeys()
    writeTags(event, tagKeys)

###########################################################################
def handleEvent(event, context):
    """ Handle the event containing changed tags that matter and if present, update them all """
    logIfDebug('Event:', event)
    changedTags = getChangedTags(event)
    if changedTags:
        updateTags(event)

###########################################################################
#   E N T R Y   V I A   C A L L   T O   L A M B D A   F T N
###########################################################################
def lambda_handler(event, context):
    """
    Entry point from AWS

    event varies based on what matched to cause this lambda handler to run
    context can tell you how much time is left before a timeout, how much memory is available, to name a couple

    """
    setmyEnv()
    setLogging()
    if iCanHandle(event):
        handleEvent(event, context)
    else:
        logging.debug('Not handling detail-type          "%s" ' % event['detail-type'])
        if event['detail-type'] == HANDLED_TYPE:
            logging.debug(' ' * 13 + 'detail service       "%s"' % event['detail']['resource-type'])
            logging.debug(' ' * 13 + 'detail resource type "%s"' % event['detail']['service'])

###########################################################################
#   M A I N   V I A   C L I
###########################################################################
if __name__ == '__main__':
    """
    If called via command line, make up an event and context, then call the handler
    """
    event = mySampleEvent()
    context = mySampleContext()
    lambda_handler(event, context)
