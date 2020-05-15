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

# import opencv for accessing camera, image preprocessing
# so that it's easier than to have pytesseract translate image to text with live video
import cv2 as cv
import numpy as np
import utlis

# import pyautogui for key, mouse event controller automation
import pyautogui

# import time for programme sleep time
import time

# import GTTS for text-to-speech
# text-to-speech
from gtts import gTTS
import os

# import playsound
from playsound import playsound

# import google-cloud-translate
from google.cloud import translate_v2 as translate
# import googlemaps for geolocations and directions
import googlemaps
from datetime import datetime

# import wolframalpha for common knowledge
import wolframalpha

# import tkinter
import tkinter as tk

# import random
import random

# import requests for requesting API calls from websites
import requests

# specifying languages to be used for image-to-text analysis
# vietnamese, english, korean, chinese simplified, french, african, finish, italian, japanese, hungarian, spanish, thai, russian, hindi, german
langs_tesseract = 'vie+eng+kor+chi_sim+fra+afr+fin+ita+jpn+hun+spa+tha+rus+hin+deu'

# specifying languages to be used for google engine (GTTS, Google Translate)
langs_gg = 'vi|en|ko|zh|fr|fi|it|ja|hu|es|th|ru|hi|de'

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
r_maps = sr.Recognizer()
r_greeting = sr.Recognizer()
global result
result = None

root = tk.Tk()

# keep track of each mode in the system workflow
mode = 0

# gmaps = googlemaps.Client(key=API_KEY)
# now = datetime.now()
# geocode = gmaps.geocode('Northend Avenue, Bristol')
# directions_result = gmaps.directions("Northend Avenue, Bristol",
#                                      "BS16 1QY",
#                                      mode="transit",
#                                      departure_time=now)
# distance = directions_result['legs']
# print(distance)

def chooseDestLanguage():
    chooseDestL_label = tk.Label(root, text="Speak Your Desired Destination Language", bg='gray')
    chooseDestL_label.pack()
    print("Speak Your Desired Destination Language")

    # machine reply
    path_to_audioFile_language_choosen = 'media/audio//response/after_lang_choosen.mp3'
    playsound(path_to_audioFile_language_choosen)
    
    with sr.Microphone(sample_rate = sample_rate,  
                        chunk_size = chunk_size) as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        try:
            global destL
            destL = r.recognize_google(audio)
            # make the destination lang lower case as it'll be searched up on google translate
            destL = destL.lower()

            # seletively eliminate unnecesarry words except for language names
            # and encode them into language code that the translation engine can recognise
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
            elif 'afr' in destL:
                destL = 'af'
                print(destL)
            elif 'fin' in destL:
                destL = 'fi'
                print(destL)
            elif 'tha' in destL:
                destL = 'th'
                print(destL)
            elif 'rus' in destL:
                destL = 'ru'
                print(destL)
            elif 'hin' in destL:
                destL = 'hi'
                print(destL)
            elif 'ger' in destL:
                destL = 'de'
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
    # play a response audio file
    # machine reply
    path_to_audioFile = 'media/audio/response/init_camera.mp3'
    playsound(path_to_audioFile)
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
                saveLabel = tk.Label(root, text='A Frame Saved' + '\n' + 'You Now Have 3 Options: Choose A Destination Language' 
                                    + '\n' + 'Search Image On The Internet'
                                    + '\n' + 'Or Terminate This Process', bg='gray')
                saveLabel.pack()
                path_to_audioFile = 'media/audio/response/after_img_capturing.mp3'
                if biggest.size != 0:
                    cv.imwrite(path_to_imgFile, imgWarpColored)
                else:
                    cv.imwrite(path_to_imgFile, img_show)
                cv.waitKey(300)
                # to close the webcam/camera windows
                # pyautogui.click(1360, 141, button='left')
                pyautogui.keyDown('altleft'); pyautogui.press('f4'); pyautogui.keyUp('altleft')

                # machine reply
                playsound(path_to_audioFile)
                break
            elif cv.waitKey(1) & 0xFF == ord('q'):
                break
        
    except KeyboardInterrupt:    
        cap.release()
        cv.destroyAllWindows()

