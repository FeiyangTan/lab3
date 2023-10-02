import boto3
import ffmpeg
import face_recognition
import tempfile
import os
import shutil

# 下载 S3 对象到临时文件
s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'
object_key = 'your-object-key'

temp_file = tempfile.NamedTemporaryFile(delete=False)
temp_file_path = temp_file.name
temp_file.close()

s3.download_file(bucket_name, object_key, temp_file_path)

# 使用 ffmpeg 将视频转换为图像
temp_folder = tempfile.TemporaryDirectory()
temp_folder_path = temp_folder.name

output_file_pattern = os.path.join(temp_folder_path, 'image_%04d.jpg')
ffmpeg.input(temp_file_path).output(output_file_pattern, format='image2', vframes='100').run()

# 创建用于存储处理后图像的临时文件夹
processed_folder = tempfile.TemporaryDirectory()
processed_folder_path = processed_folder.name

# 遍历临时文件夹中的图像文件
for root, dirs, files in os.walk(temp_folder_path):
    for file in files:
        file_path = os.path.join(root, file)

        # 将临时文件复制到处理后图像的临时文件夹
        processed_file_path = os.path.join(processed_folder_path, file)
        shutil.copy(file_path, processed_file_path)

        # 使用 face_recognition 库加载处理后图像文件
        image = face_recognition.load_image_file(processed_file_path)

        # 进行人脸识别或其他处理操作

        # 示例：获取人脸数量
        face_locations = face_recognition.face_locations(image)
        num_faces = len(face_locations)
        print(f"图像 {file} 中的人脸数量: {num_faces}")

# 删除临时文件和文件夹
os.remove(temp_file_path)
temp_folder.cleanup()
processed_folder.cleanup()

print("转换完成！")