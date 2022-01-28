#importing necessary modules
import json, boto3
from botocore.exceptions import ClientError
import datetime
import pytz
import os

from logger import Logging

#Instantiating log Object
logg_object = Logging()
#Creating the custom based logger in the database
logg_object.create_logger()


class TimeClass:

    try: 
        def datetime_to_cron(self, schedule_time):

            '''
            This method converts timezone from IST to GMT to set an event in lambda function
            :param schedule_time: time in IST obtained from the user
            '''

            schedule_time1 = str(schedule_time)
            
            input_time = datetime.datetime.strptime(schedule_time1, '%Y-%m-%d %H:%M:%S')
            
            default_time = datetime.datetime(input_time.year, input_time.month, input_time.day, input_time.hour, input_time.minute)
            
            dt = pytz.timezone("GMT")
            
            dt = default_time.astimezone(dt)

            logg_object.print_log("Timezone conversion done","info")
            
            return f"cron({dt.minute} {dt.hour} {dt.day} {dt.month} ? {dt.year})"

    except Exception as e:
        logg_object.print_log('lambda.py(TimeClass)- Something went wrong ',"ERROR",e)

        raise Exception(e)

class Email:

    """"
    This class shall be used for Sheduling date time and send email to users address.
    """

    def __init__(self,region,Role_name,accountid,fun_name,rule_name,statementid,accesskeyid,secretkey):
        
        self.region=region
        self.Role_name=Role_name
        self.accountid=accountid
        self.fun_name=fun_name
        self.rule_name=rule_name
        self.statementid=statementid
        self.accesskeyid=accesskeyid
        self.secretkey=secretkey
            
    def role(self):
        """
        Description:This method is used for setting role for our aws lambda fuction. Means we are giving 
                    permissions for labda fuction that what other aws services can be used by lambdaa fuction
                    to complete our task. Here we are giving permission for lambda to use aws cloudwatch service and 
                    aws SES service. We have to write all thing in json format.
                    
                    params
                    region_name: it is region which we set for our aws account.
                    aws_access_key_id: secret credential 'key' of our aws account.
                    aws_secret_access_key: this is also secret credential of our aws account.
        """
#1.
        iam_client = boto3.client('iam',region_name=self.region,aws_access_key_id=self.accesskeyid,
                                  aws_secret_access_key=self.secretkey)
        trust_relationship_policy = {
            "Version": "2012-10-17",
            "Statement": [
             {
               "Sid": "",
               "Effect": "Allow",
               "Principal": {
                   "Service": "lambda.amazonaws.com"
               },
               "Action": "sts:AssumeRole"
             }
            ]
        }

#2.
        try:
            create_role_res = iam_client.create_role(
                RoleName=self.Role_name,
                AssumeRolePolicyDocument=json.dumps(trust_relationship_policy),
                Description='This ses + cloudwatch full access role',
                Tags=[
                    {
                    
                        'Key': 'Owner',
                        'Value': 'msb'
                    }
                ],
                )
        except ClientError as error:
            if error.response['Error']['Code'] == 'EntityAlreadyExists':
                logg_object.print_log("Role already exists... hence exiting from here","INFO")
                return('Role already exists... hence exiting from here','INFO')
            else:
                logg_object.print_log('Unexpected error occurred... Role could not be created',"INFO", error)
                return('Unexpected error occurred... Role could not be created', error)
        

