# EC2-CostManager

The EC2CostManager starts and stops AWS EC2 instances on a schedule you define based on an OP_MODE tag on your EC2 instances. The schedule is defined in UTC time.  

The CloudFormation script creates:

A. Four Lambda functions: (EC2-Starter-Lambda, EC2-Stopper-Lambda, EC2-VerticalScalerStoper-Lamda, EC2-VerticalScalerRestarter-Lamda)

B. One IAM role (LambdaEC2Role)

C. Seven CloudWatch Schedule rules (BIZ_WEEK-start, BIZ_WEEK-stop, DEV_WEEK-start, DEV_WEEK-stop, VERTICAL_PILOT-scale_down, VERTICAL_PILOT-scale_up, VERTICAL_PILOT-restart)

Instructions:

1. Tag the instances you want to control with an OP_MODE tage of either BIZ_WEEK, DEV_WEEK or VERTICAL_SCALE (VERTICAL_SCALE also requires SCALE_UP and SCALE_DOWN tags with the instance type for each scalingaction).

2. Copy this utility into an S3 bucket in the same region as the EC2 instances you wish to control.

3. Create a CloudFormation stack using the EC2CostManager.json file

4. Specify the parameters requested by the EC2CostManager.json script (again - specifiy your stop and start schedule in UTC time!)

5. Create the stack.


Charlie Christina
CharlesJChristina@gmail.com
