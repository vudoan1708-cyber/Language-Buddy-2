# import PyTesseract for image-to-text analysis
# link to Tesseract installation: 
# https://github.com/UB-Mannheim/tesseract/wiki?fbclid=IwAR2aj_N_2qrLLyNFRYwULr_1NDaB20TPQa93h-beGDvIQv1akGsByEXYCOQ

# then add tesseract to the path
# pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pytesseract as pt

# import python imaging library
from PIL import Image

# import speech recognition for getting the desired destination language for users
import speech_recognition as sr

# import opencv for accessing camera, possibly, to detect corners of an image, then capture it
# so that it's easier than to have pytesseract translate image to text with live video
import cv2 as cv
import numpy as np
import utlis

# import pyautogui for key, mouse event controller automation
import pyautogui

# import time for prgramme sleep time
import time

# import GTTS for text-to-speech
# text-to-speech
from gtts import gTTS
import os

# import google-cloud-translate
from google.cloud import translate_v2 as translate

# import tkinter
import tkinter as tk
# print('Package Loaded')

# specifying languages to be used for image-to-text analysis
# vietnamese, english, korean, chinese simplified, french, african, finish, italian, japanese, hungarian, spanish
langs_tesseract = 'vie+eng+kor+chi_sim+fra+afr+fin+ita+jpn+hun+spa'

# specifying languages to be used for google engine (GTTS, Google Translate)
langs_gg = 'vi+en+ko+zh+fr'

# Sample rate is how often values are recorded 
sample_rate = 48000

# Chunk is like a buffer. It stores 2048 samples (bytes of data) 
# here.  
# it is advisable to use powers of 2 such as 1024 or 2048 
chunk_size = 2048

# SPEECH RECOGNITION
# initialise recogniser
r = sr.Recognizer()
r1 = sr.Recognizer()
global result
result = None

root = tk.Tk()

# keep track of each mode in the system workflow
mode = 0

def chooseDestLanguage():
    chooseDestL_label = tk.Label(root, text="Speak Your Desired Destination Language", bg='gray')
    chooseDestL_label.pack()
    print("Speak Your Desired Destination Language")

    with sr.Microphone(sample_rate = sample_rate,  
                        chunk_size = chunk_size) as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        try:
            global destL
            destL = r.recognize_google(audio)
            # make the destination lang lower case as it'll be searched up on google translate
            destL = destL.lower()
            if 'viet' in destL:
                destL = 'vi'
                print(destL)
            elif 'kor' in destL:
                destL = 'ko'
                print(destL)
            elif 'chi' in destL:
                destL = 'zh-CN'
                print(destL)
            elif 'eng' in destL:
                destL = 'en'
                print(destL)
            elif 'fre' in destL:
                destL = 'fr'
                print(destL)
            elif 'spa' in destL:
                destL = 'es'
                print(destL)
            elif 'arab' in destL:
                destL = 'ar'
                print(destL)
            elif 'jap' in destL:
                destL = 'ja'
                print(destL)
            elif 'ita' in destL:
                destL = 'it'
                print(destL)
            elif 'hun' in destL:
                destL = 'hu'
                print(destL)
            else:
                warning_label = tk.Label(root, text="Apparently, we don't know that language yet", bg='gray')
                warning_label.pack()
            # call the function to do web scraping on Google Translate
            # googleTranslate()
            # call the function to do image-to-text analysis
            analyseImg()
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

# initialise OPENCV live video webcam
cap = cv.VideoCapture(0)
widthImg = 960
heightImg = 540
webcamFeed = True
path_to_imgFile =  'media/img/still_img_captured/myImage.png'
path_for_img_detection = 'media/img/img_detection/myImage.png'

