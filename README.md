# EC2-CostManager

The EC2CostManager starts and stops AWS EC2 instances on a schedule you define based on an OP_MODE tag on your EC2 instances. The schedule is defined in UTC time.  The CloudFormation script creates two lamda functions (EC2-Starter-Lambda and a EC2-Stopper-Lambda), one IAM role (LambdaEC2Role), and four CloudWatch Schedule rules - two for DEV_WEEK instances and two for BIZ_WEEK instances (two stopper rules and two starter rules).

Instructions:

1. Tag the instances you want to control with an OP_MODE tage of either BIZ_WEEK or DEV_WEEK.

2. Copy this utility into an S3 bucket in the same region as the EC2 instances you wish to control.

3. Create a CloudFormation stack using the EC2CostManager.json file

4. Specify the parameters requested by the EC2CostManager.json script (again - specifiy your stop and start schedule in UTC time!)

5. Create the stack.


Charlie Christina
CharlesJChristina@gmail.com
