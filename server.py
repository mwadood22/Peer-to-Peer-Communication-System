import socket 
from _thread import *
import threading 

from cryptography.fernet import Fernet

key  = Fernet.generate_key()

with open("key.key","wb") as f:
    f.write(key)


connect_lock = threading.Lock() 
a_ports = ["12346","12347","12348","12349","12350","12351","12352"] #Available Ports for the server
peers=[]
class peer:
    port=0
    username=""
    files=[]

f = open("users.txt")
users = f.readline()
users = users.split(' ') #Reading the peers from the file

def threaded(c):  #Creating Threadsd
     
    try:
        data = c.recv(1024) 
        print(data)
        connect_lock.aquire()
        if not data:
            pass
    except:
        print()

    if data == b'get':  #Extracting the peer list (peers available in the network)
        msg = 'Hello'
        c.send(msg.encode())
        peerlist=["null"]
        for p in peers:     
            peerlist.append(p.username)
            peerlist.append(p.port)
        reply = ""
        for p in peerlist:
            reply = reply+" "+p
        c.send(reply.encode())

    elif data == b'Acquire':  #Getting information about the peer who has the particular file
        msg = "Hello"
        c.send(msg.encode())
        data = c.recv(1024)
        data = data.decode()
        data = str(data)
        peerlist = ["null"]
        for p in peers:
            for f in p.files:
                if f == data:
                    peerlist.append(p.username)
                    peerlist.append(p.port)
        reply = ""
        for p in peerlist:
            reply = reply+" "+p
        c.send(reply.encode())
    
    
    elif data == b'upd':  #Downloading file uploaded by the other peer
        msg = "Hello"
        c.send(msg.encode())
        user=c.recv(1024)
        print(user)
        user = user.decode()
        c.send(msg.encode())
        filestr=c.recv(1024)
        filestr = filestr.decode()
        print(filestr)

        for p in peers:
            if p.username.encode()==user:
                length = c.recv(1024)
                length = length.decode()
                length = int(length)
                
                msg=""
                i=0
                if(length<=1024):
                    temp=c.recv(1024)
                    temp = temp.decode()
                    msg=temp
                else:
                    while(i<length):
                        temp = c.recv(1024)
                        temp = temp.decode()
                        print(temp)
                        msg = msg+temp
                        i = i+1024
            
                msg = msg.split("^")
                msg.pop(0)
                p.files=msg
        


    elif data == b'Bye':  #Disconnecting the peer fro the network
        try:
            msg = "Hello"
            c.send(msg.encode())
            user = c.recv(1024)
            user = user.decode()
            i=0
            for p in peers:
                if p.username==user:
                    a_ports.append(p.port)
                    print("Peer Disconnected:",user)
                    peers.pop(i)
                i=i+1
        except Exception as e:
            print("Peer Abandoned")
            pass
    elif data == b'Hello':  #Responding the peer
        connect_lock.acquire()
        data = (data.decode()+" from Server").encode()
        c.send(data)
        data = c.recv(1024)
        data=data.decode()
        print(data)
        data = str(data)
        user = data.replace('@','')
        if user in users and user not in [p.username for p in peers]:
            
            p=peer()
            p.username=user
            reply = "yes"
            data = reply.encode()
            print(data)
            c.send(data)
            p.port=a_ports[0]
            data=a_ports.pop(0).encode()
            c.send(data)
            
            length = c.recv(1024)
            length = length.decode()
            length = int(length)
            print(length)
            msg=""
            i=0
            if(length<=1024):
                temp=c.recv(1024)
                temp = temp.decode()
                msg=temp
            else:
                while(i<length):
                    temp = c.recv(1024)
                    temp = temp.decode()
                    print(temp)
                    msg = msg+temp
                    i = i+1024
            
            msg = msg.split("^")
            msg.pop(0)
            p.files=msg
            
            peers.append(p)
            print([p.username for p in peers])
            

        else:      #Checking the query
            reply = "no"
            c.send(reply.encode())
        connect_lock.release()

    else:   
        try:
            msg = "Invalid Query"
            c.send(msg.encode())
        except Exception as e:
            pass
   
        
        
    
        
            
    c.close() 
    
  
  
def Main():  #Main entry point (creating server)
    host = "" 

    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("Server binded to port", port) 
  
    
    s.listen(10) 
    print("Server is listening") 
  
   
    while True:  #Accepting Connection and creating threads
  
        
        c, addr = s.accept() 
        
        #print('Connected to',addr)
        connect_lock.acquire()
        start_new_thread(threaded, (c,)) 
        connect_lock.release()
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 
