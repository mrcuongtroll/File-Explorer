from tkinter import *
from tkinter import ttk
import os


class FileExplorerWindow(Tk):

    def __init__(self, title='File Explorer', size='640x480', theme_name='vista', directory=os.getcwd()):
        super().__init__()
        # This variable is to keep track of the directory we're currently browsing
        self.current_dir = directory

        # root window.
        self.title(title)
        self.geometry(size)
        # We need a ttk.Style object to manage the style of widgets
        self.style = ttk.Style(self)
        self.style.theme_use(theme_name)

        # Menu: including menus
        self.menu = Menu(self)
        self.config(menu=self.menu)
        # File menu contains basic options for an app like settings, help, exit...
        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open new window', command=lambda: FileExplorerWindow())
        self.file_menu.add_command(label='Settings', command=None)   # TODO: a function that opens a settings window
        self.file_menu.add_separator()  # Separator can be use to separate groups of options
        self.file_menu.add_command(label='Help', command=None)    # TODO: a function that displays a help menu
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.destroy)
        # Edit menu contains options to work with, and/or manipulate files and folders
        self.edit_menu = Menu(self.menu)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='New folder', command=None) # TODO: give this functionality
        self.edit_menu.add_command(label='Select all', command=None)  # TODO: give this functionality
        self.edit_menu.add_command(label='Select none', command=None)  # TODO: give this functionality
        self.edit_menu.add_command(label='Invert selection', command=None)  # TODO: give this functionality
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Open', command=None)   # TODO: give this functionality
        self.edit_menu.add_command(label='Rename', command=None) # TODO: give this functionality
        self.edit_menu.add_command(label='Delete', command=None) # TODO: give this functionality
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Copy', command=None)   # TODO: give this functionality
        self.edit_menu.add_command(label='Copy path', command=None)  # TODO: give this functionality
        self.edit_menu.add_command(label='Cut', command=None)    # TODO: give this functionality
        self.edit_menu.add_command(label='Paste', command=None)  # TODO: give this functionality

        # Upper frame: a.k.a the toolbar
        self.upper_frame = ttk.Frame(self, relief=FLAT, padding=2)
        self.upper_frame.grid(row=0, column=0, columnspan=2, sticky=E+W)
        # This button takes you back to your previous browsing directory
        self.back_button = ttk.Button(self.upper_frame, text='<<')
        self.back_button.grid(row=0, column=0, sticky=W)
        # This button forwards you to where you used the Back button
        self.forward_button = ttk.Button(self.upper_frame, text='>>')
        self.forward_button.grid(row=0, column=1)
        # This button takes you up 1 step in the directory tree
        self.up_button = ttk.Button(self.upper_frame, text='^')
        self.up_button.grid(row=0, column=2)
        # TODO: give the above buttons functionality
        # Directory bar: You can type the path you want to browse directly
        # You can also choose from frequently browsed paths in the drop-down menu
        self.dir_bar = ttk.Combobox(self.upper_frame, text=self.current_dir)
        self.dir_bar.grid(row=0, column=3, sticky=E+W)
        self.dir_bar.insert(0, self.current_dir)
        self.upper_frame.columnconfigure(3, weight=1)
        # TODO: give dir_bar functionality
        # Search bar: You can search for a file name within the directory you're currently browsing
        self.style.configure('Search.TEntry', background='white', foreground='grey')
        self.search_bar = ttk.Entry(self.upper_frame, style='Search.TEntry')
        self.search_bar.grid(row=0, column=4, sticky=E)
        self.search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
        self.search_bar.bind('<FocusIn>', self.search_bar_focus_in)
        self.search_bar.bind('<FocusOut>', self.search_bar_focus_out)
        # TODO: give search bar an actual search function

        # Left frame: Including Quick access and My computer
        self.left_frame = ttk.Frame(self, relief=FLAT, padding=2)
        self.left_frame.grid(row=1, column=0, sticky=N+S)
        # Quick access: lets you quickly access special directories like Desktop, Documents, Downloads...
        # Future extension: let the users pin favourite directories here
        self.quick_access = ttk.LabelFrame(self.left_frame, text='Quick access')
        self.quick_access.pack(side=TOP, fill=Y, expand=True)
        self.quick_access_scrollbar = ttk.Scrollbar(self.quick_access, orient=VERTICAL)
        self.quick_access_scrollbar.pack(side=RIGHT, fill=Y, expand=True)
        self.quick_access_list = ttk.Treeview(self.quick_access,
                                              selectmode=EXTENDED,
                                              yscrollcommand=self.quick_access_scrollbar.set)
        self.quick_access_list.pack(side=LEFT, fill=Y, expand=True)
        self.quick_access_scrollbar.config(command=self.quick_access_list.yview)
        # TODO: add stuff to quick access
        # My computer: lets you quickly access the disk drives (C, D, E...)
        self.my_computer = ttk.LabelFrame(self.left_frame, text='This PC')
        self.my_computer.pack(side=BOTTOM, fill=Y, expand=True)
        self.my_computer_scrollbar = ttk.Scrollbar(self.my_computer, orient=VERTICAL)
        self.my_computer_scrollbar.pack(side=RIGHT, fill=Y, expand=TRUE)
        self.my_computer_list = ttk.Treeview(self.my_computer,
                                             selectmode=EXTENDED,
                                             yscrollcommand=self.my_computer_scrollbar.set)
        self.my_computer_list.pack(fill=Y, expand=True)
        self.my_computer_scrollbar.config(command=self.my_computer_list.yview)
        # TODO: add stuff to my computer

        # Main frame. The list of files and folders will be on this frame
        self.main_frame = ttk.Frame(self, relief=FLAT, padding=2)
        self.main_frame.grid(row=1, column=1, sticky=N+S+E+W)
        # This frame should be the largest. Thus the higher weight compared to other frames
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        # list of files and folders inside the current directory
        # We'll need a scrollbar to scroll the list vertically
        self.browser_scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL)
        self.browser_scrollbar.grid(row=0, column=1, sticky=N+S+E)
        self.browser_list = ttk.Treeview(self.main_frame,
                                         selectmode=EXTENDED,
                                         yscrollcommand=self.browser_scrollbar.set)
        self.browser_list.grid(row=0, column=0, sticky=N+S+E+W)
        self.browser_scrollbar.config(command=self.browser_list.yview)
        # The browser view is the main component => Put more weight to it.
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        # TODO: add functionality to the browser

        self.mainloop()
    # __init__ ends here

    def browser_refresh(self, event=None):
        # This function will refresh the browser and list all the items inside the current working directory
        for item in os.listdir(self.current_dir):
            pass

    def search_bar_focus_in(self, event=None):
        # This function will remove the greyed out "Search..." indicator and let the user type in the search key
        if self.search_bar.get() == 'Search ' + os.path.split(self.current_dir)[1]:
            self.search_bar.delete(0, END)
            self.style.configure('Search.TEntry', foreground='black')
        else:
            self.search_bar.select_range(0, END)

    def search_bar_focus_out(self, event=None):
        # This function will leave a greyed out "Search <current directory>" to tell the user that
        # this is the search bar when not focused in
        if self.search_bar.get() == '':
            self.search_bar.delete(0, END)
            self.style.configure('Search.TEntry', foreground='grey')
            self.search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
