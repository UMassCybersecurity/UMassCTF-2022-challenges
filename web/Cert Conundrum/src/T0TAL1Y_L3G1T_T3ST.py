import ctypes  # An included library with Python install.

#import everything from tkinter
from tkinter import *


# and import messagebox as mb from tkinter
from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk

#for setting random seed
from datetime import datetime
import random

import sys
import time

def slowprint(s):
	for c in s + '\n':
		sys.stdout.write(c)
		sys.stdout.flush()
		time.sleep(0.005)
    



# Create a GUI Window


def Mbox():
    random.seed(datetime.now())
    temp = tk.Tk()
    temp.title("Reason #5 you're a failure")
    width = temp.winfo_screenwidth()
    height = temp.winfo_screenheight()
    temp.geometry("300x150+0+49")
    lines = open("insults.txt").read().splitlines()
    ttk.Label(temp, text = random.choice(lines), wraplength=250, justify="center").pack()
    ttk.Button(temp, text = " OK ", command = temp.destroy).pack(side=tk.BOTTOM)
  
    for i in range(100):
        width_pos = random.randint(0,width) - 100
        height_pos = random.randint(0,height) - 100
        x = tk.Toplevel()
        x.title("Reason #" + str(i) + " you're a failure")
        x.geometry("300x150+" + str(width_pos) + "+" + str(height_pos))
        x.resizable(False, False)
        lines = open("insults.txt").read().splitlines()
        ttk.Label(x, text = random.choice(lines), wraplength=250, justify="center").pack()
        ttk.Button(x, text = " OK ", command = x.destroy).pack(side=tk.BOTTOM)
    
    temp.mainloop()


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
slowprint("Welcome to our totally legit AWS Certification Practice Exam. If multiple answers are expected, type them together with no spaces in alphabetical order. Now let's get to some practicing. Good luck!")
temp = {
    "I am testing my application and deploys it to AWS Lambda. To remain under the package size limit, the dependencies were not included in the deployment file. When testing the application through the console, the function won't work due to a missing dependencies issue.":
      ["Use the console to manually update the dependencies",
      "Set environment variables for the missing dependencies",
      "Attach a layer with the missing dependencies",
      "Request a package size limit increase and include the dependencies in the package.",
      "c"],
    "What are the steps to using the AWS CLI to launch a templatized serverless application":
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
    "An application currently uses multiple lambdas invoking one another as a large state machine? How could this application be simplified and managed more effectively":
    ["Combine all lambda functions into one large lambda",
    "Utilize Step Functions",
    "Amazon Elastic MapReduce",
    "Move the codebase out of lambda to an EC2 instance",
    "b"],
    "A developer is asked to implement caching in front of Amazon RDS. Which implementation below would work while maintaining maximum uptime and minimal costs?":
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
    ["Create a cross-account access role, and use sts:AssumeRole API"
    "Add an SSH key for another IAM user",
    "Create a user pool through Amazon Cognito",
    "Create a dedicated IAM access key and dm your friend it",
    "a"],
    "An application periodically reads data from an Amazon DynamoDB table. Every so often the applications crashes. Looking through the logs the error reads: 'ProvisionedThroughputExceeded'. How can this be fixed?":
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
		"Cancel the competition",
		"Set a capacity on the Auto Scaling group",
		"Create IAM credentials for each individual and cancel those who excessively utilize the infrastructure",
		"ac"],
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
		"b"],
		"What is the maximum batch size supported by AWS SQS for ReceiveMessage call as an event sources for AWS Lambda?":
		["20","40","100","10","d"]
  }
t_key = list(temp.keys())
print(len(t_key))
random.seed(str(datetime.now()))
random.shuffle(t_key)
i = 1
for key in t_key[:5]:
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
    Mbox()
    exit()
  i += 1
  print(" ")
  slowprint("CORRECT!")

slowprint("")
slowprint("You didn't think you could just get away with multiple choice questions did you? Every good cloud engineer should know some networking. Let's get to it! :)")
slowprint("")
slowprint(str(i) + ".) Suppose that TCP's current estimated values for the round trip time (estimatedRTT) and deviation in the RTT (DevRTT) are 260 msec and 12 msec, respectively (see Section 3.5.3 for a discussion of these variables). Suppose that the next three measured values of the RTT are 240 msec, 320 msec, and 240 msec respectively. What is the estimatedRTT after the third RTT?")
slowprint("")
i+=1
user_answer = input("What is your answer? ")
if float(user_answer) != float(262.15):
	Mbox()
	exit()
slowprint("CORRECT!")
slowprint(" ")
slowprint(str(i) + ".) What is the subnet mask for a network designed to have 1,164,375 hosts?")
slowprint("")
user_answer = input("What is your answer? ")
if user_answer != "255.244.0.0":
	Mbox()
	exit()
slowprint(" ")
slowprint("CORRECT!")
i+=1
slowprint(" ")
slowprint(str(i) + ".) Design a VLSM Network with an ip of 10.0.0.0 designed for 11 hosts. Please give each respective subnet ip in sequential order separated by a comma. Assume that connections are unstable and that you are using IPV10 for your protocols.")
time.sleep(10)
slowprint("Just kidding :)")
slowprint("I guess you deserve this for escaping my Cert Hell...")
slowprint("UMASS{D0E$_UD3My_C0UNT?}")
