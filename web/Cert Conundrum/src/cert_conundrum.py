#import everything from tkinter
#from tkinter import *


# and import messagebox as mb from tkinter
#from tkinter import messagebox as mb
#import tkinter as tk
#from tkinter import ttk

#for setting random seed
from datetime import datetime
import random

import sys
import time

def slowprint(s):
	for c in s + '\n':
		sys.stdout.write(c)
		sys.stdout.flush()
		time.sleep(0.01)
    



# Create a GUI Window


# END OF THE PROGRAM
print("""   _                   _
 _( )                 ( )_
(_, |      __ __      | ,_)
   \'\    /  ^  \    /'/
    '\'\,/\      \,/'/'
      '\| []   [] |/'
        (_  /^\  _)
          \  ~  /
          /HHHHH\\
        /'/{^^^}\'\\
    _,/'/'  ^^^  '\'\\,_
   (_, |           | ,_)
     (_)           (_)""")
slowprint("Welcome to our totally legit AWS Certification Practice Exam. If multiple answers are expected, type them together with no spaces in alphabetical order (For example 'ac' if you thought choices a and c were the answer). Answers are not case sensitive. Now let's get to some practicing. Good luck!")
temp = {
    "I am testing my application and deploys it to AWS Lambda. To remain under the package size limit, the dependencies were not included in the deployment file. When testing the application through the console, the function won't work due to a missing dependencies issue.":
      ["Use the console to manually update the dependencies",
      "Set environment variables for the missing dependencies",
      "Attach a layer with the missing dependencies",
      "Request a package size limit increase and include the dependencies in the package.",
      "c"],
    "What are the steps to using the AWS Command Line Interface to launch a serverless application through a premade template?":
      ["Use AWS CloudFormation get-template then CloudFormation execute-change-set",
      "Use AWS CloudFormation package then CloudFormation deploy",
      "Use AWS CloudFormation validate-template then CloudFormation create-change-set",
      "Use AWS CloudFormation create-stack then CloudFormation update-stack",
      "b"],
    "I'm attempting to develop a web app (should still be mobile compatible) that needs authentication but also needs to be able to give users limited 'guest' access. What service can provide guest access to users?":
      ["Cognito with unauthenticated access enabled",
      "IAM temporary Credentials using AWS STS",
      "IAM with SAML integration",
      "Amazon Directory Service",
      "a"],
    "An application currently uses multiple lambdas invoking one another in succession? How could this application be simplified and managed more effectively?":
    ["Combine all lambda functions into one large lambda",
    "Utilize Step Functions",
    "Amazon Elastic MapReduce",
    "Move the codebase out of lambda to an EC2 instance",
    "b"],
    "I want to develop a cache in front of my Amazon Relational Database System. Which implementation below would work while minimizing downtime and costs?":
    ["Install Redis on an Amazon EC2 Instance",
    "Implement Amazon ElastiCache Memcached",
    "Migrate the database to Amazon Redshift",
    "Implement Amazon ElastiCache Redis in Cluster Mode",
    "d"],
    "I'm trying to get some static objects from my Amazon S3 bucket for my personal project. I'm expecting hundreds of GET requests a second as my site is quite popular on campus. What should I do to optimize my performance? (Choose all that apply)":
    ["Enable Amazon S3 cross-region replication",
    "Randomize Amazon S3 key name prefixes",
    "Configure Amazon S3 lifecycle rules",
    "Integrate Amazon CloudFront with S3",
    "bd"],
    "My friend needs temporary access to some resources on my other account. What is the most secure way I could achieve this?":
    ["Create a cross-account access role, and use sts:AssumeRole API",
    "Add an SSH key for another IAM user",
    "Create a user pool through Amazon Cognito",
    "Create a dedicated IAM access key and dm your friend it",
    "a"],
    "My application periodically reads data from an Amazon DynamoDB table. Every so often the applications crashes. Looking through the logs the error reads: 'ProvisionedThroughputExceeded'. How can this be fixed?":
    ["Create a new global secondary index for the table to help with the additional requests",
    "Try sending the request again",
    "Try the failed read requests with exponential backoff",
    "Request an API limit increase through AWS Support",
    "c"],
    "I've created a pretty large Lambda function but I can't seem to deploy it. I keep getting an error saying my deployment package is too big. How can I solve this?":
    ["Use a compression algorithm that is more efficient than ZIP",
    "Zip the file twice",
    "Break up the function into smaller parts",
    "Submit a limit increase request to AWS Support",
    "c"],
    "My web app utilizes Lambda functions to process events and update items in an on-prem MySQL server. Users have been reporting latency issues while updating lots of their personal information. What are some possible improvements that could be made? (Choose all that apply)":
    ["Process events in batches",
    "Migrate from an on-prem MySQL server to Amazon RDS",
    "Utilize AWS Connection pooling for the MySQL server",
    "Break up the Lambda function into smaller parts",
    "bc"],
    "My application stores images in an S3 bucket. S3 Event notifications are used to trigger a lambda function which helps pre-process the images before I perform some analysis on them. The processing of each image takes less than a second. How will AWS Lambda handle this traffic?":
    ["Lambda will scale out to execute the requests concurrently",
    "Lambda will handle requests sequentially",
    "Lambda will process multiple images in a single execution",
    "Lambda will add more resources in each execution to reduce processing time",
    "a"],
    "I've created an S3 bucket for my web app and enabled server across logging to monitor the bucket stored in the same bucket. After moving around 200kb of CSS files to the bucket. I checked the bucket the other day and now there were over 100 gbs of data. What is the MOST likely cause of the situation?":
    ["An S3 lifecycle policy has moved the entire CSS file to S3 Infrequent Access",
    "S3 replication was enabled on the bucket",
    "The CSS files were not compressed and S3 Versioning was enabled",
    "Logging into the same bucket caused exponential log growth",
    "d"],
    "I'm attempting to create a CTF Challenge on AWS and have enabled auto scaling to support the needs of my competitors. I am worried that someone may exploit my infrastructure and attempt to crash it or worse (I'm broke) run me up hundred's of dollers in bills. What are my options to prevent this? (Choose all that apply)":
		["Utilize AWS Cloudwatch to alert me when my spending goes over my budget",
		"Limit the number of competitors accessing my site at a time",
		"Set a capacity on the Auto Scaling group",
		"Create IAM credentials for each individual and cancel those who excessively utilize the infrastructure",
		"abc"],
		"Your IT Security department has mandated that all the traffic flowing in and out of EC2 instances needs to be monitored for potential malicious activity. The EC2 instances are launched in their own VPC. Which services would you use to achieve this?":
		["VPC Flow Logs",
		"Cloudwatch Metrics",
		"CloudTrail",
		"CloudMonitor",
		"a"],
		"You currently have some EC2 instances and want to restart them if the CPU usage goes beyond a certain threshold. How would you implement a potential solution?":
		["Create a CLI script that restarts the server at certain intervals",
		"Look at the Cloudtrail logs and parse for when to restart",
		"Create a CloudWatch metric which looks into the instance threshold, and assign this metric against an alarm to reboot the instance",
		"Use the AWS Config utility on the EC2 Instance to check for metrics and restart the server",
		"c"],
		"What is the maximum batch size supported by AWS SQS for ReceiveMessage call as an event sources for AWS Lambda?":
		["20","40","100","10","d"],
    "In an AWS CloudFormation template, what section of the root must be included to incorporate objects specified by the AWS SAM in addition to resources?":
    ["Globals","Conditions","Properties","Transform","d"],
    "When using Amazon Lex, bots can be directly or indirectly deployed to which of the following? (Choose all that apply)":
    ["Slack", "A Web App", "Twilio", "Microsoft Teams", "abcd"],
    "Which of the following are compute purchasing options? (Choose all that apply)":
    ["Dedicated","Reduced","Spot", "Savings Plans", "acd"],
    "I wanna create an S3 bucket with public read-only objects. How can I do this?":
    ["Set permission on upload",
    "Update the bucket policy",
    "Use IAM Roles",
    "S3 objects by default are public read-only so no action is needed", "b"],
    "Which of the following services would be best for transfering data across the country to various S3 buckets? (Choose all that apply)":
    ["Amazon Cloudfront",
    "Amazon Glacier",
    "Amazon Snowball",
    "Amazon Transfer Acceleration", 'cd'],
    "How far do EBS Volumes go out?":
    ["Virtual Private Cloud",
    "AWS Region",
    "Avaliablity Zone",
    "Placement Group",
    "c"],
    "How far do EC2 security groups reach out?":
    ["Placement Group",
    "VPC",
    "Avaliability Zone",
    "Region", "d"],
  }
