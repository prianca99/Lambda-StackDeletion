import boto3
import time
import datetime
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#notification_date = current_date - datetime.timedelta(days=7)

def Delete_Stack(stackname):
	client = boto3.client('cloudformation')
	
	deleting_stack = client.delete_stack(StackName = stackname)
	if not deleting_stack['ResponseMetadata']['HTTPStatusCode'] == 200:
		logger.error("Stack Deletion  Failed for %d" ,stackname)
		
def Send_Notification(stackname, notifying_stacks):
###############################HTml Report Content############################
	report = "<html>" 
	report+= "<head>" 
	report+= "<meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>" 
	report+= '<title>AWS Stack Status Report</title>' 
	report+= '<STYLE TYPE="text/css">' 
	report+=  "<!--" 
	report+=  "td {" 
	report+=  "font-family: Tahoma;" 
	report+=  "font-size: 11px;" 
	report+=  "border-top: 1px solid #999999;" 
	report+=  "border-right: 1px solid #999999;" 
	report+=  "border-bottom: 1px solid #999999;" 
	report+=  "border-left: 1px solid #999999;" 
	report+=  "padding-top: 0px;" 
	report+=  "padding-right: 0px;" 
	report+=  "padding-bottom: 0px;" 
	report+=  "padding-left: 0px;" 
	report+=  "}" 
	report+=  "body {" 
	report+=  "margin-left: 5px;" 
	report+=  "margin-top: 5px;" 
	report+=  "margin-right: 0px;" 
	report+=  "margin-bottom: 10px;" 
	report+=  "" 
	report+=  "table {" 
	report+=  "border: thin solid #000000;" 
	report+=  "}" 
	report+=  "-->" 
	report+=  "</style>" 
	report+= "</head>" 
	report+= "<body>" 
	report+=  "<table width='70%'>" 
	report+=  "<tr bgcolor='#E62D8B'>" 
	report+=  "<td colspan='7' height='25' align='center'>" 
	report+=  "<font face='tahoma' color='#ffffff' size='5'><strong>AWS Stack Termination Event</strong></font>" 
	report+=  "</td>" 
	report+=  "</tr>" 
	report+=  "</table>" 
	############ Header ###########
	report+=  "<table width='70%'>" 
	report+=  "<tr bgcolor='#fed9fd'>" 
	report+=  "<td bgcolor= '#E62D8B' width='5%' colspan='2' size='5' align='center'>"
	report+=  "<font face='tahoma' color='#ffffff' size='2'><strong>Stacks Affected</strong></font>"
	report+=  "</td>"
	for sevent in notifying_stacks:
		report+= "</tr>"
		report+=  "<tr bgcolor='#fed9fd'>" 
		report+=  "<td bgcolor= '#ffffff' width='5%' colspan='2' size='5' align='center'>"
		report+=  "<font face='tahoma' color='#ffffff' size='2'><strong>&nbsp</strong></font>"
		report+=  "</td>"
		report+= "</tr>"
		report+=  "<tr bgcolor='#fed9fd'>" 
		report+=  "<td bgcolor= '#fed9fd' width='5%' align='center'><b>" + stackname + "</b></td>"
		report+= "</tr>"
		report+= "</tr>"
		report+=  "<tr bgcolor='#fed9fd'>" 
		report+=  "<td bgcolor= '#fed9fd' width='5%' align='center'><b>" + sevent + "</b></td>" 
		report+= "</tr>"
		
	############################################Close HTMl Tables###########################
	report+=  "</table>" 
	report+= "</body>" 
	report+= "</html>" 
	########################################################################################
	#############################################Send Email#################################
	subject="Alert: Stacks Terminating in 7 days"
	ses_client = boto3.client('ses')
	response = ses_client.send_email(Source='xyz@abc.com',Destination={'ToAddresses': ['xyz@abc.com']},Message={'Subject': {'Data': subject,'Charset': 'UTF-8'},'Body': {'Html': {'Data': report,'Charset': 'UTF-8'}}})

	
	
def Get_The_Details_And_Delete():
	client = boto3.client('cloudformation')
	current_date = datetime.datetime.today().date()
	stack_list=[]
	retirement_date = []
	notifying_stacks = []
	for stackname in stack_list:
		cf_details = client.describe_stacks(StackName = stackname)['Stacks']
		for parameters in cf_details:
			for tag in parameters['Parameters']:
				if tag['ParameterKey'] == 'DeadManSwitchDate':
					retirement_date.append(str(tag['ParameterValue']))
					for i in retirement_date:
						y=i
						format_str = '%m %d %Y'
						dead=datetime.datetime.strptime(y.replace("/"," "), format_str)
						dead_date=dead.date()
						print("OK")
						#print(dead_date.date())
						date_7_days_ago = dead - datetime.timedelta(days=7)
						dead_date_7_days_ago = date_7_days_ago.date()
						if dead_date == current_date:
							if parameters['EnableTerminationProtection'] == 'True':
								change_termination_policy = client.update_termination_protection(EnableTerminationProtection=False,StackName = stackname)
								time.sleep(.03)
								logger.info("deleting the stack", stackname)
								Delete_Stack(stackname)
						elif dead_date_7_days_ago == current_date:
							notifying_stacks.append(tag['ParameterValue'])
							logger.info("sending notification to owner")
							Send_Notification(stackname, notifying_stacks)
						else:
							logger.info("no stacks")

def lambda_handler(event,context):
	Get_The_Details_And_Delete()
