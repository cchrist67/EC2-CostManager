import json
import boto3
import logging
from datetime import datetime

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define audit table
auditTableName = 'EC2CostAuditTrail'
dynamodb = boto3.resource('dynamodb')
auditTable = dynamodb.Table(auditTableName);

#define the connection
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    print "Received event: " + json.dumps(event, indent=2)
    opMode = event['OpMode']
    print opMode

    # Use the filter() method of the instances collection to retrieve
    # all running EC2 instances.
    filters = [{
            'Name': 'tag:OP_MODE',
            'Values': [opMode]
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['running']
        }
    ]
    
    #print the instances for logging purposes
    #instances = ec2.instances.all()
    #for i in instances:
    #    print i.id, i.instance_type, i.state['Name']

    #filter the instances
    filteredInstances = ec2.instances.filter(Filters=filters)

    #locate all running instances
    runningInstances = [instance.id for instance in filteredInstances]
    
    #make sure there are actually instances to shut down. 
    if len(runningInstances) > 0:
        #perform the shutdown
        shuttingDown = ec2.instances.filter(InstanceIds=runningInstances).stop()
        print shuttingDown
        dt = datetime.now()
        #print dt
        for ri in runningInstances:
            # Insert instance information into EC2 Audit DynamoDB table
            try:
                resp = auditTable.put_item(
                    Item={
                        'InstanceId': ri,
                        'TimeStamp': str(dt),
                        'OpMode': opMode,
                        'Action': "stop",
                        'InstanceType': ec2.Instance(ri).instance_type})
            except Exception as e:
                 print(e)
                 print("Unable to insert data into DynamoDB table".format(e))
    else:
        print "Nothing to stop."