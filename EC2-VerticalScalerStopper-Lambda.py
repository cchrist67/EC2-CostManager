import json
import boto3
import logging
from datetime import datetime

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define audit table
dynamodb = boto3.resource('dynamodb')
scalingStateTableName = 'EC2ScalingState'
scalingStateTable = dynamodb.Table(scalingStateTableName);

#define the connection
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    print "Received event: " + json.dumps(event, indent=2)
    opMode = event['OpMode']
    action = event['Action']
    print opMode, action

    if opMode == 'VERTICAL_PILOT':
        # Use the filter() method of the instances collection to retrieve
        # all EC2 instances with an OP_MODE of VERTICAL_PILOT and action tag.
        filters = [{
                'Name': 'tag:OP_MODE',
                'Values': [ opMode ]
            },
            {
                'Name': 'tag:'+action, 
                'Values': ['*']
            },
            {
                'Name': 'instance-state-name', 
                'Values': ['running']
            }
        ]
    
        #print the instances for logging purposes
        instances = ec2.instances.all()
        for i in instances:
            print i.id, i.instance_type, i.state['Name'] 
    
        #filter the instances
        filteredInstances = ec2.instances.filter(Filters=filters)
    
        #locate all instances to scale
        scaleInstances = [instance.id for instance in filteredInstances]
        
        #print the instances for logging purposes
        print scaleInstances 
        
        #make sure there are actually instances to scale. 
        if len(scaleInstances) > 0:
            #perform the stop
            shuttingDown = ec2.instances.filter(InstanceIds=scaleInstances).stop()
            print shuttingDown
    
            dt = datetime.now()
            print dt
            for fi in scaleInstances:
                inst = ec2.Instance(fi)
                if action == "SCALE_DOWN":
                	state = 'WAITING_TO_SCALE_DOWN'
                else:
                	state = 'WAITING_TO_SCALE_UP'
                # Insert instance information into EC2 Scaling State DynamoDB table
                try:
                    resp = scalingStateTable.put_item(
                        Item={
                            'InstanceId': inst.id,
                            'State': state,
                            'TimeStamp': str(dt)})
                except Exception as e:
                     print(e)
                     print("Unable to insert data into DynamoDB table".format(e))
        else:
            print "Nothing to " + action
    else:
        print opMode + " is not a valid OP_MODE for this function."
        if opMode == 'VERTICAL_PILOT_AS':
            print "For vertical scaling of an auto scaling group, use AS-VerticalScaler-Lambda."