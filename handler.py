import boto3
import pandas as pd
import subprocess
import pickle
import face_recognition
import os
import tempfile
import shutil

input_bucket = "inputbucket77"
output_bucket = "outputbucket76"
dynamodb_name = "studentInfor"

s3 = boto3.client('s3', region_name='us-east-1')


# 从S3中下载、删除指定MP4文件，保存在本地
def lget_item_from_s3(video_name):
    # 创建临时文件
    temp_folder = tempfile.TemporaryDirectory()
    temp_folder_path = temp_folder.name
    temp_file_path = os.path.join(temp_folder_path, video_name)

    # temp_file.close()
    try:
        # S3下载文件
        s3.download_file(input_bucket, video_name, temp_file_path)
        print("File downloaded successfully!")
        # S3删除文件
        s3.delete_object(Bucket=input_bucket, Key=video_name)
    except Exception as e:
        print("Error occurred:", str(e))
    
    # 2.把MP4文件分解成jpg图片，保存在本地
    person_name = split_MP4_file(temp_file_path)
    
    return person_name

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
def set_result_to_s3(item, video_name):
    if item:
        df = pd.DataFrame.from_dict([item])
        csv_data = df.to_csv(index=False)

        # Upload CSV data to S3 bucket
        s3.put_object(
            Body=csv_data,
            Bucket=output_bucket,
            Key=video_name[:-4]+".csv"
        )
        print("Data uploaded successfully as CSV to S3 bucket!")
        print("~~~~~~")
        print(item["name"])
    else:
        print("Item not found in DynamoDB!")
        
        
# 把MP4文件分解成jpg图片，保存在本地
def split_MP4_file(temp_file_path):
    # 创建临时文件
    temp_folder = tempfile.TemporaryDirectory()
    temp_folder_path = temp_folder.name

    command = [
        "ffmpeg",
        "-i", temp_file_path,
        "-vf", "fps=1",
        "-qscale:v", "2",
        f"{temp_folder_path}/frame-%d.jpg"
    ]
    subprocess.run(command)
    
    # os.remove(temp_file_path)
    
    # 3.获取图片集合中第一张出现人物的照片，返回人物名称
    person_name = open_encoding(temp_folder_path)
    
    return person_name

# 获取图片集合中第一张出现人物的照片，返回人物名称
def open_encoding(temp_folder_path):    
    #读取已知人物文件
    file = open("encoding", "rb")
    data = pickle.load(file)
    file.close()
    
    # 创建用于存储处理后图像的临时文件夹
    processed_folder = tempfile.TemporaryDirectory()
    processed_folder_path = processed_folder.name
    for root, dirs, files in os.walk(temp_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # 将临时文件复制到处理后图像的临时文件夹
            processed_file_path = os.path.join(processed_folder_path, file)
            shutil.copy(file_path, processed_file_path)

            unknown_image = face_recognition.load_image_file(processed_file_path)

            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            results = face_recognition.compare_faces(data['encoding'], unknown_encoding)
            print(type(results))
            if any(results):
                first_true_index = next((i for i, x in enumerate(results) if x), None)
                print(first_true_index)
                return data["name"][first_true_index]            
    
    

    
# 测试函数
def handler():
    video_name = "test_1.mp4"
    # 1.从S3中下载、删除指定MP4文件，保存在本地
    person_name = lget_item_from_s3(video_name)
    print("~~1: ")
    print(person_name)
    
    # 4.从dynamodb中获取人物信息
    person_infor = get_item_from_dynamodb(person_name)
    print("~~4")
    print(person_infor)
    # 5.上传人物信息到S3
    set_result_to_s3(person_infor, video_name)
    print("~~5")
    
# handler() 
    
def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    # key就是文件名
    video_name = event['Records'][0]['s3']['object']['key']

    # video_name = "test_1.mp4"
    # 1.从S3中下载、删除指定MP4文件，保存在本地
    person_name = lget_item_from_s3(video_name)
    print("~~1: ")
    print(person_name)
    
    # 4.从dynamodb中获取人物信息
    person_infor = get_item_from_dynamodb(person_name)
    print("~~4")
    print(person_infor)
    # 5.上传人物信息到S3
    set_result_to_s3(person_infor, video_name)
    print("~~5")