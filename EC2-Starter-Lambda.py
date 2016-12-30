import json
import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connection
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    print "Received event: " + json.dumps(event, indent=2)
    opMode = event['OpMode']
    print opMode

    # Use the filter() method of the instances collection to retrieve
    # all stopped EC2 instances.
    filters = [{
            'Name': 'tag:OP_MODE',
            'Values': [ opMode ]
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['stopped']
        }
    ]
    
    #filter the instances
    instances = ec2.instances.filter(Filters=filters)

    #locate all stopped instances
    StoppedInstances = [instance.id for instance in instances]
    
    #print the instances for logging purposes
    #print StoppedInstances 
    
    #make sure there are actually instances to start up. 
    if len(StoppedInstances) > 0:
        #perform the start
        startingUp = ec2.instances.filter(InstanceIds=StoppedInstances).start()
        print startingUp
    else:
        print "Nothing to start."