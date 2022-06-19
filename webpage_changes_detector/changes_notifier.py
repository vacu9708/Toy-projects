import tkinter as tk
import tkinter.messagebox 
import hashlib
from urllib.request import urlopen, Request
import threading
import backend
import webbrowser
import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
driver = webdriver.Chrome('./chromedriver.exe')

window = tk.Tk()
window.title("Webpage detector")
window.geometry("1000x600")

#-----Left frame
leftFrame = tk.Frame(window)
leftFrame.pack(side='left',padx=10, pady=10)

webpageNameLabel=tk.Label(leftFrame, text="Webpage name")
webpageNameLabel.pack()
webpageNameEntry = tk.Entry(leftFrame, width=50, font=("Courier",10), borderwidth=4)
webpageNameEntry.pack()

urlLabel=tk.Label(leftFrame, text='URL')
urlLabel.pack()
urlEntry = tk.Entry(leftFrame, width=50, font=("Courier",10), borderwidth=4)
urlEntry.pack()

identifierLabel=tk.Label(leftFrame, 
text="XPath to HTML element(Empty this for any change to be detected)\n**Use F12 developer tools to get XPath")
identifierLabel.pack()
frontOfHtmlElementEntry = tk.Entry(leftFrame, width=50, font=("Courier",10), borderwidth=4)
frontOfHtmlElementEntry.pack()

symbolLabel=tk.Label(leftFrame, text="className of HTML element(not necessary)")
symbolLabel.pack()
backOfHtmlElementEntry = tk.Entry(leftFrame, width=50, font=("Courier",10), borderwidth=4)
backOfHtmlElementEntry.pack()

alarmTurnedOn=tk.BooleanVar()
alarmTurnedOnCheckbox=tk.Checkbutton(leftFrame, variable=alarmTurnedOn, text='Turn on alarm')
alarmTurnedOnCheckbox.pack()
printFoundElement=tk.BooleanVar()
printFoundElementCheckbox=tk.Checkbutton(leftFrame, variable=printFoundElement, text='Print found HTML element')
printFoundElementCheckbox.pack()

# button: Append webpage
buttonAppendWebpage = tk.Button(leftFrame,
text='Append a webpage', padx=15, pady=10, font=("Courier",10), bg="yellow")  
buttonAppendWebpage.pack(padx=5, pady=5)

# button: Start monitoring
buttonStartMonitoring = tk.Button(leftFrame,
text='Start monitoring', padx=15, pady=10, font=("Courier",10), bg="red",
    command=lambda: threading.Thread(target=startMonitoringOnClick, args=()).start())
buttonStartMonitoring.pack(padx=5, pady=5)
#-----Left frame end

backend.parseDatabase()

#-----Webpage list on right frame
rightFrame = tk.Frame(window)
rightFrame.pack(side='right',padx=10, pady=10)

horizontalScrollbar=tk.Scrollbar(rightFrame, orient='horizontal')
horizontalScrollbar.pack()
verticalScrollbar=tk.Scrollbar(rightFrame, orient='vertical')
verticalScrollbar.pack()
webpageList=tk.Listbox(rightFrame, xscrollcommand=horizontalScrollbar.set, yscrollcommand=verticalScrollbar.set, width=200, height=20)
webpageList.pack()

for i in range(len(backend.webpageNames)):
    webpageList.insert(tk.END, '(('+backend.webpageNames[i]+')) XPath to HTML element : (('+backend.frontOfHtmlElements[i]+
    ')) className of HTML element : (('+backend.backOfHtmlElements[i]+'))')

buttonFrame=tk.Frame(rightFrame)
buttonFrame.pack()
# button: Hyperlink to webpage
buttonDeleteWebpage = tk.Button(buttonFrame, 
text='Open page', padx=10, pady=10, font=("Courier",10), bg="yellow", command=lambda: openWebpage())
buttonDeleteWebpage.pack(side='left', padx=5, pady=5)

# button: Delete webpage
buttonDeleteWebpage = tk.Button(buttonFrame, 
text='Delete', padx=10, pady=10, font=("Courier",10), bg="yellow", command=lambda: deleteWebpageOnClick())
buttonDeleteWebpage.pack(side='right', padx=5, pady=5)
#-----Webpage list end

monitoring=False
def appendWebpageOnClick():
    if(urlEntry.get()!=''):
        backend.urls.append(urlEntry.get())
    else:
        tk.messagebox.showinfo(title='Error', message='URL is essential')
        return

    if monitoring==True:
        tk.messagebox.showinfo(title='Error', message='Please turn off monitoring first')
        return

    backend.webpageNames.append(webpageNameEntry.get())
    backend.frontOfHtmlElements.append(frontOfHtmlElementEntry.get())
    backend.backOfHtmlElements.append(backOfHtmlElementEntry.get())
    # Write on the end of database
    database = open("./webpage_list.txt", 'a', encoding='utf-8')
    database.write(
        '(('+webpageNameEntry.get()+')) (('+urlEntry.get()+')) (('+frontOfHtmlElementEntry.get()+')) (('+backOfHtmlElementEntry.get()+'))\n')
    database.close()

    # Insert webpage into webpage list
    webpageList.insert(tk.END, '(('+webpageNameEntry.get()+')) XPath to HTML element : (('+frontOfHtmlElementEntry.get()+
    ')) className of HTML element : (('+backOfHtmlElementEntry.get()+'))')

    # Reset
    urlEntry.delete(0,tk.END)
    frontOfHtmlElementEntry.delete(0,tk.END)
    backOfHtmlElementEntry.delete(0,tk.END)
    webpageNameEntry.delete(0,tk.END)
