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
# import selenium for web scraping in order to automate the translation on Google Translate
# import selenium
# from selenium import webdriver
# # import webdriverwait for wait time
# from selenium.webdriver.support.ui import WebDriverWait
# # import keys for any keyboard triggering
# from selenium.webdriver.common.keys import Keys
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

# set the path to the chrom driver executables file
# link to download: https://sites.google.com/a/chromium.org/chromedriver/downloads
# PATH = 'C:\Program Files (x86)\chromedriver.exe'


#Sample rate is how often values are recorded 
sample_rate = 48000
#Chunk is like a buffer. It stores 2048 samples (bytes of data) 
#here.  
#it is advisable to use powers of 2 such as 1024 or 2048 
chunk_size = 2048

# SPEECH RECOGNITION
# initialise recogniser
r = sr.Recognizer()


def chooseDestLanguage():
    with sr.Microphone(sample_rate = sample_rate,  
                        chunk_size = chunk_size) as source:
        # r.adjust_for_ambient_noise(source)
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

def liveVideoCapture():
    while True:
        # loop through the img sequence and pass it to another variable
        _, frames = cap.read()
        gray = cv.cvtColor(frames, cv.COLOR_BGR2GRAY)
        gray = np.float32(gray)

        corners = cv.goodFeaturesToTrack(gray, 50, 0.01, 10)
        corners = np.int0(corners)

        for c in corners:
            x, y = c.ravel()
            cv.circle(frames, (x, y), 3, 255, -1)
        cv.imshow('Live Webcam', frames)

        # end the loop if there is a key interrupts 
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        # toText = pt.image_to_string(gray, lang=langs_tesseract)
        # if toText == '' or toText == None:
        #     pass
        # else:
        #     print(toText)

# SELENIUM - WEB SCRAPING (GOOGLE TRANSLATE)
# def googleTranslate():
#     global driver
#     # opts = ChromeOptions()
#     # opts.add_experimental_option("excludeSwitches", ['enable-automation'])
#     # choose the web browser type to be driven
#     driver = webdriver.Chrome(PATH)

#     # specify the url to be driven, format it with the custom destL
#     driver.get(f'https://translate.google.com/#view=home&op=translate&sl=auto&tl={destL}')

#     # set input field
#     inputField = 'source'

#     # set output field
#     outputField = "//div[@class='result tlid-copy-target']"

#     # find input field
#     input = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(inputField))

#     # input = driver.find_element_by_xpath("//textarea[@id='source']")
#     # analyseImg()

#     # wait for 3 secs for analysing text
#     time.sleep(2)

#     # input some keywords into the field
#     input.send_keys(keywords)

#     # wait for 3 secs
#     time.sleep(3)

#     # before finding out the output HTML element 
#     # as it's hidden before the input field is filled with text
#     output = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(outputField))

#     print(output.text)
#     time.sleep(3)

# remember to add the json file to the environment PATH before running this code file
def translateText(text):
    client = translate.Client()
    global result
    result = client.translate(text, target_language=destL)

    print('Text: ', result['input'])
    print('Translation: ', result['translatedText'])
    print('Detected Source Lang: ', result['detectedSourceLanguage'])

def analyseImg():
    # for prototyping
    # testing the accuracy in image-to-text analysis between grayscaled img and coloured img 
    img = cv.imread('media/img/fra.png')
    # img = Image.open('media/img/korean.jpg')
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    bilateral = cv.bilateralFilter(gray, 5, 12, 12)
    # threshold = cv.adaptiveThreshold(bilateral, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, 11)
    # cv.imshow('img', bilateral)
    # cv.imshow('Coloured', img)
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
    sourceL = result['detectedSourceLanguage']
    path_to_audioFile = 'media/audio/input.mp3'
    input = gTTS(text=keywords, lang=sourceL, slow=False)
    input.save(path_to_audioFile)
    os.system(f'start {path_to_audioFile}')

def listenTrans():
    # listenField = driver.find_element_by_xpath("//div[@class='res-tts ttsbutton-res left-positioned ttsbutton jfk-button-flat source-or-target-footer-button jfk-button']")
    # listenField.click()
    translated_text = result['translatedText']
    path_to_audioFile = 'media/audio/output.mp3'
    output = gTTS(text=translated_text, lang=destL, slow=False)
    output.save(path_to_audioFile)
    os.system(f'start {path_to_audioFile}')
    
# TKINTER
root = tk.Tk()

canvas = tk.Canvas(root, bg='white')
canvas.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

webcamBtn = tk.Button(root, text='Open Live Webcam', padx=20, pady=10, fg='white', bg='black', command=liveVideoCapture)
webcamBtn.pack()

imageRecognitionBtn = tk.Button(root, text='PyTesseract', padx=20, pady=10, fg='white', bg='black', command=analyseImg)
imageRecognitionBtn.pack()

speakBtn = tk.Button(root, text='Speak Your Desired Destination Language', padx=20, pady=10, fg='white', bg='black', command=chooseDestLanguage)
speakBtn.pack()

listenOrgBtn = tk.Button(root, text='Listen to The Original Text', padx=20, pady=10, fg='white', bg='red', command=listenOrg)
listenOrgBtn.pack()

listenTransBtn = tk.Button(root, text='Listen to The Translated Text', padx=20, pady=10, fg='white', bg='red', command=listenTrans)
listenTransBtn.pack()

root.mainloop()