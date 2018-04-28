import time
import socket
import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
import _thread
import re

from bidirectional_discovery import Bidirectional_discovery
from bidirectional_communication import Bidirectional_communication
from rsa_encryption import RSA_encryption

class ConnectButton():
    def __init__(self, frame, onclick, value):
        self.connect_button = tk.Button(frame, text="Connect", command=self.clicked)
        self.onclick = onclick
        self.value = value

    def clicked(self):
        self.onclick(self.value)

class GridButton():
    def __init__(self, frame, x, y, onclick):
        self.button = tk.Button(frame, text=" ", command=self.clicked, height=2, width=2)
        self.onclick = onclick
        self.x = x
        self.y = y

    def clicked(self):
        self.onclick(self.x, self.y)

class GameWindow():
    def center_window(self):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = 1024
        height = 768
        x_position = int(screen_width / 2 - width / 2)
        y_position = int(screen_height / 2 - height / 2)
        self.window.geometry("{}x{}+{}+{}".format(width, height, x_position, y_position))

    def connect_to_player(self, ip, port):
        self.game_connection_sender = socket.socket()
        self.game_connection_sender.settimeout(5)
        self.game_connection_sender.connect((ip, port))

    def run_window(self):
        self.window.mainloop()

    def set_game_state(self, state=""):
        if state == "":
            self.window.title("Gomoku")
        else:
            self.window.title("Gomoku - {}".format(state))

    def clear_frame(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = tk.Frame(self.window)
        self.menu_frame.place(relx=.5, rely=.5, anchor="c")

    def display_gui(self, state):
        self.clear_frame()

        button_font = font.Font(size="20")
        label_font = font.Font(size="24")

        if state == 0:
            local_multiplayer_button = tk.Button(self.menu_frame, text="Local Multiplayer", font=button_font, command=self.setup_local_game)
            local_multiplayer_button.grid(row=0, columnspan=2, sticky="NSEW")
            connect_button = tk.Button(self.menu_frame, text="Connect", font=button_font, command=self.discover_hosts)
            connect_button.grid(row=1, column=0, sticky=tk.NSEW)
            create_button = tk.Button(self.menu_frame, text="Create Game", font=button_font, command=self.setup_game)
            create_button.grid(row=1, column=1, sticky=tk.NSEW)

        if state == 1:
            width_label = tk.Label(self.menu_frame, text="Grid width:", font=label_font)
            width_label.grid(row=0, column=0, sticky="w")
            self.width_value = tk.IntVar(self.menu_frame, value=20)
            width_entry = tk.Entry(self.menu_frame, textvariable=self.width_value)
            width_entry.grid(row=0, column=1)
            height_label = tk.Label(self.menu_frame, text="Grid height:", font=label_font)
            height_label.grid(row=1, column=0, sticky="w")
            self.height_value = tk.IntVar(self.menu_frame, value=20)
            height_entry = tk.Entry(self.menu_frame, textvariable=self.height_value)
            height_entry.grid(row=1, column=1)
            if not self.local_game:
                separator = ttk.Separator(self.menu_frame)
                separator.grid(row=2, columnspan=2, sticky="we")
                port_label = tk.Label(self.menu_frame, text="Port:", font=label_font)
                port_label.grid(row=3, column=0, sticky="w")
                self.port_value = tk.IntVar(self.menu_frame, value=65530)
                port_entry = tk.Entry(self.menu_frame, textvariable=self.port_value)
                port_entry.grid(row=3, column=1)
                #password_label = tk.Label(self.menu_frame, text="Password:", font=label_font)
                #password_label.grid(row=4, column=0, sticky="w")
                #self.password_value = tk.StringVar()
                #password_entry = tk.Entry(self.menu_frame, textvariable=self.password_value)
                #password_entry.grid(row=4, column=1)
                #message_label = tk.Label(self.menu_frame, text="Leave empty for no password")
                #message_label.grid(row=5, columnspan=2)
            separator2 = ttk.Separator(self.menu_frame)
            separator2.grid(row=6, columnspan=2, sticky="we")
            go_button = tk.Button(self.menu_frame, text="Confirm", command=self.start_loading)
            go_button.grid(row=7, columnspan=2)

        if state == 2:
            port_label = tk.Label(self.menu_frame, text="Port:", font=label_font)
            port_label.grid(row=0, column=0, sticky="w")
            self.port_value = tk.IntVar(self.menu_frame, value=65530)
            port_entry = tk.Entry(self.menu_frame, textvariable=self.port_value)
            port_entry.grid(row=0, column=1)
            go_button = tk.Button(self.menu_frame, text="Confirm", command=self.discover_hosts)
            go_button.grid(row=1, columnspan=2)

        if state == 3:
            waiting_label = tk.Label(self.menu_frame, text="Waiting...", font=label_font)
            waiting_label.grid(row=0)

        if state == 4:
            searching_label = tk.Label(self.menu_frame, text="Searching...", font=label_font)
            searching_label.grid(row=0)

        if state == 5:
            self.game_frame = tk.Frame(self.menu_frame)
            self.game_frame.grid(row=0, column=0)

    def discover_hosts(self):
        self.display_gui(4)
        self.connection_options = []
        self.connection_frames = []
        self.discovery.start_discovery(self.new_server_found, self.server_timeout)

    def start_network_game(self):
        self.display_gui(5)
        self.game_grid = []
        for i in range(self.grid_height):
            self.game_grid.append([])
            for j in range(self.grid_width):
                self.game_grid[i].append(GridButton(self.game_frame, i, j, self.button_clicked))
                self.game_grid[i][j].grid(row=i, column=j)

    def button_clicked(self, x, y):
        print(x, y)

    def start_loading(self):
        self.connected = False
        self.cancelled = False
        if self.local_game:
            start_local_game()
        else:
            self.display_gui(3)
            self.communication.host(self.local_ip, self.port_value.get() + 1, get_connection, self.get_message)
            self.discovery.start_announcement("GOMOKU-{}-{}-{}-{}-{}-{}".format(self.version, self.local_ip, self.width_value.get(), self.height_value.get(), self.local_name, self.port_value.get()))
            _thread.start_new(self.wait_for_connection(), ())
        print(self.port_value.get())

    def get_connection(address):


    def get_message(message):
        pass

    def wait_for_connection(self):
        self.connection_from_other.listen(5)
        client, address = self.connection_from_other.accept()
        data = client.recv(1024).decode()
        actual_data = get_announced_data(data)
        self.connected = True
        self.communication.connect(actual_data[1], int(actual_data[5]) + 2)
        if not hasattr(self, "connection_to_other"):
            self.connection_to_other = socket.socket()
        self.connection_to_other.connect((actual_data[1], int(actual_data[5]) + 2))

    def start_local_game(self):
        self.display_gui(5)

    def setup_game(self):
        self.local_game = False
        self.display_gui(1)

    def setup_local_game(self):
        self.local_game = True
        self.display_gui(1)

    def display_connection_details(self, data):
        frame = tk.Frame(self.menu_frame)
        name_label = tk.Label(frame, text=data[4], font="Arial 14 bold")
        name_label.grid(row=0, column=0, sticky="we")
        ip_label = tk.Label(frame, text="IP: {}:{}".format(data[1], data[5]))
        ip_label.grid(row=1, column=0, sticky="we")
        size_label = tk.Label(frame, text="Width: {}, Height: {}".format(data[2], data[3]))
        size_label.grid(row=2, column=0, sticky="we")
        connect_button = ConnectButton(frame, self.connect_to, len(self.connection_options) - 1)
        connect_button.connect_button.grid(column=1, rowspan=3, row=0, sticky="ns")
        frame.grid(row=len(self.connection_options))
        self.connection_frames.append(frame)

    def connect_to(self, id):
        self.connected = True
        self.communication.connect(self.connection_options[id][1], int(self.connection_options[id][5]) + 1)
        self.communication.host(self.local_ip, int(self.connection_options[id][5]) + 2, self.get_connection, self.get_message)

    def get_announced_data(self, data):
        if not data.startswith("GOMOKU"):
            return None
        else:
            return data.split("-")[1:]

    def new_server_found(self, data):
        if len(self.connection_options) == 0:
            self.clear_frame()
        self.connection_options.append(self.get_announced_data(data))
        self.display_connection_details(self.get_announced_data(data))

    def server_timeout(self, id):
        del self.connection_options[id]
        self.connection_frames[id].destroy()
        del self.connection_frames[id]

    def __init__(self):
        self.version = "V1.1"
        self.window = tk.Tk()
        self.center_window()
        self.set_game_state()
        self.display_gui(0)
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.local_ip_numbers = [int(a) for a in self.local_ip.split(".")]
        self.local_name = socket.gethostname().replace("-", " ")

        self.discovery = Bidirectional_discovery()
        self.communication = Bidirectional_communication()

if __name__ == "__main__":
    game = GameWindow()
    game.run_window()