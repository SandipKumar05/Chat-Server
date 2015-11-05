from Tkinter import *
# from socket import *
from ftplib import FTP
import tkFileDialog
from tkMessageBox import *
import thread
import sys
import pyaudio
import wave
import threading
import socket
import time
import os
from Crypto.PublicKey import RSA
from Crypto import Random
import ast

######### RSA Key Generation ##########
rng = Random.new().read
RSAkey = RSA.generate(1024, rng) 

server_privatekey = RSAkey
server_publickey = RSAkey.publickey()

file = open("server_publickey.txt", "w")
file.write(server_publickey.exportKey()) 
file.close()

file = open("client_publickey.txt", "r")
privatestr = file.read() 
file.close()
client_publickey = RSA.importKey(privatestr)

########### FILE UPLOAD ###########3

########### MODIFY ########################

USER = 'amitkmr'
PASS = '121258'

########### MODIFY IF YOU WANT ############
call_flag = True
SERVER = 'webhome.cc.iitk.ac.in'
PORT = 21
BINARY_STORE = True # if False then line store (not valid for binary files (videos, music, photos...))
CLIENT_ADDRESS = ('','')


RECORD_SECONDS = 1
CALL = 1
connection_done = False  # to check if connection is established or not

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

def secure_sendFile():
    if connection_done :
        Tk().withdraw()
        filePath =tkFileDialog.askopenfilename()
        filename = filePath.split('/')
        file_extension = filename[-1].split('.')
        data = open(filePath, "r").read()
        enc_data = client_publickey.encrypt(data, 32)
        message = ""
        if len(file_extension) == 1:
            message = "9^"+str(enc_data)
        else:
            message = "9^"+str(enc_data)+"^"+file_extension[1]
        conn.send(message)
        
        chatBox("File sent "+filename[-1])
    else :
        chatBox("Connection not yet established")

def secure_recvFile(encrypt_msg,file_extension):
    Tk().withdraw()
    if askyesno('Download File', 'Yes you really want to Download file'):
        save_path = ''
        if file_extension == '':
            save_path = file_save()
        else:
            save_path = file_save()+'.'+file_extension
        data = server_privatekey.decrypt(ast.literal_eval(encrypt_msg))
        file = open(save_path, "w")
        file.write(str(data)) 
        file.close() 
        showwarning('File downloaded', 'you have recieved a file')
    else:
        showinfo('File Download Cancel', 'Download quit')


def file_save():
    f = tkFileDialog.asksaveasfilename()
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    return f

def retrieveFile(list):
    Tk().withdraw()
    file_extension = list.split('.')
    if askyesno('Download File', 'DO you really want to Download file?'):
        ftp = FTP('webhome.cc.iitk.ac.in')
        ftp.login(user='amitkmr', passwd = '121258')
        filename =list
        save_path = ''
        if len(file_extension) == 1:
        	save_path = file_save()
        else:
        	save_path = file_save()+'.'+file_extension[1]
        localfile = open( save_path, 'wb')
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        ftp.quit()
        showwarning('File downloaded', 'you have received a file')
    else:
        showinfo('File Download Cancel', 'Download quit')


