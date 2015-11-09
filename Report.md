# Chat Server

## Introduction
This project implemented a basic Peer to Peer chat program.This is a multiuser program.
Program supports text messages, voice messages and also support live voice calling.
File transfer using FTP in secure as well as normal mode is also supported as a feature
in the program.

## Methodology
We have implemented this program in python using a number of libraries such as Tkinter for GUI, socket, pyaudio for voice support, and socket for network  programming.
Work flow of the Program:
1. Server program is started that create a socket with a port, ready to listen to a client.
2. Client program create a socket connection and send message to the advertise IP address of Server.
3. Server receive  the Client message reply to the client.
4. Tkinter is used to make GUI of the program.
5. Voice message are recorded and converted in to MP3 format and sent to other peer.
6. File are sent using FTP. First they uploaded on a common server and message is sent regarding the same
if other peer say yes for the download FTP connection is set up and file is downloaded.
7. Secure file transfer preceded by step exchanging Public key of RSA encryption. File is encrypted and then sent.     
