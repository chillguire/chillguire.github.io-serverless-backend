import boto3
import json


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


def lambda_handler(event, context):
    # print('Start - {}'.format(context.aws_request_id))
    if (event['project']) and (event['project'] is not None):
        resourceFinder = boto3.client('resourcegroupstaggingapi')
        resources = resourceFinder.get_resources(TagFilters=[
            {
                'Key': 'Name',
                'Values': [
                    event['project'],
                ]
            },
        ])

        for i in resources['ResourceTagMappingList']:
            params = parse_arn(i['ResourceARN'])
            if (params['resource_type'] == 'instance' and params['service'] == 'ec2'):
                ec2 = boto3.resource('ec2')
                instance = ec2.Instance(params['resource'])
                instance.stop()
                # instance.wait_until_stopped()
                print(
                    'Stopped - {} - {} - {}'.format(event['project'], i, i['ResourceARN']))
            # elif ():
            else:
                print(
                    'Not implemented - {} - {} - {}'.format(event['project'], i, i['ResourceARN']))

    # print('End - {}'.format(context.aws_request_id))
    return None
