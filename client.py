import socket
from _thread import *
import threading 
import os
import time
from cryptography.fernet import Fernet
import emoji
from tkinter import *
from tkinter import messagebox

def call_key():
    return open("key.key", "rb").read()

connect_lock = threading.Lock()   
class Client:
    portnumber=0
    myserver=0
    mainserver=0
    username = ""
    end = True

    def __init__(self,username):   #This function is for craeting Peer, Creating threads and Socket for the peer, assigning username,ports to the peer
        super().__init__()
        self.username = username
        u_name=username
        self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Connecting to the server so that server adds to the network
        self.mainserver.connect(('localhost',12345))
        self.mainserver.send(('Hello').encode())
        self.mainserver.recv(1024)
        self.mainserver.send(('@'+username).encode())
        reply= self.mainserver.recv(1024)
        if reply == b'yes':   #Getting list of files from server
           print('yes')
           self.portnumber=int(self.mainserver.recv(1024))   
           print(self.portnumber)
           start_new_thread(self.startserver, ()) 
           filestr = self.getfileslist()
           msg = str(len(filestr))
           print(msg)
           self.mainserver.send(msg.encode())
           self.mainserver.send(filestr.encode())
           self.mainserver.close()
           t2 = threading.Thread(target=self.menu_gui())  #Creating thread for GUI
           t2.start()

           
           
           end = "Bye"
           self.end=False
           t2.join()  #Joining the network
           self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
           self.mainserver.connect(('localhost',12345)) #connecting tot he server
           self.mainserver.send(end.encode())
           print(self.mainserver.recv(1024))
           self.mainserver.send((self.username).encode())
           self.mainserver.close()
           if self.myserver!=0:
              self.myserver.close()

        else:
            print("Invalid User")
       
        


    def startserver(self):  #Starting the server, Creating threads for Inter process communication 
        try:  
            self.myserver  = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.myserver.bind(("",self.portnumber))
            self.myserver.listen()  #Binding and listening the connection
            
            print('Self Server Started Successfully',self.myserver)
            while self.end: 
                c,addr = self.myserver.accept()
                start_new_thread(self.handle, (c,))  #Starting thraed for handling incoming operations
        except Exception as e:
            print("")
                
                

    
    def download(self,c,filename):  #This fuction downloads the required file after requesting it from the other peers
        op="get"
        c.send(op.encode())  #Encoding the data
        c.recv(1024)
        c.send(filename.encode())
        filepath = self.username+"\\"+filename #Path for the file to store
        with open(filepath,'ab+') as wrt: #Writting the file to the location
            while(True):
                f = c.recv(1024)
                if not f:
                    break
                wrt.write(f)
        self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.mainserver.connect(('localhost',12345)) #connecting to the server
        op = "upd"
        self.mainserver.send(op.encode())
        print(self.mainserver.recv(1024))
        self.mainserver.send(self.username.encode())
        print(self.mainserver.recv(1024))
        filename = self.getfileslist()  
        self.mainserver.send(filename.encode())  #Sending file details to server so that it can assist in downloading
        self.mainserver.close() 


    def handle(self,c): #This function is to for handling any incoming files or messages. Messaging and file sharing is done using this function

        op=c.recv(1024)
        if op==b'msg':
            
            msg = "Hello" #Group Chat Implementation
            c.send(msg.encode())
            msg  = c.recv(1024)
            key = call_key()
            f = Fernet(key)
            decrypted_msg = f.decrypt(msg)
            decrypted_msg = decrypted_msg.decode()   #Decrypting the message
            msg = msg.decode()
            self.textCons.config(state = NORMAL) 
            self.textCons.insert(END, 
                                decrypted_msg+"\n\n") 
                      
            self.textCons.config(state = DISABLED) 
            self.textCons.see(END)
            print(msg)
            print('\n')
            
        elif op==b'file':  #File sharing implementation
            msg = "Hello"
            c.send(msg.encode())
            filename=c.recv(1024)
            filename=filename.decode()
            c.send(filename.encode())
            filepath = self.username+"\\"+filename  #Defining path for the file
            with open(filepath,'ab+') as w:
                while(True):
                    f = c.recv(1024)
                    if not f:
                        break
                    w.write(f)  #Writting the file
            self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.mainserver.connect(('localhost',12345))
            op = "upd"
            self.mainserver.send(op.encode())
            print(self.mainserver.recv(1024))
            self.mainserver.send(self.username.encode())
            print(self.mainserver.recv(1024))
            filename = self.getfileslist()
            self.mainserver.send(filename.encode())
            self.mainserver.close()
                
                
    def goAhead(self, name): 
        self.menu_list.destroy() 
        self.layout(name) 
    # The main layout of the chat using GUI
    def layout(self,name): 
        
        self.name = name 
        # This is the GUI to show chat window 
        self.Window.deiconify() 
        self.Window.title("CHATROOM") 
        self.Window.resizable(width = False, 
                              height = False) 
        self.Window.configure(width = 470, 
                              height = 550, 
                              bg = "#17202A") 
        self.labelHead = Label(self.Window, 
                             bg = "#17202A",  
                              fg = "#EAECEE", 
                              text = self.name , 
                               font = "Helvetica 13 bold", 
                               pady = 5) 
          
        self.labelHead.place(relwidth = 1) 
        self.line = Label(self.Window, 
                          width = 450, 
                          bg = "#ABB2B9") 
          
        self.line.place(relwidth = 1, 
                        rely = 0.07, 
                        relheight = 0.012) 
          
        self.textCons = Text(self.Window, 
                             width = 20,  
                             height = 2, 
                             bg = "#17202A", 
                             fg = "#EAECEE", 
                             font = "Helvetica 14",  
                             padx = 5, 
                             pady = 5) 
          
        self.textCons.place(relheight = 0.745, 
                            relwidth = 1,  
                            rely = 0.08) 
          
        self.labelBottom = Label(self.Window, 
                                 bg = "#ABB2B9", 
                                 height = 80) 
          
        self.labelBottom.place(relwidth = 1, 
                               rely = 0.825) 
          
        self.entryMsg = Entry(self.labelBottom, 
                              bg = "#2C3E50", 
                              fg = "#EAECEE", 
                              font = "Helvetica 13") 
          
        # place the given widget 
        # into the gui window 
        self.entryMsg.place(relwidth = 0.74, 
                            relheight = 0.06, 
                            rely = 0.008, 
                            relx = 0.011) 
          
        self.entryMsg.focus() 
        # create a Send Button 
        self.buttonMsg = Button(self.labelBottom, 
                                text = "Send", 
                                font = "Helvetica 10 bold",  
                                width = 20, 
                                bg = "#ABB2B9", 
                                command = lambda : self.eww(self.entryMsg.get())) 
          
        self.buttonMsg.place(relx = 0.77, 
                             rely = 0.008, 
                             relheight = 0.06,  
                             relwidth = 0.22) 
          
        self.textCons.config(cursor = "arrow") 
          
        # create a scroll bar 
        scrollbar = Scrollbar(self.textCons) 
          
        # place the scroll bar  
        # into the gui window 
        scrollbar.place(relheight = 1, 
                        relx = 0.974) 
          
        scrollbar.config(command = self.textCons.yview) 
          
        self.textCons.config(state = DISABLED) 
  

    def menu_gui(self):
        self.Window = Tk()
        self.Window.withdraw() 
