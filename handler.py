# from boto3 import client as boto3_client
import boto3
import pandas as pd
import ffmpeg

input_bucket = "inputbucket77"
s3_output_bucket = "outputbucket76"
s3_output_key = "result.csv"
dynamodb_name = "studentInfor"
s3 = boto3.client('s3', region_name='us-east-1')

local_file_path = "file.mp4"
output_frame_path = "frames/frame-%d.jpg"

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    # key就是文件名
    key = event['Records'][0]['s3']['object']['key']

    try:
        print("bucket_name: "+ bucket_name)
        print("key: "+ key)
        # S3删除文件
        s3.delete_object(Bucket=bucket_name, Key=key)
        print("Hello3.1")
    except Exception as e:
        print('Error:', str(e))
        
    # 从dynamodb中获取信息
    item = get_item_from_dynamodb("floki")
    set_result_to_s3(item)

# 从S3中获取MP4文件
def lget_item_from_s3(name):
    # key就是文件名
    try:
        print("文件名: "+ name)
        s3.download_file(input_bucket, name, local_file_path)
        print("File downloaded successfully!")
    except Exception as e:
        print("Error occurred:", str(e))

# 从dynamodb中获取信息
def get_item_from_dynamodb(name):
    key = {
    'name': name
    }
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_name)
    response = table.get_item(Key=key)
    item = response.get('Item')
    
    return item

# 上传结果到S3
def set_result_to_s3(item):
    if item:
        df = pd.DataFrame.from_dict([item])
        csv_data = df.to_csv(index=False)

        # Upload CSV data to S3 bucket
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(
            Body=csv_data,
            Bucket=s3_output_bucket,
            Key=s3_output_key
        )
        print("Data uploaded successfully as CSV to S3 bucket!")
    else:
        print("Item not found in DynamoDB!")
        
        
# Split MP4 file into frames using ffmpeg
def split_MP4_file():
    
    stream = ffmpeg.input('input.mp4')
    stream = ffmpeg.hflip(stream)
    stream = ffmpeg.output(stream, 'output.mp4')
    ffmpeg.run(stream)
    # ffmpeg.input(local_file_path).output(output_frame_path, format='image2', vframes='100').run()
    print("Frames extracted successfully!")    
    
      
# lget_item_from_s3("test_0.mp4")
split_MP4_file()