#3.
    
        policy_json={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "autoscaling:Describe*",
                        "cloudwatch:*",
                        "logs:*",
                        "sns:*",
                        "iam:GetPolicy",
                        "iam:GetPolicyVersion",
                        "iam:GetRole"
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": "iam:CreateServiceLinkedRole",
                    "Resource": "arn:aws:iam::*:role/aws-service-role/events.amazonaws.com/AWSServiceRoleForCloudWatchEvents*",
                    "Condition": {
                        "StringLike": {
                            "iam:AWSServiceName": "events.amazonaws.com"
                        }
                    }
                },
                {
                
                    "Effect":"Allow",
                    "Action":[
                        "ses:*"
                    ],
                    "Resource":"*"
                }
            ]
        }

        policy_name = self.Role_name+ '_policy'
        policy_arn = ''

        try:
            policy_res = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_json)
            )
            policy_arn = policy_res['Policy']['Arn']
        except ClientError as error:
            if error.response['Error']['Code'] == 'EntityAlreadyExists':
                logg_object.print_log('Policy already exists... hence using the same policy','INFO')
                return('Policy already exists... hence using the same policy','INFO')
                policy_arn = 'arn:aws:iam::' + self.accountid + ':policy/' + policy_name
            else:
                logg_object.print_log('Unexpected error occurred... hence cleaning up',"ERROR", error)
                return('Unexpected error occurred... hence cleaning up',"ERROR", error)
                iam_client.delete_role(
                    RoleName= self.Role_name
                )
                logg_object.print_log('Role could not be created...',"ERROR", error)
                return( 'Role could not be created...', error)

        
#4.
        try:
                policy_attach_res = iam_client.attach_role_policy(
                    RoleName=self.Role_name,
                    PolicyArn=policy_arn
                )
        except ClientError as error:
            logg_object.print_log('Unexpected error occurred... hence cleaning up')
            return('Unexpected error occurred... hence cleaning up')
            iam_client.delete_role(
                RoleName= self.Role_name
            )
            logg_object.print_log('Role could not be created...',"ERROR", error)
            return ('Role could not be created...', error)
        logg_object.print_log('Role {0} successfully got created'.format(self.Role_name),'INFO')
        return ('Role {0} successfully got created'.format(self.Role_name))
    
    
    def lambda_function(self):
        iam_client = boto3.client('iam',region_name=self.region,aws_access_key_id=self.accesskeyid,
                                 aws_secret_access_key=self.secretkey)
        lambda_client = boto3.client('lambda',region_name=self.region,aws_access_key_id=self.accesskeyid,
                                    aws_secret_access_key=self.secretkey)
        with open('lambda3.zip', 'rb') as f:
            zipped_code = f.read()
        role = iam_client.get_role(RoleName=self.Role_name)
        try:
            response = lambda_client.create_function(
            FunctionName=self.fun_name,
            Runtime='python3.8',
            Role=role['Role']['Arn'],
            Handler='auto-email.lambda_handler',
            Code=dict(ZipFile=zipped_code),
            Timeout=300,)
            return (response)
        except Exception as e:
            logg_object.print_log("lambda_function unable to create error is","ERROR",e)
            return ("lambda_function unable to create error is",e)
            
    
    def Cloudwatch(self,schedule,Input):
        try:
            client_event=boto3.client('events',self.region,aws_access_key_id=self.accesskeyid,
                                     aws_secret_access_key=self.secretkey)
            rslt=client_event.put_rule(Name=self.rule_name,
                                       ScheduleExpression=schedule,
                                       State='ENABLED')
    
            rslt=client_event.put_targets(Rule=self.rule_name,
                                          Targets=[
                                              {
                                                  'Arn':"arn:aws:lambda:"+self.region+':'+self.accountid+':function:'+self.fun_name,
                                                  'Id':self.statementid,
                                                  'Input':Input
                                               
                                              }])
    
            lambda_clnt=boto3.client('lambda',self.region,aws_access_key_id=self.accesskeyid,
                                    aws_secret_access_key=self.secretkey)
            rslt=lambda_clnt.add_permission(FunctionName="arn:aws:lambda:"+self.region+':'+self.accountid+':function:'+self.fun_name,
                                       StatementId=self.statementid,
                                       Action='lambda:InvokeFunction',
                                       Principal='events.amazonaws.com',
                                       SourceArn="arn:aws:events:"+self.region+':'+self.accountid+':rule/'+self.rule_name)
            logg_object.print_log("Cloudwatch Event set successfully.","INFO")
            return ("event set successfully")
            
        except Exception as e:
            logg_object.print_log("Cloudwatch Event error courred.","ERROR",e)
            return ("event error",e)