t_key = list(temp.keys())
random.seed(str(datetime.now()))
random.shuffle(t_key)
i = 1
for key in t_key[:8]:
  slowprint(" ")
  slowprint(str(i) +".) " + str(key))
  slowprint(" ")
  slowprint("a. " + temp[key][0])
  slowprint("b. " + temp[key][1])
  slowprint("c. " + temp[key][2])
  slowprint("d. " + temp[key][3])
  slowprint(" ")
  answer = temp[key][4]
  user_answer = input("What is your answer? ")
  if answer != user_answer.lower():
    exit()
  i += 1
  print(" ")
  slowprint("CORRECT!")

slowprint("")
slowprint("You didn't think you could just get away with multiple choice questions did you? Every good cloud engineer should know some networking. Let's get to it! :)")
slowprint("")
slowprint(str(i) + ".) Suppose we are running TCP between two hosts. Each packet has an estimated round trip time of 260ms. The current deviation between each packet's round trip time is 12 msec. Looking at the round trip time of the next three packets, we get values of 240, 320, and 240 ms each. Calculate the estimated round trip time after the third packet.")
slowprint("")
i+=1
user_answer = input("What is your answer? ")
if float(user_answer) != float(262.15):
	exit()
slowprint(" ")
slowprint("CORRECT!")
slowprint(" ")
slowprint(str(i) + ".) What is the subnet mask for a network designed to have 1,164,375 hosts? (Please input in format NUMBER.NUMBER.NUMBER.NUMBER")
slowprint("")
user_answer = input("What is your answer? ")
if user_answer != "255.224.0.0":
	exit()
slowprint(" ")
slowprint("CORRECT!")
i+=1
slowprint(" ")
slowprint(str(i) + ".) Design a VLSM Network with an ip of 10.0.0.0 designed for 11 hosts. Please give each respective subnet ip in sequential order separated by a comma. Assume that connections are unstable and that you are using IPV10 for your protocols.")
time.sleep(30)
slowprint("Just kidding :)")
slowprint("I guess you deserve this for escaping my Cert Conundrum...")
slowprint("UMASS{D0E$_UD3My_C0UNT?}")
