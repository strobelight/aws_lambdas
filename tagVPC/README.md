# update\_vpc\_tags

## NAME
    update_vpc_tags - Handles a tag change event to vpc.

## FILE
    tagVPC/update_vpc_tags.py

## DESCRIPTION
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

## CLASSES
    mySampleContext
    
    class mySampleContext
     |  Return a sample context for debug purposes
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |  
     |  get_remaining_time_in_millis(self, timeMillis=3000)

## FUNCTIONS
    getChangedTags(event)
        Return set of tags which changed that matter to us
    
    getIdFromVpcArn(resources)
        given a vpc arn, strip off all but the id
    
    getKeyValueFromEnv(tags)
        get list of key/value dict from environment based on tags
    
    getTagKeys()
        get the tag names we later need to set
    
    handleEvent(event, context)
        Handle the event containing changed tags that matter and if present, update them all
    
    iCanHandle(event)
        Returns True if have an event that can be handled
    
    lambda_handler(event, context)
        Entry point from AWS
        
        event varies based on what matched to cause this lambda handler to run
        context can tell you how much time is left before a timeout, how much memory is available, to name a couple
    
    logIfDebug(desc, someObj)
        Debug function to show dump of data passed
    
    myDefaultEnv()
        Returns dict of default environment variable settings
    
    mySampleEvent()
        Return a sample event dict for debug purposes
    
    setLogging()
        Turn on logging and set desired log level
    
    setNameVPCInEnv(event)
        Updates environment variables Name and VPCname with current value of Name tag
    
    setmyEnv(logLevel=None)
        Fills global myEnv{} with defaults and current environment variable settings
    
    updateTags(event)
        Update the tags per defaults and/or environment
    
    writeTags(event, tags)
        write the tags to the aws resource

## DATA
    HANDLED_TYPE = 'Tag Change on Resource'
    defaultTagsHandled = {'CustomerName': 'Customer Generic', 'DataClassificati...
    importantTags = set(['Name', 'VPCname'])
    logger = <logging.RootLogger object>
    myEnv = {}