# def imageCaptured():
#     while True:
#         if cv.waitKey(1) & 0xFF == ord('s'):
#             if biggest.size != 0:
#                 cv.imwrite(path_to_imgFile, imgWarpColored)
#             else:
#                 cv.imwrite(path_to_imgFile, img_show)
#             cv.waitKey(300)
#             break

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
        path_to_audioFile = 'media/audio/translated_text/input.mp3'
        sourceL = result['detectedSourceLanguage']
        input = gTTS(text=keywords, lang=sourceL, slow=False)
        input.save(path_to_audioFile)
        # playsound(path_to_audioFile)
        os.system(f'start {path_to_audioFile}')
        time.sleep(5)
        pyautogui.keyDown('altleft'); pyautogui.press('f4'); pyautogui.keyUp('altleft')
    else:
        print('You Need To Specify The Source Language First')

def listenTrans():
    # listenField = driver.find_element_by_xpath("//div[@class='res-tts ttsbutton-res left-positioned ttsbutton jfk-button-flat source-or-target-footer-button jfk-button']")
    # listenField.click()
    if result != None:
        path_to_audioFile = 'media/audio/translated_text/output.mp3'
        translated_text = result['translatedText']
        output = gTTS(text=translated_text, lang=destL, slow=False)
        output.save(path_to_audioFile)
        # playsound(path_to_audioFile)
        os.system(f'start {path_to_audioFile}')
        time.sleep(5)
        pyautogui.keyDown('altleft'); pyautogui.press('f4'); pyautogui.keyUp('altleft')
    else:
        print('You Need To Specify The Source Language First')

def imageDetection():
    os.startfile('media\img\still_img_captured')
    time.sleep(1)
    # locate the img
    pyautogui.typewrite(['down', 'enter'])
    time.sleep(1)

    # google image search
    pyautogui.click(960, 640, button='right')
    pyautogui.typewrite(['down', 'down', 'down', 'down', 'down', 'enter'])
    
    # machine reply
    path_to_audioFile_for_img_search = 'media/audio/response/after_img_search.mp3'
    playsound(path_to_audioFile_for_img_search)

    # machine reply
    path_to_audioFile_for_screenshot = 'media/audio/response/prep_for_screenshot.mp3'
    playsound(path_to_audioFile_for_screenshot)

    # wait for webpage buffering
    time.sleep(8)
    im = pyautogui.screenshot(region=(440, 429, 331, 42))
    im.save(path_for_img_detection)

    # machine reply
    path_to_audioFile_for_img_analysed = 'media/audio/response/after_screenshot.mp3'
    playsound(path_to_audioFile_for_img_analysed)

    # add label
    chooseDestL_label = tk.Label(root, text="Now, Choose A Destination Language", bg='gray')
    chooseDestL_label.pack()
    # chooseDestLanguage()
    # machine reply
    path_to_audioFile_for_dest_lang = 'media/audio/response/choose_dest_lang.mp3'
    playsound(path_to_audioFile_for_dest_lang)

def geolocate():
    print('Hey')
    # provide api key for google maps access
    API_KEY = ''

    ##########################
    # FIND PLACES
    # listen to a speech
    # voice command for finding directions
    with sr.Microphone(sample_rate = sample_rate,  
                    chunk_size = chunk_size) as source:
        r_maps.pause_threshold = 1
        r_maps.adjust_for_ambient_noise(source, duration=0.5)
        audio = r_maps.listen(source)
        try:
            speech = r_maps.recognize_google(audio)
            now = datetime.now()
            # split the string of a speech into an array
            speech = speech.split(' ')

            # create an empty array to store final words as indices
            s = []

            ##########################
            # GEOLOCATIONS AND DIRECTIONS
            ORIGIN = ''
            DESTINATION = ''
            MODE = ''

            # iterate through the array, find keywords: from, to, by
            for f in range(len(speech)):
                # to store a positional argument at the word 'from'
                if speech[f] == 'from':
                    for b in range(len(speech)):
                        # to store a positional argument at the word 'by'
                        if speech[b] == 'by':
                            # find a word after 'by'
                            MODE = speech[b + 1]
                            # find words in between these two words
                            for p in range(f + 1, b):
                                s.append(speech[p])
            
            # concatenate them and get rid of 'to'
            newString = ' '.join(map(str, s)).split('to')
            ORIGIN = newString[0]
            DESTINATION = newString[1]

            # call a places api with the origin in a scenario where users say 'here' as the origin
            URL_PLACES = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={ORIGIN}&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key={API_KEY}'
            places = requests.get(URL_PLACES)
            places = places.json()
            ORIGIN = places['candidates'][0]['formatted_address']
            # ORIGIN = URL_PLACES['candidates'][0]['formatted_address']
            print(ORIGIN, DESTINATION, MODE)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

    
    # fetch the API from the endpoint
    URL_GEOLOCATION = f'https://maps.googleapis.com/maps/api/directions/json?origin={ORIGIN}&avoid=highways&destination={DESTINATION}&mode={MODE}&key={API_KEY}'
    r = requests.get(URL_GEOLOCATION)
    # make the object into JSON
    r = r.json()
    # print(r['routes'][0]['legs'][0]['distance']['text'])