def retrieveAudio(filename):
    ftp = FTP('webhome.cc.iitk.ac.in')
    ftp.login(user='amitkmr', passwd = '121258')
    localfile = open( "sandip.wav", 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    if askyesno('play Audio','Do you want to play?'):
        play_audio(filename)
    else:
        chatBox("Audio saved")

def sendFile():
    if connection_done:
        Tk().withdraw()
        filePath =tkFileDialog.askopenfilename()
        upload_file(ftp_conn,filePath)
        filename = filePath.split('/')
        message = "1^"+filename[-1]
        conn.send(message)
        chatBox("File sent "+filename[-1])
    else:
        chatBox("Connection not yet established")

def sendMessage(event):
    if connection_done :
        message = entry1.get()
        conn.send(message)
        chatBox("You: "+message)
    else :
        chatBox("Connection not yet established")

def receivedMessage():
    while 1:
        global CLIENT_ADDRESS
        if call_flag:
            message = conn.recv(1024)
            splitMessage = message.split('^')
            if splitMessage[0]=="7":
                showinfo('Chat Disconnected', 'Chat Disconnected')
                global connection_done
                connection_done = False
                window.destroy()
            elif splitMessage[0]=="1":
	            fileName = splitMessage[1]
	            chatBox("received file :" + fileName)
	            retrieveFile(fileName)
            elif splitMessage[0]=="2":
	            chatBox(splitMessage[1])
	            connection_done = True
            elif splitMessage[0]=="3":
	            if askyesno('Incoming Call', 'Do you want to receive?'):
	            	message = "5^accept call"
	            	conn.send(message)
	                call1()
	            else:
	                message = "6^end call"
	                conn.send(message)
            elif splitMessage[0]=="5":
	        	    call1()
            elif splitMessage[0]=="6":
	       		chatBox("Call Rejected")
            elif splitMessage[0]=="8":
                fileName = splitMessage[1]
                retrieveAudio(fileName)
            elif splitMessage[0]=="9":
                chatBox("Received file")
                secure_recvFile(splitMessage[1],splitMessage[2])
            else:
	        	if message != '':
	        		chatBox("He: " + message)

def chatBox(text):
    listbox.insert(END, text)
    listbox.pack(side=LEFT, fill=BOTH)
    listbox.yview(END)
    scrollbar.config(command=listbox.yview)
    entry1.delete(0, END)
    return

# def setIP (event):
#     ipaddress = entry2.get()
#     global serverName
#     global connection_done
#     global CLIENT_ADDRESS
#     serverName = ipaddress
#     CLIENT_ADDRESS = (serverName,serverPort)
#     try:
#         conn.connect(CLIENT_ADDRESS)
#         message = "2^Someone has connected to you"
#         conn.send(message)
#         connection_done = True
#         chatBox("Connected to " + ipaddress)
#     except Exception, e :
#         chatBox("Unknown service")
#     entry2.delete(0, END)

def start_record ():
    if connection_done:
        global RECORD_SECONDS
        RECORD_SECONDS=1
        button2.config(state="normal")
        button1.config(state=DISABLED)
        try:
            thread.start_new_thread(record,())
        except:
            print "Error: unable to start thread"
    else:
        chatBox("Connection not yet established")

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

    chatBox("* recording")

    frames = []

    while RECORD_SECONDS==1:
        data = stream.read(CHUNK)
        frames.append(data)


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
    chatBox("done recording")
    button1.config(state="normal")
    button2.config(state=DISABLED)
    send_audio('output.wav')

def send_audio(audio_file):
    upload_file(ftp_conn,audio_file)
    message = "8^"+audio_file
    conn.send(message)

def play_audio(filename):
    chunk = 1024

    # open the file for reading.
    wf = wave.open(filename, 'rb')

    # create an audio object
    p = pyaudio.PyAudio()

    # open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # play stream (looping from beginning of file to the end)
    while data != '':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)

    stream.close()    
    p.terminate()

def call():
    if connection_done:
        message = "3^incoming call"
        conn.send(message)
    else:
        chatBox("Connection not yet established")
    
def call1():
    entry1.config(state=DISABLED)
    global call_flag
    call_flag = False
    global CALL
    CALL =1
    button4.config(state="normal")
    button3.config(state=DISABLED)
    threading.Thread(target=call_send).start()
    threading.Thread(target=call_recv).start()

def end_call1():
    global CALL
    CALL = 0
    chatBox("* call ended")
    global call_flag
    call_flag = True
    entry1.config(state="normal")
    button3.config(state="normal")
    button4.config(state=DISABLED)

def end_call():
    global CALL
    CALL = 0
    time.sleep(2)
    message="4^incoming call"
    conn.send(message)
    chatBox("* call ended")
    global call_flag
    call_flag = True
    entry1.config(state="normal")
    button3.config(state="normal")
    button4.config(state=DISABLED)

