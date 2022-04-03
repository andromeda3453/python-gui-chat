import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


HOST = "127.0.0.1"
PORT = 9090


class Client:

    FORMAT = "utf-8"

    def __init__(self, host, addr):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, addr))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring(
            "Nickname", "Please enter a nickname", parent=msg
        )

        self.gui_done = False
        self.running = True

        # separate threads for handling gui and receiving messages so that gui remains responisve
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):

        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):

        """
        Method that handles extracting message from message box and sending it to the server
        """
        # get text from beginning till end from text boc
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode(Client.FORMAT))
        # clear the message text box
        self.input_area.delete("1.0", "end")

    def stop(self):
        """
        Removes the client from the chat
        """
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        """
        Handles receiving messages from the server
        """
        while self.running:

            try:
                message = self.sock.recv(1024).decode(Client.FORMAT)
                if message == "NICK":
                    self.sock.send(self.nickname.encode(Client.FORMAT))
                else:

                    # check to make sure gui has been built
                    if self.gui_done:
                        # enable text area before changing it
                        self.text_area.config(state="normal")
                        self.text_area.insert("end", message)
                        # scroll down to the most recent message
                        self.text_area.yview("end")
                        self.text_area.config(state="disabled")

            except ConnectionAbortedError:
                # in this case socket is already closed so we can terminate the loop and the receive thread along with it
                break
            except:
                print("Error occured")
                # for any other type of error we need to close the socket first
                self.sock.close()

                break


client = Client(HOST, PORT)