def speakCommand():
    with sr.Microphone(sample_rate = sample_rate,  
                    chunk_size = chunk_size) as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r1.listen(source)
        try:
            SpeakCmd = r1.recognize_google(audio)
            # voice command for initiating live camera
            if 'start' in SpeakCmd:
                if 'cam' in SpeakCmd:
                    print(SpeakCmd)
                    global mode
                    mode = 1
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
                if 'image' in SpeakCmd:
                    mode = 2
                    imageDetection()
            elif 'search' in SpeakCmd:
                if 'image' in SpeakCmd:
                    mode = 2
                    imageDetection()

            # voice command for directions
            if 'map' in SpeakCmd:
                mode = 3
                geolocate()
            elif 'find' in SpeakCmd:
                mode = 3
                geolocate()

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
                # voice command to terminate tasks
                if 'termin' in SpeakCmd:
                    mode = 0
                elif 'end' in SpeakCmd:
                    mode = 0
                
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
            
def greeting():
    hour = str(datetime.now()).split(' ')[1].split(':')[0]
    if int(hour) < 12:
        path_to_audioFile = 'media/audio/response/Good_Morning.mp3'
    elif int(hour) >= 12 and int(hour) <= 18:
        path_to_audioFile = 'media/audio/response/Good_Afternoon.mp3'
    elif int(hour) > 18 and int(hour) <= 24:
        path_to_audioFile = 'media/audio/response/Good_Day.mp3'
    path_to_audioFile2 = 'media/audio/response/Yes_Sir.mp3'
    greetings = [path_to_audioFile, path_to_audioFile2]
    with sr.Microphone(sample_rate = sample_rate,  
                    chunk_size = chunk_size) as source:
        r_greeting.pause_threshold = 1
        r_greeting.adjust_for_ambient_noise(source, duration=0.5)
        audio = r_greeting.listen(source)
        try:
            greetAurora = r_greeting.recognize_google(audio)
            if 'Aurora' in greetAurora:
                playsound(random.choice(greetings))
                speakCommand()
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

# TKINTER
canvas = tk.Canvas(root, bg='white')
canvas.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

# webcamBtn = tk.Button(root, text='Open Live Webcam', padx=20, pady=10, fg='white', bg='black', command=liveVideoCapture)
# webcamBtn.pack()

greetingsBtn = tk.Button(root, text='Command Aurora', padx=20, pady=10, fg='white', bg='red', command=greeting)
greetingsBtn.pack()

speakBtn = tk.Button(root, text='Speak Command', padx=20, pady=10, fg='white', bg='black', command=speakCommand)
speakBtn.pack()

mapsBtn = tk.Button(root, text='Maps', padx=20, pady=10, fg='white', bg='black', command=geolocate)
mapsBtn.pack()

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
    # ideally, users should follow the system workflow to get the best result
    # then automatically analyses the img, once a targeted language is choosen
    # then automatically processes to the translation pipeline
    # after that, users can either choose to listen to the original text language or the translated one
    # then the whole workflow will be restarted once users hit the reset button

################################################################################
