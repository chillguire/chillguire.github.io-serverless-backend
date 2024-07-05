import boto3
from botocore.exceptions import ClientError
import json
import os
from datetime import datetime, timedelta
import dateutil.tz


def parse_arn(arn):
    # http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
    elements = arn.split(':', 5)
    result = {
        'arn': elements[0],
        'partition': elements[1],
        'service': elements[2],
        'region': elements[3],
        'account': elements[4],
        'resource': elements[5],
        'resource_type': None
    }
    if '/' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split(
            '/', 1)
    elif ':' in result['resource']:
        result['resource_type'], result['resource'] = result['resource'].split(
            ':', 1)
    return result


def schedule_shutdown_lambda(resourceName, resourceDetails):
    try:
        eventBridgeScheduler = boto3.client('scheduler')
        currentTimezone = 'America/Caracas'
        scheduledTime = datetime.now(dateutil.tz.gettz(
            currentTimezone)) + timedelta(hours=1)
        scheduledTime = scheduledTime.strftime('%Y-%m-%dT%H:%M:%S')
        scheduleExists = eventBridgeScheduler.get_schedule(
            Name='{}_{}_{}'.format(
                resourceName, resourceDetails['service'], resourceDetails['resource_type']),
        )
        eventBridgeScheduler.update_schedule(
            Name='{}_{}_{}'.format(
                resourceName, resourceDetails['service'], resourceDetails['resource_type']),
            ActionAfterCompletion='DELETE',
            FlexibleTimeWindow={
                'Mode': 'OFF'
            },
            ScheduleExpression='at({})'.format(
                scheduledTime),  # at(2024-06-26T14:08:00)
            ScheduleExpressionTimezone=currentTimezone,
            State='ENABLED',
            Target={
                'Arn': os.environ['ShutDownLambdaARN'],
                'Input': '{{"project": "{}"}}'.format(resourceName),
                'RoleArn': os.environ['EventBridgeAssumeRoleARN'],
                # 'RetryPolicy': {
                # 	'MaximumEventAgeInSeconds': 123,
                # 	'MaximumRetryAttempts': 123
                # },
            }
        )
    except ClientError as error:
        eventBridgeScheduler.create_schedule(
            Name='{}_{}_{}'.format(
                resourceName, resourceDetails['service'], resourceDetails['resource_type']),
            ActionAfterCompletion='DELETE',
            FlexibleTimeWindow={
                'Mode': 'OFF'
            },
            ScheduleExpression='at({})'.format(
                scheduledTime),  # at(2024-06-26T14:08:00)
            ScheduleExpressionTimezone=currentTimezone,
            State='ENABLED',
            Target={
                'Arn': os.environ['ShutDownLambdaARN'],
                'Input': '{{"project": "{}"}}'.format(resourceName),
                'RoleArn': os.environ['EventBridgeAssumeRoleARN'],
                # 'RetryPolicy': {
                # 	'MaximumEventAgeInSeconds': 123,
                # 	'MaximumRetryAttempts': 123
                # },
            }
        )


def lambda_handler(event, context):
    response = {
        'statusCode': 404,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'data': None,
            'error': 'Not found',
        },
    }

    if (event['project']) and (event['project'] is not None):
        resourceFinder = boto3.client('resourcegroupstaggingapi')
        resources = resourceFinder.get_resources()
        for i in resources['ResourceTagMappingList']:
            name_tag = ''
            for j in i['Tags']:
                if (j['Key'] and j['Key'] == 'Name'):
                    name_tag = j['Value']
                    break

            if (name_tag == event['project']):
                params = parse_arn(i['ResourceARN'])

                try:
                    if (params['resource_type'] == 'instance' and params['service'] == 'ec2'):
                        ec2 = boto3.resource('ec2')
                        instance = ec2.Instance(params['resource'])

                        # 0 : pending
                        # 16 : running - just retrieve IP and DNS
                        # 32 : shutting-down
                        # 48 : terminated
                        # 64 : stopping
                        # 80 : stopped - start it
                        if (instance.state['Code'] == 80):
                            instance.start()
                            instance.wait_until_running()
                            schedule_shutdown_lambda(event['project'], params)

                            response['statusCode'] = 200
                            response['body']['error'] = None
                            response['body']['data'] = {
                                'DNS': instance.public_dns_name,
                                'IP': instance.public_ip_address,
                            }
                        elif (instance.state['Code'] == 16):
                            schedule_shutdown_lambda(event['project'], params)

                            response['statusCode'] = 200
                            response['body']['error'] = None
                            response['body']['data'] = {
                                'DNS': instance.public_dns_name,
                                'IP': instance.public_ip_address,
                            }
                        else:
                            # ? enviar notificacion? no se
                            response['statusCode'] = 501
                            response['body']['error'] = 'Not Implemented'
                            response['body']['data'] = {
                                'DNS': instance.public_dns_name,
                                'IP': instance.public_ip_address,
                            }
                    # elif ():
                    else:
                        response['statusCode'] = 501
                        response['body']['error'] = 'Not Implemented'

                    return response
                except AttributeError:
                    continue
    return response