# menu window 
        self.menu_list = Toplevel() 
# set the title 
        self.menu_list.title("Menu") 
        self.menu_list.resizable(width = False,  
                height = False) 
        self.menu_list.configure(width = 400, 
                height = 300) 
        # create a Label 
        self.pls = Label(self.menu_list,  
                        text = "Select any of the option from the following!", 
                        justify = CENTER,  
                        font = "Helvetica 10 bold") 
        self.pls.place(relheight = 0.09, 
                        relx = 0.2,  
                        rely = 0.07) 
        self.op1 = Label(self.menu_list,  
                        text = "1)Disconnect fromnetwork(exit)", 
                        justify = RIGHT,  
                        font = "Helvetica 10") 
        self.op1.place(relheight = 0.1, 
                        relx = 0.1,  
                        rely = 0.2) 
        self.op2 = Label(self.menu_list,  
                        text = "2)Request a File", 
                        justify = RIGHT,  
                        font = "Helvetica 10") 
        self.op2.place(relheight = 0.1, 
                        relx = 0.1,  
                        rely = 0.3)   
        self.op2 = Label(self.menu_list,  
                        text = "3)Upload File", 
                        justify = RIGHT,  
                        font = "Helvetica 10") 
        self.op2.place(relheight = 0.1, 
                        relx = 0.1,  
                        rely = 0.4)      
        self.op2 = Label(self.menu_list,  
                        text = "4)Group chat", 
                        justify = RIGHT,  
                        font = "Helvetica 10") 
        self.op2.place(relheight = 0.1, 
                        relx = 0.1,  
                        rely = 0.5)      
        self.labelName = Label(self.menu_list, 
                        text = "Option: ", 
                        font = "Helvetica 10") 
          
        self.labelName.place(relheight = 0.1, 
                        relx = 0.25,  
                        rely = 0.6) 
          
        # create a entry box for  
        # tyoing the message 
        self.entryName = Entry(self.menu_list,  
                        font = "Helvetica 10") 
          
        self.entryName.place(relwidth = 0.1,  
                            relheight = 0.1, 
                            relx = 0.37, 
                            rely = 0.6 )
        self.go = Button(self.menu_list, 
                        text = "CONTINUE",  
                        font = "Helvetica 10 bold",
                        command = lambda: self.menu(self.entryName.get()))  
        self.go.place(relx = 0.37, 
                      rely = 0.7) 
        self.Window.mainloop()


    def eww(self,msg):  #The python code for Group Chat

        self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #Getting peer list from server in order to build the connection
        self.mainserver.connect(('localhost',12345))
        op = "get"
        self.mainserver.send(op.encode())
        print(self.mainserver.recv(1024))
        peerlist = self.mainserver.recv(1024)
        peerlist = peerlist.decode()
        peerlist = peerlist.split(' ')
        self.mainserver.close()
        i=0
        peerlist.pop(0)
        peerlist.pop(0)
                
        op="msg"
        msg = self.username+":"+msg  #Storing the message with the sender name
        while i<len(peerlist):
            port = int(peerlist[i+1])
            peername = peerlist[i]
            smg = msg.encode()
            key = call_key()
            f = Fernet(key)
            smg = f.encrypt(smg)  #Encrypting the message
            conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #Connecting to the other peers in the network
            conn.connect(('localhost',port)) 
            start_new_thread(self.handle,  (conn,))
            conn.send(op.encode())
            conn.recv(1024)
            conn.send(smg)  #Sending the message
            i=i+2
        #self.menu_gui()
    
    def Upfile_gui(self):  #GUI TO UPLOAD FILE TO THE OTHER PEERS
        self.menu_list.destroy()
        self.Window = Tk()
        self.Window.withdraw() 

        self.upload_list = Toplevel() 

        self.upload_list.title("File") 
        self.upload_list.resizable(width = False,  
                                    height = False) 
        self.upload_list.configure(width = 400, 
                                    height = 300) 
        # create a Label 
        self.pls = Label(self.upload_list,  
                        text = "File Upload!", 
                        justify = CENTER,  
                        font = "Helvetica 10 bold") 
        self.pls.place(relheight = 0.09, 
                        relx = 0.3,  
                        rely = 0.07) 
        self.op1 = Label(self.upload_list,  
                        text = "1)Upload a file!", 
                        justify = CENTER,  
                        font = "Helvetica 10") 
        self.op1.place(relheight = 0.1, 
                        relx = 0.3,  
                        rely = 0.2) 
    
    
        self.labelName = Label(self.upload_list, 
                                text = "File name: ", 
                                font = "Helvetica 10") 
          
        self.labelName.place(relheight = 0.1, 
                                relx = 0.3,  
                                rely = 0.3) 
          
        # create a entry box for  
        # tyoing the message 
        self.entryName = Entry(self.upload_list,  
                                font = "Helvetica 10") 
          
        self.entryName.place(relwidth = 0.1,  
                                relheight = 0.1, 
                                relx = 0.47, 
                                rely = 0.3 )
        self.go = Button(self.upload_list, 
                        text = "upload",  
                        font = "Helvetica 10 bold",
                        command = lambda: self.upfile(self.entryName.get())) 
        self.go.place(relx = 0.57, 
                      rely = 0.3) 
    
        self.Window.mainloop()

    def upfile(self,filename): #Python code for uploading files to the other peers
        op = "get"
        filename=str(filename)
        self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Getting peer list from server to uploa files
        self.mainserver.connect(('localhost',12345))
        self.mainserver.send(op.encode())
        print(self.mainserver.recv(1024))
        peerlist = self.mainserver.recv(1024)
        peerlist = peerlist.decode()
        peerlist = peerlist.split(' ')  #Seperating peers from the peerlist
        peerlist.pop(0)
        peerlist.pop(0)
        print("The available peers are: ",peerlist)  #available peers in the network
        op="file"
        i=0
        while i<len(peerlist):  #Connecting to all the peers available in the network
            port =int(peerlist[i+1])
            peername = peerlist[i]
            print('Uploading file to: ',peername)  
            conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #Connecting to the peers
            conn.connect(('localhost',port))
            start_new_thread(self.handle, (conn,)) 
            conn.send(op.encode())
            conn.recv(1024)
            conn.send(filename.encode())   #Sending files to the peers
            i=i+2  
            value=3
            self.ck_box(value)
        

    def reqfile_gui(self):   #Gui for requesting file from the other peers
            self.menu_list.destroy()
            self.Window = Tk()
            self.Window.withdraw() 
