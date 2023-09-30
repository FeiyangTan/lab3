import boto3

def lambda_handler(event, context):
    print("Hello3")
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        file_name = getFileNameFromS3(bucket_name, key)
        print('FileName:', file_name)
        deleteFileFromS3(bucket_name, key)
    except Exception as e:
        print('Error:', str(e))

def getFileNameFromS3(bucket_name, key):
    print('getFileNameFromS3: bucket_name: {0}, key: {1}'.format(bucket_name, key))
    s3_client = boto3.client('s3')
    response = s3_client.head_object(Bucket=bucket_name, Key=key)
    return response['Metadata']['filename']

def deleteFileFromS3(bucket_name, key):
    print('deleteFileFromS3: bucket_name: {0}, key: {1}'.format(bucket_name, key))
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=bucket_name, Key=key)