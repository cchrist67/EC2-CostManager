import json
import boto3
import logging
from datetime import datetime

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#define the connections
autoScaling = boto3.client('autoscaling')
auditTableName = 'ASCostMgmtAuditTrail'
dynamodb = boto3.resource('dynamodb')
auditTable = dynamodb.Table(auditTableName)

def lambda_handler(event, context):
    print "Received event: " + json.dumps(event, indent=2)
    action = event['Action']
    print action
    
    if action in ('SCALE_UP', 'SCALE_DOWN'):
        # find all the auto scaling groups with VERTICAL_PILOT_AS tag
        autoScalingGroups = autoScaling.describe_auto_scaling_groups()
    
        if len(autoScalingGroups['AutoScalingGroups']) > 0:
            for asg in autoScalingGroups['AutoScalingGroups']:
                asgName = asg['AutoScalingGroupName']
                print "Auto Scaling Group Name : " +asgName
    
                #find the auto scaling tags
                opMode = ''
                scaleDownLaunchConfig = ''
                scaleUpLaunchConfig = ''
                newLaunchConfig = ''
                for tag in asg['Tags']:
                    if tag['Key'] == 'OP_MODE':
                        opMode = tag['Value']
                    elif tag['Key'] == 'SCALE_DOWN_LAUNCH_CONFIG':
                        scaleDownLaunchConfig = tag['Value']
                        print "SCALE_DOWN_LAUNCH_CONFIG: " +scaleDownLaunchConfig
                    elif tag['Key'] == 'SCALE_UP_LAUNCH_CONFIG':
                        scaleUpLaunchConfig = tag['Value']
                        print "SCALE_UP_LAUNCH_CONFIG: " +scaleUpLaunchConfig
    
                #Set the new launch configuration
                if action == 'SCALE_DOWN':
                    newLaunchConfig = scaleDownLaunchConfig
                elif action == 'SCALE_UP':
                    newLaunchConfig = scaleUpLaunchConfig
    
                print "OP_MODE: " +opMode
                print "New Launch Config: " + newLaunchConfig
                if (opMode == 'VERTICAL_PILOT_AS') and (newLaunchConfig != ''):
                    launchConfig = autoScaling.describe_launch_configurations(LaunchConfigurationNames=[newLaunchConfig])
                    if len(launchConfig['LaunchConfigurations']) > 0:
                        # Change the auto scaling launch config
                        resp = autoScaling.update_auto_scaling_group(
                            AutoScalingGroupName=asgName,
                            LaunchConfigurationName=newLaunchConfig)
    
                        #log auto scaling action in auto scaling audit table
                        dt = datetime.now()
                        try:
                            resp = auditTable.put_item(
                                Item={
                                    'AutoScalingGroupName': asgName,
                                    'TimeStamp': str(dt),
                                    'Action': action,
                                    'NewLaunchConfig': newLaunchConfig})
                        except Exception as e:
                             print(e)
                             print("Unable to insert into " + auditTableName + " DynamoDB table".format(e))
    
                        #terminate the current instances in the AS group
                        for inst in asg['Instances']:
                            dt = datetime.now()
                            instanceId=inst['InstanceId']
                            print "Terminating instance: " +instanceId
                            resp = autoScaling.terminate_instance_in_auto_scaling_group(
                                InstanceId=instanceId,
                                ShouldDecrementDesiredCapacity=False)
    
                            #log instance terminations in auto scaling audit table
                            try:
                                resp = auditTable.put_item(
                                    Item={
                                        'AutoScalingGroupName': asgName,
                                        'TimeStamp': str(dt),
                                        'Action': 'terminated',
                                        'NewLaunchConfig': newLaunchConfig,
                                        'InstanceId': instanceId})
                            except Exception as e:
                                 print(e)
                                 print("Unable to insert into " + auditTableName + " DynamoDB table".format(e))
                    else:
                        print "Launch config " + newLaunchConfig + " does not exist."
                else:
                    print "Invalid or missing tags on auto scaling group - no action will be taken."
        else:
            print "No autoscaling groups found."
    else:
        print action + " is not a valid action."