# menu window 
            self.file_list = Toplevel() 
# set the title 
            self.file_list.title("File") 
            self.file_list.resizable(width = False,  
                                    height = False) 
            self.file_list.configure(width = 400, 
                                    height = 300) 
        # create a Label 
            self.pls = Label(self.file_list,  
                            text = "File Request!", 
                            justify = CENTER,  
                            font = "Helvetica 10 bold") 
            self.pls.place(relheight = 0.09, 
                            relx = 0.3,  
                            rely = 0.07) 
            self.op1 = Label(self.file_list,  
                            text = "1)Request a file!", 
                            justify = CENTER,  
                            font = "Helvetica 10") 
            self.op1.place(relheight = 0.1, 
                            relx = 0.3,  
                            rely = 0.2) 
    
    
            self.labelName = Label(self.file_list, 
                            text = "File name: ", 
                            font = "Helvetica 10") 
          
            self.labelName.place(relheight = 0.1, 
                            relx = 0.3,  
                            rely = 0.3) 
          
        # create a entry box for  
        # tyoing the message 
            self.entryName = Entry(self.file_list,  
                            font = "Helvetica 10") 
          
            self.entryName.place(relwidth = 0.1,  
                            relheight = 0.1, 
                            relx = 0.47, 
                            rely = 0.3 )
            self.go = Button(self.file_list, 
                            text = "find",  
                            font = "Helvetica 10 bold",
                            command = lambda: self.filereq(self.entryName.get())) 
            self.go.place(relx = 0.57, 
                        rely = 0.3) 
    
            self.Window.mainloop() 


    def ck_box(self,value):  #GUI for file transfer
        self.top = Tk()
        self.top.geometry("100x100")
        if value==1:
            self.file_list.destroy()
            messagebox.showerror("error","No peers found")
            self.menu_gui()
        if value==2:
            self.file_list.destroy()
            messagebox.askyesno("File Transfer Successfully","Got It?")
            self.menu_gui()
        if value==3:
            self.upload_list.destroy()
            messagebox.askyesno("File Uploaded Successfully","Got It?")
            self.menu_gui()
        self.top.mainloop()


        

    def filereq(self,filename):   #Python cde for requesting a file from the other peers in the network
        filename=str(filename)
        msg = "Acquire"
        value=0
        self.mainserver = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.mainserver.connect(('localhost',12345))  #Connecting tot he server so that it can check which peer has the required file
        self.mainserver.send(msg.encode()) 
        print(self.mainserver.recv(1024))
        self.mainserver.send(filename.encode())  #Sending file name to the server
        peerlist=self.mainserver.recv(1024)
        peerlist = peerlist.decode()
        peerlist = peerlist.split(' ') #getting the peer with desired file
        if len(peerlist) == 2:
            print("No peer found")
            value=1
            self.ck_box(value) 
        peerlist.pop(0)
        peerlist.pop(0)
        print(peerlist)
        i=0
        while i<len(peerlist): #Connecting peers
            port =int(peerlist[i+1])
            peername = peerlist[i]
            print('Getting File From ',peername)
            conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #Connecting to the particular peer
            conn.connect(('localhost',port))
            if conn ==0 :
                i=i+2
                continue
            start_new_thread(self.download, (conn,filename,))   # Getting file from the peer
            value=2
            self.ck_box(value)
            break

    def menu(self,choice): #A menu to call GUI, where you can select different operations from the given options.
        #It will call the gui for th required operation 
        while True:
            choice=int(choice)
            if choice == 1:
                self.menu_list.destroy()
            elif choice == 2:
                self.reqfile_gui()
                
            elif choice== 3:
                self.Upfile_gui()
                
                pass

            elif choice == 4:
                self.goAhead(self.username)
                print("Group Chatting")
                msg=input("Enter q to quit: ")
                while msg!='q':
                    msg = input("Enter a Message (enter q to quit):")
                    if msg== "q":
                        break 
                    pass
                           
            else:
                continue

                    
                    

              
    def getfileslist(self):  #Getting list of files from the server
        try:
            files = os.listdir(self.username)
            filestr =""
            for f in files:
                filestr=filestr+"^"+f
            return filestr
        except:
            print("User Folder not Found")

