# EC2-CostManager

The EC2CostManager starts and stops AWS EC2 instances on a schedule you define based on an OP_MODE tag on your EC2 instances. The schedule is defined in UTC time.  The CloudFormation script creates two lamda functions, one IAM role and four CloudWatch Schedule rules.

Instructions:

1. Tag the instances you want to control with an OP_MODE tage of either BIZ_WEEK or DEV_WEEK.

2. Copy this utility into an S3 bucket in the same region as the EC2 instances you wish to control.

3. Create a CloudFormation stack using the EC2CostManager.json file

4. Specify the parameters requested by the EC2CostManager.json script


Charlie Christina
CharlesJChristina@gmail.com
