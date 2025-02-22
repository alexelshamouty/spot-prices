import plotly.express as px
import pandas as pd
import boto3
from datetime import datetime, timedelta

timeNow = datetime.utcnow()
startTime = timeNow - timedelta(days=10)

ec2 = boto3.client('ec2',region_name='eu-central-1')
s3 = boto3.client("s3")


def calculate_instances_price(response):
    instance_list_graviton_spot = [
        {"Architecture":instance['ProcessorInfo']['SupportedArchitectures'],
        "InstanceType": instance["InstanceType"],
        "FreeTierEligible":instance["FreeTierEligible"]
        ,"vCPUs": instance['VCpuInfo']['DefaultVCpus']
        } 
        for instance in response['InstanceTypes'] 
        if instance['ProcessorInfo']['SupportedArchitectures'] != 'x86_64' #Non X68
        and "spot" in instance['SupportedUsageClasses'] # Allows for spot
        ]

    less_than_or_equal_4_vcpus = [
        {"Architecture":instance['ProcessorInfo']['SupportedArchitectures'],
        "InstanceType": instance["InstanceType"],
        "FreeTierEligible":instance["FreeTierEligible"]
        ,"vCPUs": instance['VCpuInfo']['DefaultVCpus']
        } 
        for instance in response['InstanceTypes'] 
        if instance['ProcessorInfo']['SupportedArchitectures'] != 'x86_64' #Non X68
        and "spot" in instance['SupportedUsageClasses'] # Allows for spot
        and instance['VCpuInfo']['DefaultVCpus'] <= 4
        ]


    instance_types = [instance['InstanceType'] for instance in instance_list_graviton_spot]

    #Get last 30 days spot prices
    prices = []
    frames = []
    for instance_type in instance_list_graviton_spot:
        response = ec2.describe_spot_price_history(
        InstanceTypes=[instance_type['InstanceType']],
        ProductDescriptions=["Linux/UNIX"],
        EndTime=timeNow,
        StartTime=startTime) 
        for price in response["SpotPriceHistory"]:
            prices.append({                                                                                  
            "Timestamp":price["Timestamp"],                                                                  
            "InstanceType":price["InstanceType"],                                                            
            "AvailabilityZone": price["AvailabilityZone"],                                                   
            "SpotPrice":float(price["SpotPrice"])                                                                   
            })                                                                                               
        df = pd.DataFrame(prices).sort_values(by="SpotPrice", ascending=False)
        frames.append(df)

    combined_all_instances = pd.concat(frames, ignore_index=True).sort_values(by="SpotPrice", ascending=False)

    prices = []
    frames = []
    for instance_type in less_than_or_equal_4_vcpus:
        response = ec2.describe_spot_price_history(
        InstanceTypes=[instance_type['InstanceType']],
        ProductDescriptions=["Linux/UNIX"],
        EndTime=timeNow,
        StartTime=startTime) 
        for price in response["SpotPriceHistory"]:
            prices.append({                                                                                  
            "Timestamp":price["Timestamp"],                                                                  
            "InstanceType":price["InstanceType"],                                                            
            "AvailabilityZone": price["AvailabilityZone"],                                                   
            "SpotPrice":float(price["SpotPrice"])                                                                   
            })                                                                                               
        df = pd.DataFrame(prices).sort_values(by="SpotPrice", ascending=False)
        frames.append(df)

    combined_small_instances = pd.concat(frames, ignore_index=True).sort_values(by="SpotPrice", ascending=False)

    fig = px.line(combined_all_instances, x="Timestamp", y="SpotPrice", color="InstanceType")

    figCpus = px.line(combined_small_instances, x="Timestamp", y="SpotPrice", color="InstanceType")

    fig.update_yaxes(type="linear")
    figCpus.update_yaxes(type="linear")

    fig.write_html("/tmp/spot_prices_all.html")
    figCpus.write_html("/tmp/spot_prices_small.html")

def upload_to_s3():
    s3.upload_file("/tmp/spot_prices_all.html", "costspottyalex", "spot_prices_all.html", ExtraArgs={'ContentType': 'text/html'})
    s3.upload_file("/tmp/spot_prices_small.html", "costspottyalex", "spot_prices_small.html", ExtraArgs={'ContentType': 'text/html'})

# start a python lambda handler function
def handler(event, context):
    print("Function started")
    response = ec2.describe_instance_types()
    try :
        calculate_instances_price(response)
        upload_to_s3()
        return {
            'statusCode': 200,
            'body': 'Check your website!'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Something up with the code mate!'
        }