def obj_create(name): #Creating object of client class
    obj = Client(name)


def Welcome_Gui():   #Creating GUI  for login terminal
    Window = Tk()
    Window.withdraw() 
# login window 
    login = Toplevel() 
# set the title 
    login.title("Login") 
    login.resizable(width = False,  
                height = False) 
    login.configure(width = 400, 
                height = 300) 
        # create a Label 
    pls = Label(login,  
            text = "Please login to continue", 
            justify = CENTER,  
            font = "Helvetica 14 bold") 
          
    pls.place(relheight = 0.15, 
        relx = 0.2,  
        rely = 0.07) 
        # create a Label 
    labelName = Label(login, 
                text = "Name: ", 
                font = "Helvetica 12") 
          
    labelName.place(relheight = 0.2, 
                relx = 0.1,  
                rely = 0.2) 
          
        # create a entry box for  
        # tyoing the message 
    entryName = Entry(login,  
                  font = "Helvetica 14") 
          
    entryName.place(relwidth = 0.4,  
                relheight = 0.12, 
                relx = 0.35, 
                rely = 0.2) 
    # set the focus of the curser 
    entryName.focus() 
          
        # create a Continue Button  
        # along with action 
    go = Button(login, 
                text = "CONTINUE",  
                font = "Helvetica 14 bold",  
                command = lambda: obj_create(entryName.get())) 
          #------------------------------------------
    go.place(relx = 0.4, 
                      rely = 0.55) 
    #login.destroy() 
    Window.mainloop()    

    


Welcome_Gui()

input("Press any key to continue")