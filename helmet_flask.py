from tkinter.tix import Tree
from mainfunc import *
import os
from flask import *
import cv2
import easyocr

reader = easyocr.Reader(['en']) 

IMAGE_FOLDER = 'static/'

numbers_plates = []



save_img=True  # set true when using only image file to save the image
# when using image as input, lower the threshold value of image classification
def work(path):
    cap = cv2.imread(path) #2.jpg pic is best for testing this project
    frame = cv2.resize(cap, frame_size)  # resizing imagey
    original_frame = frame.copy()
    frame, results = object_detection(frame) 
    print(results, 1)

    rider_list = []
    head_list = []
    number_list = []

    for result in results:
        x1,y1,x2,y2,cnf, clas = result
        if clas == 0:
            rider_list.append(result)
        elif clas == 1:
            head_list.append(result)
        elif clas == 2:
            number_list.append(result)

    print('R', rider_list)
    print('H', head_list)
    print('N', number_list)
    for rdr in rider_list:
        time_stamp = str(time.time())
        x1r, y1r, x2r, y2r, cnfr, clasr = rdr
        for hd in head_list:
            x1h, y1h, x2h, y2h, cnfh, clash = hd
            if inside_box([x1r,y1r,x2r,y2r], [x1h,y1h,x2h,y2h]): # if this head inside this rider bbox
                try:
                    head_img = original_frame[y1h:y2h, x1h:x2h]
                    helmet_present = img_classify(head_img)
                    print("rider ",helmet_present)
                except:
                    helmet_present[0] = None
                if  helmet_present[0] == True: # if helmet present
                    frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0,255,0), 1)
                    frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    frame = cv2.putText(frame, "Helmet Worn", (x1h, y1h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255, 0), 1, cv2.LINE_AA)
                    # cv2.imwrite(f'riders_pictures/{time_stamp}.jpg', frame[y1r:y2r, x1r:x2r])
                elif helmet_present[0] == False: # if helmet absent 
                    frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 255, 255), 1)
                    frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    frame = cv2.putText(frame, "Helmet Absent", (x1h, y1h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    # cv2.imwrite(f'riders_pictures/{time_stamp}.jpg', frame[y1r:y2r, x1r:x2r])
                elif helmet_present[0] == None: # Poor prediction
                    frame = cv2.rectangle(frame, (x1h, y1h), (x2h, y2h), (0, 0, 255), 1)
                    frame = cv2.putText(frame, f'{round(helmet_present[1],1)}', (x1h, y1h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    frame = cv2.putText(frame, "No Helmet", (x1h, y1h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    
                    print('S',number_list)
                    for num in number_list:
                        x1_num, y1_num, x2_num, y2_num, conf_num, clas_num = num
                        if inside_box([x1r,y1r,x2r,y2r], [x1_num, y1_num, x2_num, y2_num]):
                            num_img = original_frame[y1_num:y2_num, x1_num:x2_num]  #resized frame
                            cv2.imwrite(f'number_plates/{time_stamp}_{conf_num}.jpg', num_img)
                            output = reader.readtext(num_img)
                            numbers_plates.append(output)
                            print("Output is:", output)


    frame = cv2.resize(frame, (900, 450))  # resizing to fit in screen
    # cv2.imshow('Frame', frame)
    my_img = frame
    x = len(os.listdir("static/pavan"))
    cv2.imwrite(f'static/pavan/{x}.jpg', frame)						
							
    if save_img: #save img

        y = len(os.listdir("static/saved_pictures"))
        cv2.imwrite(f'static/saved_pictures/{y}.jpg', frame[y1r:y2r, x1r:x2r])
        cv2.imwrite('saved_frame.jpg', frame)

    print('Execution completed')
    return x

app = Flask(__name__)  
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
#app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/')  
def upload():
    return render_template("file_upload_form.html")  
 
@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        image_ext = cv2.imread(full_filename)
        img_path = full_filename
        print(img_path)
        # print("sa")
        x = work(img_path)
        x = int(x)
        print(x)
        # predicted_image = os.path.join('pavan',f'{x}.jpg')
        predicted_image = os.path.join(f"{app.config['UPLOAD_FOLDER']}/pavan/", f'{x}.jpg')
        print("predicted_image is ",predicted_image,"org is ",full_filename)
        # print("yippie")
        final_text = 'Results after Detecting Input Image'
        
        return render_template("success.html", name = final_text, img = full_filename,img2 = predicted_image,output = numbers_plates)
        
@app.route('/info', methods = ['POST'])  
def info():
    return render_template("info.html")  


if __name__ == '__main__':  
    app.run(host="127.0.0.1",port=8080,debug=True)  
