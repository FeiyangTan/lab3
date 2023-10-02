# from boto3 import client as boto3_client
import boto3
import pandas as pd
import ffmpeg
import pickle
import face_recognition
import os
import tempfile
import shutil

input_bucket = "inputbucket77"
s3_output_bucket = "outputbucket76"
s3_output_key = "result.csv"
dynamodb_name = "studentInfor"
s3 = boto3.client('s3', region_name='us-east-1')

local_file_path = "video/"
output_frame_path = "/frame-%d.jpg"



i = 1




def face_recognition_handler(event, context):
    print("helloworld")    

def lambda_handler(event, context):
    print(i)
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

# 从S3中下载、删除指定MP4文件，保存在本地
def lget_item_from_s3(video_name):
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    # temp_file.close()
    try:
        # S3下载文件
        s3.download_file(input_bucket, video_name, temp_file_path)
        print("File downloaded successfully!")
        # S3删除文件
        s3.delete_object(Bucket=input_bucket, Key=video_name)
    except Exception as e:
        print("Error occurred:", str(e))
        
    print(temp_file_path)
    return temp_file_path

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
        
        
# 把MP4文件分解成jpg图片，保存在本地
def split_MP4_file(temp_file_path):
    # 创建临时文件
    temp_folder = tempfile.TemporaryDirectory()
    temp_folder_path = temp_folder.name

    s3 = boto3.client('s3', region_name='us-east-1')
    s3.upload_file(temp_file_path, s3_output_bucket, "test_1.mp4")


    output_file_pattern = os.path.join(temp_folder_path, 'image_%04d.jpg')
    # os.mkdir("videoPicture/"+video_name[:-4])
    
    ffmpeg.input(temp_file_path).output(output_file_pattern, format='image2', vframes='100').run()
    print("Frames extracted successfully!")   
    os.remove(temp_file_path)
    
    # 3.获取图片集合中第一张出现人物的照片，返回人物名称
    person_name = open_encoding(temp_folder_path)
    print("~~3: "+ person_name)
    
    # return temp_folder_path
    return person_name

# 获取图片集合中第一张出现人物的照片，返回人物名称
def open_encoding(temp_folder_path):
    #  # 将临时文件夹中的图像复制到输出文件夹
    # output_folder_path = 'result/'
    # os.makedirs(output_folder_path, exist_ok=True)
    # for root, dirs, files in os.walk(temp_folder_path):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         os.rename(file_path, os.path.join(output_folder_path, file))

    
    
    
    #读取已知人物文件
    file = open("encoding", "rb")
    data = pickle.load(file)
    file.close()
    # print("Data type:", type(data))
    # fileName = "frame-%d.jpg"
    
    # output_folder_path = 'your-output-folder-path'
    # os.makedirs(output_folder_path, exist_ok=True)
    
    # 创建用于存储处理后图像的临时文件夹
    processed_folder = tempfile.TemporaryDirectory()
    processed_folder_path = processed_folder.name
    for root, dirs, files in os.walk(temp_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # 将临时文件复制到处理后图像的临时文件夹
            processed_file_path = os.path.join(processed_folder_path, file)
            shutil.copy(file_path, processed_file_path)
            
            # os.rename(file_path, os.path.join(output_folder_path, file))
            print("processed_file_path: ")
            print(processed_file_path)
            unknown_image = face_recognition.load_image_file(processed_file_path)
            print("unknown_image: ")
            print(unknown_image)
            # i += 1
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            # print(unknown_encoding)
            # print(data['encoding'][0])
            results = face_recognition.compare_faces(data['encoding'], unknown_encoding)
            print(type(results))
            if any(results):
                first_true_index = next((i for i, x in enumerate(results) if x), None)
                print(first_true_index)
                return data["name"][first_true_index]            
    
    
    # i = 1
    # while True:
    #     unknown_image = face_recognition.load_image_file("videoPicture/"+video_name[:-4]+"/frame-"+str(i)+".jpg")
    #     i += 1
    #     unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    #     # print(unknown_encoding)
    #     # print(data['encoding'][0])
    #     results = face_recognition.compare_faces(data['encoding'], unknown_encoding)
    #     print(type(results))
    #     if any(results):
    #         first_true_index = next((i for i, x in enumerate(results) if x), None)
    #         print(first_true_index)
    #         return data["name"][first_true_index]
    #     # print(results)
    
# def handler(event, context):
def handler():
    video_name = "test_1.mp4"
    # 1.从S3中下载、删除指定MP4文件，保存在本地
    temp_file_path = lget_item_from_s3(video_name)
    print("~~1: ")
    print(temp_file_path)
    # 2.把MP4文件分解成jpg图片，保存在本地
    person_name = split_MP4_file(temp_file_path)
    print("~~2: temp_file_path2")

    # # 4.从dynamodb中获取人物信息
    # person_infor = get_item_from_dynamodb(person_name)
    # print("~~4")
    # print(person_infor)
    # # 5.上传人物信息到S3
    # set_result_to_s3(person_infor)
    # print("~~5")
    
handler() 
    