# from boto3 import client as boto3_client
import boto3

input_bucket = "inputbucket77"
dynamodb_name = "studentInfor"
s3 = boto3.client('s3', region_name='us-east-1')

def lambda_handler(event, context):
    print("Hello3")
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    # key就是文件名
    key = event['Records'][0]['s3']['object']['key']

    try:
        print("bucket_name: "+ bucket_name)
        print("key: "+ key)
        # 删除文件
        s3.delete_object(Bucket=bucket_name, Key=key)
        print("Hello3.1")
    except Exception as e:
        print('Error:', str(e))

# 从
def get_item_from_dynamodb(key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_name)
    response = table.get_item(Key=key)
    item = response.get('Item')
    
    return item

# 使用示例
key = {
    'name': 'floki'
}
item = get_item_from_dynamodb(key)
print(item)