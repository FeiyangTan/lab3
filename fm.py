import pickle
import face_recognition

def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    # print("Data type:", type(data))
    # fileName = "frame-%d.jpg"
    i = 1
    while True:
        unknown_image = face_recognition.load_image_file("frames/frame-"+str(i)+".jpg")
        i += 1
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        # print(unknown_encoding)
        # print(data['encoding'][0])
        results = face_recognition.compare_faces(data['encoding'], unknown_encoding)
        print(type(results))
        if any(results):
            first_true_index = next((i for i, x in enumerate(results) if x), None)
            print(first_true_index)
            print(data["name"][first_true_index])
            break
        # print(results)
    


open_encoding("encoding")
