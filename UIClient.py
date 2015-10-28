from Tkinter import *
from socket import *
from ftplib import FTP
import tkFileDialog
from tkMessageBox import *
import thread
import sys
import pyaudio
import wave

########### FILE UPLOAD ###########3

########### MODIFY ########################

USER = 'amitkmr'
PASS = '121258'

########### MODIFY IF YOU WANT ############

SERVER = 'webhome.cc.iitk.ac.in'
PORT = 21
BINARY_STORE = True # if False then line store (not valid for binary files (videos, music, photos...))

###########################################
RECORD_SECONDS = 1

connection_done = False  # to check if connection is established or not

def print_line(result):
    print(result)

def connect_ftp():
    #Connect to the server
    ftp = FTP()
    ftp.connect(SERVER, PORT)
    ftp.login(USER, PASS)

    return ftp

def upload_file(ftp_connetion, upload_file_path):

    #Open the file
    try:
        upload_file = open(upload_file_path, 'r')

        #get the name
        path_split = upload_file_path.split('/')
        final_file_name = path_split[len(path_split)-1]

        #transfer the file
        print('Uploading ' + final_file_name + '...')

        if BINARY_STORE:
            ftp_connetion.storbinary('STOR '+ final_file_name, upload_file)
        else:
            #ftp_connetion.storlines('STOR ' + final_file_name, upload_file, print_line)
            ftp_connetion.storlines('STOR '+ final_file_name, upload_file)

        print('Upload finished.')
        return

    except IOError:
        print ("No such file or directory... passing to next file")


#Take all the files and upload all
ftp_conn = connect_ftp()

def file_save():
    f = tkFileDialog.asksaveasfilename()
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    return f

def retrieveFile(list):
    Tk().withdraw()
    file_extension = list.split('.')
    if askyesno('Download File', 'Yes you really want to Download file'):
        ftp = FTP('webhome.cc.iitk.ac.in')
        ftp.login(user='amitkmr', passwd = '121258')
        filename =list
        save_path = file_save()+'.'+file_extension[1] 
        localfile = open( save_path, 'wb')
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        ftp.quit()
        showwarning('File downloaded', 'you have recieved a file')
    else:
        showinfo('File Download Cancel', 'Download quit')

def sendFile():
    Tk().withdraw()
    filePath =tkFileDialog.askopenfilename()
    #print filePath
    upload_file(ftp_conn,filePath)
    filename = filePath.split('/')
    message = "1^"+filename[-1]
    #print message
    clientSocket.sendto(message,(serverName,serverPort))
    chatBox("File sent "+filename[-1])


def sendMessage(event):
    if connection_done :
        message = entry1.get()
        clientSocket.sendto(message,(serverName,serverPort))
        chatBox("You: "+message)
    else :
        chatBox("Connection not yet established")

def recievedMessage():
    while 1:
        message, serverAddress = clientSocket.recvfrom(2048)
        splitMessage = message.split('^')
        if splitMessage[0]=="1":
            fileName = splitMessage[1]
            chatBox("He: Recieved file :" + fileName)
            retrieveFile(fileName)
        else:
            chatBox("He: " + message)

def chatBox(text):
    listbox.insert(END, text)
    listbox.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=listbox.yview)
    entry1.delete(0, END)
    return

def setIP (event):
    ipaddress = entry2.get()
    global serverName
    global connection_done
    serverName = ipaddress
    try:
        clientSocket.connect((serverName,serverPort))
        #clientSocket.sendto(message,(serverName,serverPort))
        connection_done = True
        chatBox("Connected to " + ipaddress)
    except Exception, e :
        chatBox("Unknown service")
    entry2.delete(0, END)

def start_record ():
    global RECORD_SECONDS
    RECORD_SECONDS=1
    try:
        thread.start_new_thread(record,())
    except:
        print "Error: unable to start thread"

def record():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    while RECORD_SECONDS==1:
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def stop_record():
    global RECORD_SECONDS
    RECORD_SECONDS = 0
    send_audio('output.wav')
def send_audio():
    pass
########## Socket Connection ###############
serverName = ''
serverPort = 12000
clientSocket = socket(AF_INET,SOCK_DGRAM)




#####################
#############
window = Tk()
window.title("chatWindow")
window.geometry("400x500")
frame = Frame(window)
frame.pack(side = TOP, fill = X)

frame1 = Frame(window)
frame1.pack(side = BOTTOM, fill = X)

button = Button(window, text ="Send File",command= sendFile)
button.pack(side=BOTTOM)

button1 = Button(frame1, text ="record",command= start_record)
button1.pack(side=LEFT)

button2 = Button(frame1, text ="stop & send",command= stop_record)
button2.pack(side=LEFT)


message = StringVar()
entry1 = Entry(window,text = message)
entry1.pack(side=BOTTOM,fill=X)
entry1.bind("<Return>", sendMessage)

scrollbar = Scrollbar(window)
scrollbar.pack(side=RIGHT, fill=Y)
listbox = Listbox(window, width = 50,yscrollcommand=scrollbar.set)




label1 = Label( frame, text="Connect to IP address : " , bg = "#a3dfdd" )
label1.pack(fill = X, side = LEFT, ipadx=20)

ipaddress = StringVar()
entry2 = Entry(frame,text = ipaddress,width=30)
entry2.pack(side=LEFT)
entry2.bind("<Return>", setIP)

############### Start recieved message as thread ########3
try:
   thread.start_new_thread(recievedMessage,())
except:
   print "Error: unable to start thread"
frame.pack()

window.mainloop()
