import sys
import socket
import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import re

from bidirectional_discovery import Bidirectional_discovery
from bidirectional_communication import Bidirectional_communication
#from rsa_encryption import RSA_encryption
from agreement import Agreement
from localization import Localization

DEFAULT_PORT = 65001

class ConnectButton():
    def __init__(self, frame, onclick, id, text):
        self.connect_button = tk.Button(frame, text=text, command=self.clicked)
        self.onclick = onclick
        self.id = id

    def clicked(self):
        self.onclick(self.id)

class GridCell():
    def __init__(self, frame, size, x, y, onclick):
        self.frame = tk.Frame(frame, width=size, height=size, borderwidth=0)
        self.frame.pack_propagate(0)
        self.cell = tk.Label(self.frame, text=" ", borderwidth=2, relief="groove")
        self.cell.pack(fill="both", expand=1)
        self.cell.bind("<Button-1>", self.clicked)
        self.onclick = onclick
        self.x = x
        self.y = y

    def clicked(self, event):
        self.onclick(self.x, self.y)

    def set(self, label):
        self.cell["text"]=label
        if label == " ":
            self.cell.config(bg="white")
        elif label == "X":
            self.cell.config(bg="#CFCFFF")
        else:
            self.cell.config(bg="#FFCFCF")

class GameWindow():
    def __init__(self):
        if len(sys.argv) > 1:
            self.locale = Localization(sys.argv[1])
        else:
            self.locale = Localization("en_US")
        self.version = "V1.2"
        self.window = tk.Tk()
        self.center_window()
        self.display_gui(0)
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.local_name = socket.gethostname().replace("-", " ")

        self.discovery = Bidirectional_discovery()
        self.communication = Bidirectional_communication()

    def center_window(self):
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = 1024
        height = 768
        x_position = int(screen_width / 2 - width / 2)
        y_position = int(screen_height / 2 - height / 2)
        self.window.geometry("{}x{}+{}+{}".format(width, height, x_position, y_position))

    def run_window(self):
        self.window.mainloop()

    def set_game_state(self, state=""):
        if state == "":
            self.window.title(self.locale.get("gomoku"))
        else:
            self.window.title("{} - {}".format(self.locale.get("gomoku"), state))

    def clear_frame(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.menu_frame = tk.Frame(self.window)
        self.menu_frame.place(relx=.5, rely=.5, anchor=tk.CENTER)

    def display_gui(self, state):
        self.clear_frame()
        self.set_game_state()

        button_font = font.Font(size="20")
        label_font = font.Font(size="24")

        if state == 0:
            local_multiplayer_button = tk.Button(self.menu_frame, text=self.locale.get("localMultiplayer"), font=button_font, command=self.setup_local_game)
            local_multiplayer_button.grid(row=0, columnspan=2, sticky=tk.NSEW)
            connect_button = tk.Button(self.menu_frame, text=self.locale.get("connect"), font=button_font, command=self.discover_hosts)
            connect_button.grid(row=1, column=0, sticky=tk.NSEW)
            create_button = tk.Button(self.menu_frame, text=self.locale.get("createGame"), font=button_font, command=self.setup_game)
            create_button.grid(row=1, column=1, sticky=tk.NSEW)

        if state == 1:
            width_label = tk.Label(self.menu_frame, text=self.locale.get("gridWidth:"), font=label_font)
            width_label.grid(row=0, column=0, sticky=tk.W)
            self.width_value = tk.IntVar(self.menu_frame, value=20)
            width_entry = tk.Entry(self.menu_frame, textvariable=self.width_value)
            width_entry.grid(row=0, column=1)
            height_label = tk.Label(self.menu_frame, text=self.locale.get("gridHeight:"), font=label_font)
            height_label.grid(row=1, column=0, sticky=tk.W)
            self.height_value = tk.IntVar(self.menu_frame, value=20)
            height_entry = tk.Entry(self.menu_frame, textvariable=self.height_value)
            height_entry.grid(row=1, column=1)
            if not self.local_game:
                separator = ttk.Separator(self.menu_frame)
                separator.grid(row=2, columnspan=2, sticky=tk.EW)
                port_label = tk.Label(self.menu_frame, text=self.locale.get("port:"), font=label_font)
                port_label.grid(row=3, column=0, sticky=tk.W)
                self.port_value = tk.IntVar(self.menu_frame, value=DEFAULT_PORT)
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
            separator2.grid(row=6, columnspan=2, sticky=tk.EW)
            go_button = tk.Button(self.menu_frame, text=self.locale.get("confirm"), command=self.start_loading)
            go_button.grid(row=7, columnspan=2)

        if state == 2:
            port_label = tk.Label(self.menu_frame, text=self.locale.get("port:"), font=label_font)
            port_label.grid(row=0, column=0, sticky=tk.W)
            self.port_value = tk.IntVar(self.menu_frame, value=DEFAULT_PORT)
            port_entry = tk.Entry(self.menu_frame, textvariable=self.port_value)
            port_entry.grid(row=0, column=1)
            go_button = tk.Button(self.menu_frame, text=self.locale.get("confirm"), command=self.discover_hosts)
            go_button.grid(row=1, columnspan=2)

        if state == 3:
            waiting_label = tk.Label(self.menu_frame, text=self.locale.get("waiting..."), font=label_font)
            waiting_label.grid(row=0)

        if state == 4:
            searching_label = tk.Label(self.menu_frame, text=self.locale.get("searching..."), font=label_font)
            searching_label.grid(row=0)

        if state == 5:
            self.game_frame = tk.Frame(self.menu_frame)
            self.game_frame.grid(row=0, column=0)
    
    def start_game(self):
        self.display_gui(5)
        self.game_grid = []
        self.window.update_idletasks()
        screen_width = self.window.winfo_width()
        screen_height = self.window.winfo_height()
        cell_size = min(screen_width / self.grid_width, screen_height / self.grid_height)
        for i in range(self.grid_height):
            self.game_grid.append([])
            for j in range(self.grid_width):
                self.game_grid[i].append(GridCell(self.game_frame, cell_size, i, j, self.button_clicked))
                self.game_grid[i][j].frame.grid(row=i, column=j)

    def start_local_game(self):
        self.next_player = "X"
        self.display_gui(5)
        self.start_game()

    def setup_game(self):
        self.local_game = False
        self.started = False
        self.display_gui(1)

    def setup_local_game(self):
        self.local_game = True
        self.display_gui(1)

    def display_connection_details(self, data):
        frame = tk.Frame(self.menu_frame)
        name_label = tk.Label(frame, text=data[4], font="Arial 14 bold")
        name_label.grid(row=0, column=0, sticky=tk.EW)
        ip_label = tk.Label(frame, text="{} {}:{}".format(self.locale.get("ip:"), data[1], data[5]))
        ip_label.grid(row=1, column=0, sticky=tk.EW)
        size_label = tk.Label(frame, text="{} {}, {} {}".format(self.locale.get("width:"), data[2], self.locale.get("height:"), data[3]))
        size_label.grid(row=2, column=0, sticky=tk.EW)
        connect_button = ConnectButton(frame, self.connect_to, len(self.connection_options) - 1, self.locale.get("connect"))
        connect_button.connect_button.grid(row=0, column=1, rowspan=3, sticky=tk.NS)
        frame.grid(row=len(self.connection_options))
        self.connection_frames.append(frame)

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
        if len(self.connection_options) == 0:
            self.display_gui(4)

    def start_loading(self):
        self.grid_width = self.width_value.get()
        self.grid_height = self.height_value.get()
        if self.local_game:
            self.start_local_game()
        else:
            self.display_gui(3)
            self.connected = False
            self.communication.host(self.local_ip, int(self.port_value.get()) + 1, self.get_connection, self.get_message)
            self.discovery.start_announcement("GOMOKU-{}-{}-{}-{}-{}-{}".format(self.version, self.local_ip, self.width_value.get(), self.height_value.get(), self.local_name, self.port_value.get()))

    def connect_to(self, id):
        self.connected = True
        self.started = False
        self.discovery.stop_discovery()
        self.grid_width = int(self.connection_options[id][2])
        self.grid_height = int(self.connection_options[id][3])
        self.communication.connect(self.connection_options[id][1], int(self.connection_options[id][5]) + 1)
        self.communication.send("GOMOKU-{}-{}".format(self.local_ip, int(self.connection_options[id][5]) + 2))
        self.communication.host(self.local_ip, int(self.connection_options[id][5]) + 2, self.get_connection, self.get_message)
        self.my_turn = False

    def discover_hosts(self):
        self.display_gui(4)
        self.local_game = False
        self.connection_options = []
        self.connection_frames = []
        self.discovery.start_discovery(self.new_server_found, self.server_timeout)

    def get_connection(self, address):
        pass

    def check_win(self):
        for row in self.game_grid:
            if re.search("O{5}", "".join([cell.cell["text"] for cell in row])) is not None:
                return "OH"
        for column in range(self.grid_width):
            if re.search("O{5}", "".join([row[column].cell["text"] for row in self.game_grid])) is not None:
                return "OV"
        for x in range(self.grid_height - 4):
            for y in range(self.grid_width - 4):
                if re.search("O{5}", "".join([self.game_grid[x + i][y + i].cell["text"] for i in range(5)])):
                    return "ODL"
        for x in range(4, self.grid_height):
            for y in range(self.grid_width - 4):
                if re.search("O{5}", "".join([self.game_grid[x - i][y + i].cell["text"] for i in range(5)])):
                    return "ODR"
        return None

    def check_x_win(self):
        for row in self.game_grid:
            if re.search("X{5}", "".join([cell.cell["text"] for cell in row])) is not None:
                return "XH"
        for column in range(self.grid_width):
            if re.search("X{5}", "".join([row[column].cell["text"] for row in self.game_grid])) is not None:
                return "XV"
        for x in range(self.grid_height - 4):
            for y in range(self.grid_width - 4):
                if re.search("X{5}", "".join([self.game_grid[x + i][y + i].cell["text"] for i in range(5)])):
                    return "XDL"
        for x in range(4, self.grid_height):
            for y in range(self.grid_width - 4):
                if re.search("X{5}", "".join([self.game_grid[x - i][y + i].cell["text"] for i in range(5)])):
                    return "XDR"
        return None

    def get_message(self, message):
        data = self.get_announced_data(message)
        if data is None:
            return
        if not self.connected:
            self.connected = True
            self.discovery.stop_discovery()
            self.communication.connect(data[0], int(data[1]))
            self.my_turn = True
        if not self.started:
            self.started = True
            self.communication.send("GOMOKU-START")

        if data[0] == "START":
            self.start_game()

        elif data[0] == "STEP":
            self.game_grid[int(data[1])][int(data[2])].set("O")
            self.my_turn = True
            self.set_game_state(self.locale.get("yourTurn"))
            if self.check_win() is not None:
                self.communication.send("GOMOKU-WIN")
                self.new_game_agreement = Agreement(self.new_game)
                new_game = messagebox.askyesno(self.locale.get("wouldYouLikeToPlayAgain?"), self.locale.get("yourOpponentWon"))
                self.new_game_agreement.local_answer(new_game)
                if new_game:
                    self.communication.send("GOMOKU-RESTART-OK")
                else:
                    self.communication.send("GOMOKU-RESTART-NO")

        elif data[0] == "WIN":
            new_game = messagebox.askyesno(self.locale.get("wouldYouLikeToPlayAgain?"), self.locale.get("youWon"))
            self.new_game_agreement = Agreement(self.new_game)
            self.new_game_agreement.local_answer(new_game)
            if new_game:
                self.communication.send("GOMOKU-RESTART-OK")
            else:
                self.communication.send("GOMOKU-RESTART-NO")

        elif data[0] == "RESTART":
            if data[1] == "OK":
                self.new_game_agreement.remote_answer(True)
            else:
                self.new_game_agreement.remote_answer(False)

    def new_game(self, agreed):
        if agreed:
            for row in self.game_grid:
                for cell in row:
                    cell.set(" ")
        else:
            if not self.local_game:
                self.communication.disconnect()
            self.display_gui(0)

    def button_clicked(self, x, y):
        if self.game_grid[x][y].cell["text"] == " ":
            if self.local_game:
                self.game_grid[x][y].set(self.next_player)
                if self.next_player == "X":
                    self.next_player = "O"
                else:
                    self.next_player = "X"
                self.set_game_state("{}{}".format(self.next_player, self.locale.get("'sTurn")))
                if self.check_win():
                    new_game = messagebox.askyesno(self.locale.get("wouldYouLikeToPlayAgain?"), "O {}".format(self.locale.get("won")))
                    self.new_game(new_game)
                elif self.check_x_win():
                    new_game = messagebox.askyesno(self.locale.get("wouldYouLikeToPlayAgain?"), "X {}".format(self.locale.get("won")))
                    self.new_game(new_game)
            elif self.my_turn:
                self.communication.send("GOMOKU-STEP-{}-{}".format(x, y))
                self.game_grid[x][y].set("X")
                self.my_turn = False
                self.set_game_state(self.locale.get("opponent'sTurn"))
                
if __name__ == "__main__":
    game = GameWindow()
    game.run_window()