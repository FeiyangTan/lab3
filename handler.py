# from boto3 import client as boto3_client
# import face_recognition
# import pickle

# input_bucket = "inputbucket666"
# output_bucket = "outputbucket666"
# s3 = boto3_client('s3', region_name='ap-northeast-2')

# # Function to read the 'encoding' file
# def open_encoding(filename):
# 	file = open(filename, "rb")
# 	data = pickle.load(file)
# 	file.close()
# 	return data

def face_recognition_handler():	
	print("Hello")