def call_send():
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 20

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
	                frames_per_buffer=CHUNK)

	chatBox("* call start")

	frames = []
	# chatBox(CALL)
	while CALL==1:
	 data  = stream.read(CHUNK)
	 frames.append(data)
	 conn.sendall(data)
	 if CALL == 0:
	 	return

	# chatBox("chat_end")
	stream.stop_stream()
	stream.close()
	p.terminate()

def call_recv():

	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 20
	WAVE_OUTPUT_FILENAME = "server_output.wav"
	WIDTH = 2
	frames = []

	p = pyaudio.PyAudio()
	stream = p.open(format=p.get_format_from_width(WIDTH),
	                channels=CHANNELS,
	                rate=RATE,
	                output=True,
	                frames_per_buffer=CHUNK)

	data = conn.recv(1024)

	while CALL==1:
	    stream.write(data)
	    data = conn.recv(1024)
	    splitMessage = data.split('^')
	    if splitMessage[0]=="4":
	    	 # chatBox("please call end")
	         end_call1()
	         return 
	    frames.append(data)
	    if CALL ==0:
	    	return

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

	stream.stop_stream()
	stream.close()
	p.terminate()

def new_chat():
    os.system("python UIClient.py &")

def on_closing():
    if askokcancel("Quit", "Do you want to quit?"):
        global connection_done 
        if connection_done:
            message="7^chat end"
            conn.send(message)
            connection_done = False
            window.destroy()
            s.close()
        else:
            connection_done = False
            window.destroy()

########## Socket Connection ###############
serverName = ''
serverPort = 12000

# s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind(('', serverPort))
# s.listen(1)
# conn, addr = s.accept()
# conn, addr = s.accept()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', serverPort))
s.listen(1)
conn, addr = s.accept()

window = Tk()
window.title("chatWindow")
window.geometry("400x500")
frame = Frame(window)
frame.pack(side = TOP, fill = X)

frame1 = Frame(window)
frame1.pack(side = BOTTOM, fill = X)

button6 = Button(window, text ="Secure Send File",command= secure_sendFile)
button6.pack(side=BOTTOM)

button = Button(window, text ="Send File",command= sendFile)
button.pack(side=BOTTOM)

button1 = Button(frame1, text ="record",command= start_record, bg='#63dd7a',state='normal')
button1.pack(side=LEFT)

button2 = Button(frame1, text ="stop & send",command= stop_record, bg='#e86f5e',state=DISABLED)
button2.pack(side=LEFT)

button4 = Button(frame1, text ="End",command= end_call,bg = '#df2620',state=DISABLED)
button4.pack(side=RIGHT)

button3 = Button(frame1, text ="Call",command= call, bg = '#29ab22',state='normal')
button3.pack(side=RIGHT)

button5 = Button(frame, text ="New Chat",command= new_chat,bg = '#0b2fee')
button5.pack(side=TOP,fill=X)

message = StringVar()
entry1 = Entry(window,text = message)
entry1.pack(side=BOTTOM,fill=X)
entry1.bind("<Return>", sendMessage)

scrollbar = Scrollbar(window)
scrollbar.pack(side=RIGHT, fill=Y)
listbox = Listbox(window, width = 50,yscrollcommand=scrollbar.set)

window.protocol("WM_DELETE_WINDOW", on_closing)


# label1 = Label( frame, text="Connect to IP address : " , bg = "#a3dfdd" )
# label1.pack(fill = X, side = LEFT, ipadx=20)

# ipaddress = StringVar()
# entry2 = Entry(frame,text = ipaddress,width=30)
# entry2.pack(side=LEFT)
# entry2.bind("<Return>", setIP)

############### Start received message as thread ########3
try:
   thread.start_new_thread(receivedMessage,())
except:
   print "Error: unable to start thread"
frame.pack()

window.mainloop()