# initialise the system workflow with live camera
def init():
    try:
        while True:
            if webcamFeed:
                _, frame = cap.read()
            else:
                frame = cv.imread(path_to_imgFile)
            frame = cv.resize(frame, (widthImg, heightImg))
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            bilateral = cv.bilateralFilter(gray, 5, 12, 12)
            canny = cv.Canny(bilateral, 100, 200)

            kernel = np.ones((5, 5))
            dilate = cv.dilate(canny, kernel, iterations=2)
            erode = cv.erode(dilate, kernel, iterations=1)

            imgContour = frame.copy()
            imgBigContour = frame.copy()
            contours, _ = cv.findContours(erode, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            cv.drawContours(imgContour, contours, -1, (0, 255, 0), 10)

            # find the biggest contour
            global biggest, imgWarpColored, img_show
            biggest, _ = utlis.biggestContour(contours)
            if biggest.size != 0:
                # reorder the list of the biggest resolution
                biggest = utlis.reorder(biggest)
                cv.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)
                imgBigContour = utlis.drawRectangle(imgBigContour, biggest, 2)

                # warp perspective
                pts1 = np.float32(biggest)
                pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
                matrix = cv.getPerspectiveTransform(pts1, pts2)
                imgWarpColored = cv.warpPerspective(frame, matrix, (widthImg, heightImg))

                # remove 20px from each side
                # grayscale the warped img
                imgWarpGray = cv.cvtColor(imgWarpColored, cv.COLOR_BGR2GRAY)
                imgAdaptiveThre = cv.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
                imgAdaptiveThre = cv.bitwise_not(imgAdaptiveThre)
                imgAdaptiveThre = cv.medianBlur(imgAdaptiveThre, 3)

                # show the biggest contour found in a live video
                img_show = imgBigContour
            else:
                img_show = frame

            # either show the biggest contour found in a frame
            # or just show the live video as usual
            cv.imshow('Live Webcam', img_show)

            if cv.waitKey(1) & 0xFF == ord('s'):
                saveLabel = tk.Label(root, text='A Frame Saved' + '\n' + 'You Now Have Two Options: Choose A Destination Language' 
                                    + '\n' + 'or Ask Me To Perform Object Detection', bg='gray')
                saveLabel.pack()
                if biggest.size != 0:
                    cv.imwrite(path_to_imgFile, imgWarpColored)
                else:
                    cv.imwrite(path_to_imgFile, img_show)
                cv.waitKey(300)
                # to close the webcam/camera windows
                # pyautogui.click(1360, 141, button='left')
                pyautogui.keyDown('altleft'); pyautogui.press('f4'); pyautogui.keyUp('altleft')
                break
            elif cv.waitKey(1) & 0xFF == ord('q'):
                break
        
    except KeyboardInterrupt:    
        cap.release()
        cv.destroyAllWindows()

def imageCaptured():
    while True:
        if cv.waitKey(1) & 0xFF == ord('s'):
            if biggest.size != 0:
                cv.imwrite(path_to_imgFile, imgWarpColored)
            else:
                cv.imwrite(path_to_imgFile, img_show)
            cv.waitKey(300)
            break

# remember to add the json file to the environment PATH before running this code file
def translateText(text):
    client = translate.Client()
    global result
    result = client.translate(text, target_language=destL)

    print('Text: ', result['input'])
    print('Translation: ', result['translatedText'])
    print('Detected Source Lang: ', result['detectedSourceLanguage'])

    global mode
    mode = 0
    print(mode)

def analyseImg():
    # for prototyping
    # testing the accuracy in image-to-text analysis between grayscaled img and coloured img 
    if mode == 1:
        img = cv.imread(path_to_imgFile)
    else: img = cv.imread(path_for_img_detection)
    # img = Image.open('media/img/korean.jpg')
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    bilateral = cv.bilateralFilter(gray, 5, 12, 12)
    global keywords
    keywords = pt.image_to_string(bilateral, lang=langs_tesseract)
    cv.waitKey(0)
    # print(keywords)
    # call the function to do the translation afterwards
    # googleTranslate()
    translateText(keywords)

def listenOrg():
    # listenField = driver.find_element_by_xpath("//div[@class='src-tts left-positioned ttsbutton jfk-button-flat source-or-target-footer-button jfk-button']")
    # listenField.click()
    if result != None:
        sourceL = result['detectedSourceLanguage']
        path_to_audioFile = 'media/audio/input.mp3'
        input = gTTS(text=keywords, lang=sourceL, slow=False)
        input.save(path_to_audioFile)
        os.system(f'start {path_to_audioFile}')
    else:
        print('You Need To Specify The Source Language First')

def listenTrans():
    # listenField = driver.find_element_by_xpath("//div[@class='res-tts ttsbutton-res left-positioned ttsbutton jfk-button-flat source-or-target-footer-button jfk-button']")
    # listenField.click()
    if result != None:
        translated_text = result['translatedText']
        path_to_audioFile = 'media/audio/output.mp3'
        output = gTTS(text=translated_text, lang=destL, slow=False)
        output.save(path_to_audioFile)
        os.system(f'start {path_to_audioFile}')
    else:
        print('You Need To Specify The Source Language First')

