import json
import boto3
import logging
from datetime import datetime

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define audit table
auditTableName = 'EC2CostAuditTrail'
scalingStateTableName = 'EC2ScalingState'
dynamodb = boto3.resource('dynamodb')
scalingStateTable = dynamodb.Table(scalingStateTableName);
auditTable = dynamodb.Table(auditTableName);

#define the connection
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    print "Received event: " + json.dumps(event, indent=2)
    instanceId = event['detail']['instance-id']
    print "instanceId = " + instanceId

    #try to retrieve a record from the EC2 scaling state table
    try:
        resp = scalingStateTable.get_item(
            Key={
                'InstanceId': instanceId
            }
        )
    except Exception as e:
        print(e)
        print("Unable to find instance in state table".format(e))
        action = "DO_NOTHING"
    else:
        item = resp['Item']
        print item
        state = item['State']
        if state == "SCALING_UP":
            action = "SCALE_UP"
        elif state == "SCALING_DOWN":
            action = "SCALE_DOWN"
        else:
            action = "DO_NOTHING"

    #change the instance type of the instance based on the value in the state table
    print action
    if action != "DO_NOTHING":
        inst = ec2.Instance(instanceId)
        previousInstanceType = inst.instance_type
        for tag in inst.tags:
                if tag["Key"] == action:
                   newInstanceType = tag["Value"]
        print previousInstanceType, newInstanceType

        # Change the instance type
        response = inst.modify_attribute(Attribute='instanceType',Value=newInstanceType)

        #restart the instance
        startingUp = inst.start()
        print startingUp

        #insert a row into the EC2 audit table
        dt = datetime.now()
        try:
            resp = auditTable.put_item(
                Item={
                    'InstanceId': inst.id,
                    'TimeStamp': str(dt),
                    'OpMode': 'VERTICAL_PILOT',
                    'Action': action,
                    'PreviousInstanceType': previousInstanceType,
                    'NewInstanceType': newInstanceType})
        except Exception as e:
            print(e)
            print("Unable to insert data into DynamoDB table".format(e))

        #delete the row from the EC2 scalaing state table
        try:
            resp = scalingStateTable.delete_item(
                Key={
                    'InstanceId': instanceId,
                }
            )
        except Exception as e:
            print(e)
            print("Unable to delete instance state from state table".format(e))
    else:
        print "Not a scaling stop."