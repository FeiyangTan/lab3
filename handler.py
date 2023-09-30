from boto3 import client as boto3_client

input_bucket = "inputbucket77"
s3 = boto3_client('s3', region_name='us-east-1')

# 清空bucket
def clear_bucket(bucketName):
	# global input_bucket
	# s3 = boto3_client('s3', region_name='ap-northeast-2')
	list_obj = s3.list_objects_v2(Bucket=bucketName)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=bucketName, Key=key)
	except:
		print("Nothing to clear in bucket: " + bucketName)

def lambda_handler(event, context):
    print("Hello3")
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        print("bucket_name: "+ bucket_name)
        print("key: "+ key)
        # file_name = getFileNameFromS3(bucket_name, key)
        # print('FileName:', file_name)
        # deleteFileFromS3(bucket_name, key)
        s3.delete_object(Bucket=bucket_name, Key=key)
        print("Hello3.8")
    except Exception as e:
        print('Error:', str(e))

def getFileNameFromS3(bucket_name, key):
    print("Hello3.2")
    s3_client = boto3.client('s3')
    print("Hello3.3")
    response = s3_client.head_object(Bucket=bucket_name, Key=key)
    print("Hello3.4")
    print("getFileNameFromS3: "+response['Metadata'])
    # return response['Metadata']['filename']

def deleteFileFromS3(bucket_name, key):
    print("Hello3.5")
    s3_client = boto3.client('s3')
    print("Hello3.6")
    s3_client.delete_object(Bucket=bucket_name, Key=key)
    print("Hello3.7")