def imageDetection():
    os.startfile('media\img\still_img_captured')
    time.sleep(0.75)
    # locate the img
    pyautogui.typewrite(['down', 'enter'])
    time.sleep(0.75)

    # google image search
    pyautogui.click(960, 640, button='right')
    pyautogui.typewrite(['down', 'down', 'down', 'down', 'down', 'enter'])
    
    # wait for webpage buffering
    time.sleep(8)
    im = pyautogui.screenshot(region=(440, 429, 331, 42))
    im.save(path_for_img_detection)

    # add label
    chooseDestL_label = tk.Label(root, text="Now, Choose A Destination Language", bg='gray')
    chooseDestL_label.pack()
    # chooseDestLanguage()

def speakCommand():
    with sr.Microphone(sample_rate = sample_rate,  
                    chunk_size = chunk_size) as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r1.listen(source)
        try:
            SpeakCmd = r1.recognize_google(audio)
            # voice command for initiating live camera
            if 'start' in SpeakCmd:
                if 'cam' in SpeakCmd:
                    print(SpeakCmd)
                    global mode
                    mode = 1
                    print(mode)
                    init()
                elif 'video' in SpeakCmd:
                    print(SpeakCmd)
                    mode = 1
                    init()
            elif 'init' in SpeakCmd:
                if 'cam' in SpeakCmd: 
                    print(SpeakCmd)
                    mode = 1
                    init()
                elif 'video' in SpeakCmd:
                    print(SpeakCmd)
                    mode = 1
                    init()
            
            # voice command for object detection
            if 'detect' in SpeakCmd:
                mode = 2
                imageDetection()
            elif 'image' in SpeakCmd:
                mode = 2
                imageDetection()
            
            if mode == 1:
                # voice command to listen to the original text
                if 'listen' in SpeakCmd:
                    if 'source' in SpeakCmd:
                        print(SpeakCmd)
                        listenOrg()
                    elif 'origin' in SpeakCmd:
                        print(SpeakCmd)
                        listenOrg()

            # voice command to listen to the translated text
            if 'listen' in SpeakCmd:
                if 'dest'  in SpeakCmd:
                    print(SpeakCmd)
                    listenTrans()
                elif 'target'  in SpeakCmd:
                    print(SpeakCmd)
                    listenTrans()
                elif 'translate' in SpeakCmd:
                    print(SpeakCmd)
                    listenTrans()
            
            if mode == 1 or mode == 2:
                # voice command to choose a desired destination language
                if 'choose' in SpeakCmd:
                    if 'dest'  in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
                    elif 'lang' in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
                elif 'select' in SpeakCmd:
                    if 'dest'  in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
                    elif 'lang' in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
                elif 'say' in SpeakCmd:
                    if 'dest'  in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
                    elif 'lang' in SpeakCmd:
                        print(SpeakCmd)
                        chooseDestLanguage()
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            

# TKINTER
canvas = tk.Canvas(root, bg='white')
canvas.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

# webcamBtn = tk.Button(root, text='Open Live Webcam', padx=20, pady=10, fg='white', bg='black', command=liveVideoCapture)
# webcamBtn.pack()

speakBtn = tk.Button(root, text='Speak Command', padx=20, pady=10, fg='white', bg='black', command=speakCommand)
speakBtn.pack()

chooseDestLBtn = tk.Button(root, text='Speak a Desired Destination Language', padx=20, pady=10, fg='white', bg='black', command=chooseDestLanguage)
chooseDestLBtn.pack()

listenOrgBtn = tk.Button(root, text='Listen to The Original Text', padx=20, pady=10, fg='white', bg='red', command=listenOrg)
listenOrgBtn.pack()

listenTransBtn = tk.Button(root, text='Listen to The Translated Text', padx=20, pady=10, fg='white', bg='red', command=listenTrans)
listenTransBtn.pack()

initBtn = tk.Button(root, text='Initialise', padx=20, pady=10, fg='white', bg='red', command=init)
initBtn.pack()

root.mainloop()

################################################################################

    # waits for a triggering event to initialise live webcam
    # then waits for a button press for a still img captured from live video webcam
    # then immediately asks users to speak a desired destination language once the above condition is satisfied
    # this feature can either be triggered by a button OR by following this workflow
    # ideally, users should follow the sysmte workflow to get the best result
    # then automatically analyses the img, once a targeted language is choosen
    # then automatically processes to the translation pipeline
    # after that, users can either choose to listen to the original text language or the translated one
    # then the whole workflow will be restarted once users hit the reset button

################################################################################
