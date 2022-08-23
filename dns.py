#!/usr/bin/python3
import os
import boto3
def r53_zone_finder(record):
    zone_id = None
    Domain = record.split('.')
    Domainname='.'.join(Domain[1:])
    print('Domain name:', Domainname)
    zone_finder = boto3.client('route53')
    zone_finder_response = zone_finder.list_hosted_zones_by_name(DNSName=Domainname,)
    zone_response_hosted_zones = zone_finder_response['HostedZones']
    for zone_response_hosted_zone in zone_response_hosted_zones:
        if zone_response_hosted_zone['Name']== Domainname:
            zone_id = zone_response_hosted_zone['Id']
    if zone_id:
        print('Hosted zone id:', zone_id)
        return zone_id
    else:
        print('No zone found with given domain name',Domainname)
def r53_record_create(record, record_value, account_name):
    r53 = boto3.client('route53')
    r53_response = r53.change_resource_record_sets(
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record,
                        'ResourceRecords': [
                            {
                                'Value': record_value,
                            },
                        ],
                        'TTL': 300,
                        'Type': 'A',
                    },
                },
            ],
        },
        HostedZoneId=zone_id,
    )
    status = r53_response['ResponseMetadata']['HTTPStatusCode']
    if status == 200:
        print('Given dns A record created successfully')
        os.rename('root/'+record[:-1],'account/'+account_name+'/'+record[:-1])
    else:
        print('Unable to create a given dns A record')
with open("root/domain_list", "r") as dl:
    domain_list = dl.readlines()
input_files=os.listdir("root")
input_files.remove("domain_list")
for input_file in input_files:
    for domain in domain_list:
        domain=domain.strip()
        if domain in input_file:
            print(input_file,"is created from",domain)
            with open("root/"+input_file, "r") as inf:
                record_detail = inf.readlines()
                account_name=record_detail[0].strip()
                record_value=record_detail[1].strip()
                record=input_file.strip()+'.'
                print(account_name)
                print(record_value)
                print(input_file)
                zone_id=r53_zone_finder(record)
                if zone_id:
                    r53_record_create(record,record_value,account_name)