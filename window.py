from tkinter import *
from tkinter import ttk
import os


class FileExplorerWindow(Tk):

    def __init__(self, title='File Explorer', size='640x480', theme_name='vista', directory=os.getcwd()):
        super().__init__()
        self.current_dir = directory

        # root window
        self.title(title)
        self.geometry(size)
        self.style = ttk.Style(self)
        self.style.theme_use(theme_name)

        # Menu: including menus
        menu = Menu(self)
        self.config(menu=menu)
        file_menu = Menu(menu)
        menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Open new window', command=lambda: FileExplorerWindow())
        file_menu.add_command(label='Settings', command=None)   # TODO: write a function that opens a settings window
        file_menu.add_separator()
        file_menu.add_command(label='Help', command=None)    # TODO: write a function that displays a help menu
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)

        edit_menu = Menu(menu)
        menu.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='New folder', command=None) # TODO: give this functionality
        edit_menu.add_command(label='Select all', command=None)  # TODO: give this functionality
        edit_menu.add_command(label='Select none', command=None)  # TODO: give this functionality
        edit_menu.add_command(label='Invert selection', command=None)  # TODO: give this functionality
        edit_menu.add_separator()
        edit_menu.add_command(label='Open', command=None)   # TODO: give this functionality
        edit_menu.add_command(label='Rename', command=None) # TODO: give this functionality
        edit_menu.add_command(label='Delete', command=None) # TODO: give this functionality
        edit_menu.add_separator()
        edit_menu.add_command(label='Copy', command=None)   # TODO: give this functionality
        edit_menu.add_command(label='Copy path', command=None)  # TODO: give this functionality
        edit_menu.add_command(label='Cut', command=None)    # TODO: give this functionality
        edit_menu.add_command(label='Paste', command=None)  # TODO: give this functionality


        # Upper frame: Including menus and toolbar
        upper_frame = ttk.Frame(self, relief=FLAT, padding=2)
        upper_frame.grid(row=0, column=0, columnspan=2, sticky=E+W)
        back_button = ttk.Button(upper_frame, text='<<')
        back_button.grid(row=0, column=0, sticky=W)
        forward_button = ttk.Button(upper_frame, text='>>')
        forward_button.grid(row=0, column=1)
        up_button = ttk.Button(upper_frame, text='^')
        up_button.grid(row=0, column=2)
        # TODO: give the above buttons functionality
        dir_bar = ttk.Combobox(upper_frame, text=self.current_dir)
        dir_bar.grid(row=0, column=3, sticky=E+W)
        dir_bar.insert(0, self.current_dir)
        # TODO: give the above combobox functionality
        upper_frame.columnconfigure(3, weight=1)
        self.style.configure('Search.TEntry', background='white', foreground='grey')
        search_bar = ttk.Entry(upper_frame, style='Search.TEntry')
        search_bar.grid(row=0, column=4, sticky=E)
        search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
        search_bar.bind('<FocusIn>', lambda event: self.search_bar_focus_in(search_bar, event))
        search_bar.bind('<FocusOut>', lambda event: self.search_bar_focus_out(search_bar, event))
        # TODO: give search bar an actual search function

        # Left frame: Including Quick access and My computer
        left_frame = ttk.Frame(self, relief=FLAT, padding=2)
        left_frame.grid(row=1, column=0, sticky=N+S)
        quick_access = ttk.LabelFrame(left_frame, text='Quick access')
        quick_access.pack(side=TOP, fill=Y, expand=True)
        quick_access_scrollbar = ttk.Scrollbar(quick_access, orient=VERTICAL)
        quick_access_scrollbar.pack(side=RIGHT, fill=Y, expand=True)
        quick_access_list = ttk.Treeview(quick_access, selectmode=EXTENDED, yscrollcommand=quick_access_scrollbar.set)
        quick_access_list.pack(side=LEFT, fill=Y, expand=True)
        quick_access_scrollbar.config(command=quick_access_list.yview)
        # TODO: add stuff to quick access
        my_computer = ttk.LabelFrame(left_frame, text='This PC')
        my_computer.pack(side=BOTTOM, fill=Y, expand=True)
        my_computer_scrollbar = ttk.Scrollbar(my_computer, orient=VERTICAL)
        my_computer_scrollbar.pack(side=RIGHT, fill=Y, expand=TRUE)
        my_computer_list = ttk.Treeview(my_computer, selectmode=EXTENDED, yscrollcommand=my_computer_scrollbar.set)
        my_computer_list.pack(fill=Y, expand=True)
        my_computer_scrollbar.config(command=my_computer_list.yview)
        # TODO: add stuff to my computer

        # Main frame. The list of files and folders will be on this frame
        main_frame = ttk.Frame(self, relief=FLAT, padding=2)
        main_frame.grid(row=1, column=1, sticky=N+S+E+W)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        # list of files and folders inside the current directory
        # We'll need a scrollbar to scroll the list vertically
        browser_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL)
        browser_scrollbar.grid(row=0, column=1, sticky=N+S+E)
        browser_list = ttk.Treeview(main_frame, selectmode=EXTENDED, yscrollcommand=browser_scrollbar.set)
        browser_list.grid(row=0, column=0, sticky=N+S+E+W)
        browser_scrollbar.config(command=browser_list.yview)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        # TODO: add functionality to the browser

        self.mainloop()
    # __init__ ends here

    def search_bar_focus_in(self, search_bar, event=None):
        if search_bar.get() == 'Search ' + os.path.split(self.current_dir)[1]:
            search_bar.delete(0, END)
            self.style.configure('Search.TEntry', foreground='black')
        else:
            search_bar.select_range(0, END)

    def search_bar_focus_out(self, search_bar, event=None):
        if search_bar.get() == '':
            search_bar.delete(0, END)
            self.style.configure('Search.TEntry', foreground='grey')
            search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