buttonAppendWebpage.config(command=appendWebpageOnClick)

def deleteWebpageOnClick():
    selection=webpageList.curselection()
    if len(selection)!=0:
        i=selection[0]
    else:
        return

    webpageList.delete(i)

    backend.deleteWebpageFromDatabase(i)
    del backend.urls[i]
    del backend.frontOfHtmlElements[i]
    del backend.backOfHtmlElements[i]
    del backend.webpageNames[i]

def openWebpage():
    selection=webpageList.curselection()
    if len(selection)!=0:
        i=selection[0]
    else:
        return
    webbrowser.open(backend.urls[i])

def startMonitoringOnClick():
    print('Monitoring started')
    global monitoring
    monitoring=True
    prevHashes=[]
    for i, url in enumerate(backend.urls): # Create initial hash
        driver.get(backend.urls[i])
        if backend.frontOfHtmlElements[i]!='': # Find element by XPATH
            element=driver.find_element(By.XPATH,backend.frontOfHtmlElements[i])
            prevHashes.append(hashlib.sha224(element.text.encode('utf-8')).hexdigest())
        elif backend.backOfHtmlElements[i]!='': # Find element by class
            element=driver.find_element(By.CLASS_NAME, backend.backOfHtmlElements[i])
            prevHashes.append(hashlib.sha224(element.text.encode('utf-8')).hexdigest())
        else: # Detect any change on webpage
            response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read() # Perform a GET request and load the content of the website and store it in a var
            prevHashes.append(hashlib.sha224(response).hexdigest())

    while monitoring:
        #time.sleep(1)
        for i, url in enumerate(backend.urls):
            element=''
            response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read() # Perform the get request
            driver.get(backend.urls[i])
            if backend.frontOfHtmlElements[i]!='': # Find element by XPATH
                element=driver.find_element(By.XPATH, backend.frontOfHtmlElements[i])
                newHash=hashlib.sha224(element.text.encode('utf-8')).hexdigest()
            elif backend.backOfHtmlElements[i]!='': # Find element by class
                element=driver.find_elementr(By.CLASS_NAME, backend.backOfHtmlElements[i])
                newHash=hashlib.sha224(element.text.encode('utf-8')).hexdigest()
            else: # Detect any change on webpage
                response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read() # Perform a GET request and load the content of the website and store it in a var
                newHash=hashlib.sha224(response).hexdigest()
            if printFoundElement.get():
                print(element.text.encode('utf-8'))
                print('Previous hash: ',prevHashes[i],'New hash: ',newHash)
                print('----------------------------------')

            # Check if the new hash is different from the previous hash
            if newHash != prevHashes[i]: # If something changed in the hash
                if alarmTurnedOn.get():
                    winsound.Beep(1000, 2000)
                print("**A change detected on webpage : (",backend.webpageNames[i],')',' Time: (',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),')',sep='')
                prevHashes[i]=newHash

# def startMonitoringOnClick():
#     print('Monitoring started')
#     global monitoring
#     monitoring=True
#     prevHashes=[]
#     for i, url in enumerate(backend.urls): # Create initial hash
#         response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read() # Perform a GET request and load the content of the website and store it in a var
#         # Create initial hash
#         if backend.frontOfHtmlElements[i]!='' and backend.backOfHtmlElements[i]!='':
#             start,end=backend.findAfterString(response, backend.frontOfHtmlElements[i], backend.backOfHtmlElements[i])
#             prevHashes.append(hashlib.sha224(response[start:end]).hexdigest())
#         else: # Detect any change on webpage
#             prevHashes.append(hashlib.sha224(response).hexdigest())

#     while monitoring:
#         time.sleep(1)
#         for i, url in enumerate(backend.urls):
#             response = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read() # Perform the get request
#             if backend.frontOfHtmlElements[i]!='' and backend.backOfHtmlElements[i]!='':
#                 start,end=backend.findAfterString(response,backend.frontOfHtmlElements[i],backend.backOfHtmlElements[i])
#                 newHash=hashlib.sha224(response[start:end]).hexdigest()
#             else: # Detect any change on webpage
#                 newHash=hashlib.sha224(response).hexdigest()
#             if printFoundElement.get():
#                 print(response[start:end])
#                 print('Previous hash: ',prevHashes[i],'New hash: ',newHash)
#                 print('----------------------------------')

#             # Check if the new hash is different from the previous hash
#             if newHash != prevHashes[i]: # If something changed in the hash
#                 if alarmTurnedOn.get():
#                     winsound.Beep(1000, 2000)
#                 print("**A change detected on webpage : (",backend.webpageNames[i],')',sep='')
#                 print(prevHashes[i], newHash)
#                 prevHashes[i]=newHash

# button: Stop monitoring
def stopMonitoring():
    global monitoring
    monitoring=False
    print('Monitoring stopped')
buttonAppendWebpage = tk.Button(leftFrame,
text='Stop monitoring', padx=15, pady=10, font=("Courier",10), bg="red", command=stopMonitoring)
buttonAppendWebpage.pack(padx=5, pady=5)
#-----left frame end

window.mainloop() # Open GUI