from tkinter import *
from tkinter import ttk
from datetime import datetime
import os
import subprocess


class FileExplorerWindow(Tk):

    def __init__(self, title='File Explorer', size='640x480', theme_name='vista', directory=os.getcwd()):
        super().__init__()
        # This variable is to keep track of the directory we're currently browsing
        self.current_dir = directory

        # These stacks are used to keep track of back/forward paths:
        self.back_stack = []
        self.forward_stack = []

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
        self.file_menu.add_command(label='Refresh', command=self.refresh_browser)
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
        self.back_button = ttk.Button(self.upper_frame,
                                      text='<<',
                                      state=DISABLED,
                                      command=self.back_button_clicked)
        self.back_button.grid(row=0, column=0, sticky=W)
        # This button forwards you to where you used the Back button
        self.forward_button = ttk.Button(self.upper_frame,
                                         text='>>',
                                         state=DISABLED,
                                         command=self.forward_button_clicked)
        self.forward_button.grid(row=0, column=1)
        # This button takes you up 1 step in the directory tree
        self.up_button = ttk.Button(self.upper_frame, text='^', command=self.up_button_clicked)
        self.up_button.grid(row=0, column=2)
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
        self.search_bar.bind('<Return>', self.search)
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
        # We'll need 2 scrollbars to scroll the list vertically and horizontally
        self.browser_vertical_scrollbar = ttk.Scrollbar(self.main_frame, orient=VERTICAL)
        self.browser_vertical_scrollbar.grid(row=0, column=1, sticky=N+S+E)
        self.browser_horizontal_scrollbar = ttk.Scrollbar(self.main_frame, orient=HORIZONTAL)
        self.browser_horizontal_scrollbar.grid(row=1, column=0, columnspan=2, sticky=S+E+W)
        self.browser_list = ttk.Treeview(self.main_frame,
                                         selectmode=EXTENDED,
                                         yscrollcommand=self.browser_vertical_scrollbar.set,
                                         xscrollcommand=self.browser_horizontal_scrollbar.set)
        self.browser_list.grid(row=0, column=0, sticky=N+S+E+W)
        self.browser_vertical_scrollbar.config(command=self.browser_list.yview)
        self.browser_horizontal_scrollbar.config(command=self.browser_list.xview)
        # Define columns in browser: Name, Date modified, Type, Size
        self.browser_list['columns'] = ('Name', 'Date modified', 'Type', 'Size')
        # Format columns:
        self.browser_list.column('#0', width=0, minwidth=0, stretch=NO)
        for column in self.browser_list['columns']:
            self.browser_list.column(column, minwidth=40, stretch=NO)
            self.browser_list.heading(column, text=column)
        self.refresh_browser()
        # Bindings:
        self.browser_list.tag_bind('file', '<Double-1>', callback=self.execute_file)
        self.browser_list.tag_bind('file', '<Return>', callback=self.execute_file)
        self.browser_list.tag_bind('folder', '<Double-1>', callback=self.open_folder)
        self.browser_list.tag_bind('folder', '<Return>', callback=self.open_folder)
        # The browser view is the main component => Put more weight to it.
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        # TODO: add functionality to the browser

        self.mainloop()
    # __init__ ends here

    def refresh_browser(self, event=None):
        # This function will refresh the browser and list all the items inside the current working directory
        # First we clear the current list
        for item in self.browser_list.get_children():
            self.browser_list.delete(item)
        # Then we change to the current working directory:
        os.chdir(self.current_dir)
        # ... and rewrite it to the directory bar:
        self.dir_bar.delete(0, END)
        self.dir_bar.insert(0, self.current_dir)
        # Stats viewed for each item include: Name, Date modified, Type, Size
        count = 0
        for item in sorted(os.listdir(self.current_dir)):
            # Get date. It'll be in timestamp format
            date_modified = os.stat(item).st_mtime
            # We have to change obtained date to human-readable format
            date_modified = datetime.fromtimestamp(date_modified)
            # Get the name of the item
            name = os.path.split(item)[1]
            # The type of the item is the file extension, or nothing if it's a folder
            file_type = os.path.splitext(item)[1]
            if not os.path.isfile(item):
                file_type = 'Folder'
            if file_type == '':
                file_type = 'File'
            # Get the size of the item. It'll be in bytes
            size = os.stat(item).st_size
            units = ('KB', 'MB', 'GB', 'TB')    # Hopefully no one actually has an item that exceeds 1024 TB
            size_unit = 'Bytes'
            for i in range(len(units)):
                if size >= 1024:
                    size = round(size/1024)
                    size_unit = units[i]
                else:
                    break
            self.browser_list.insert(parent='',
                                     iid=count,
                                     tag='file' if os.path.isfile(item) else 'folder',
                                     index=END if os.path.isfile(item) else 0,  # Folders => head, files => rear
                                     values=(name, date_modified, file_type, str(size) + ' ' + size_unit))
            count += 1
        # Reset search bar, since the current directory has changed
        self.search_bar.delete(0, END)
        self.style.configure('Search.TEntry', foreground='grey')
        self.search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])

    def execute_file(self, event=None):
        for file in self.browser_list.selection():
            file_name = self.browser_list.item(file, 'values')[0]
            subprocess.run(file_name, shell=True)

    def open_folder(self, event=None):
        # Add the current directory to back stack
        self.back_stack.append(self.current_dir)
        self.back_button.config(state=NORMAL)   # Also enable the back button
        # Clean forward stack and disable forward button
        self.forward_stack.clear()
        self.forward_button.config(state=DISABLED)
        # Get new directory from the select folder name
        selected_folder = self.browser_list.selection()[0]
        folder_name = self.browser_list.item(selected_folder, 'values')[0]
        self.current_dir = os.path.join(self.current_dir, folder_name)
        self.refresh_browser()

    def up_button_clicked(self, event=None):
        # Add the current directory to back stack
        self.back_stack.append(self.current_dir)
        self.back_button.config(state=NORMAL)  # Also enable the back button
        # Clean forward stack and disable forward button
        self.forward_stack.clear()
        self.forward_button.config(state=DISABLED)
        # Up one node in directory tree
        self.current_dir = os.path.split(self.current_dir)[0]
        self.refresh_browser()

    def back_button_clicked(self, event=None):
        # We need to make sure that the back stack is not empty
        if self.back_stack:
            # Add the current directory to forward stack
            self.forward_stack.append(self.current_dir)
            self.forward_button.config(state=NORMAL)  # Also enable the forward button
            # Get the latest path from the stack
            self.current_dir = self.back_stack.pop()
            if not self.back_stack:     # Also disable the back button if back stack is empty
                self.back_button.config(state=DISABLED)
            self.refresh_browser()

    def forward_button_clicked(self, event=None):
        # We need to make sure that the forward stack is not empty
        if self.forward_stack:
            # Add the current directory to back stack
            self.back_stack.append(self.current_dir)
            self.back_button.config(state=NORMAL)   # Also enable the back button
            # Get the latest path from forward stack
            self.current_dir = self.forward_stack.pop()
            if not self.forward_stack:      # Also disable forward button if forward stack is empty
                self.forward_button.config(state=DISABLED)
            self.refresh_browser()

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

    def search(self, event=None):
        # When you press enter in the search bar, the browser will filter out the items whose name contains
        # the searched key word
        if self.search_bar.get() == '':
            # If there's nothing in the search bar, then simply refresh the browser
            self.refresh_browser()
            self.browser_list.focus_set()
        else:
            temp = self.search_bar.get()
            self.refresh_browser()
            self.search_bar.delete(0, END)
            self.search_bar.insert(0, temp)
            for item in self.browser_list.get_children():
                if self.search_bar.get().lower() not in self.browser_list.item(item, 'values')[0].lower():
                    self.browser_list.delete(item)
            self.dir_bar.delete(0, END)
            self.dir_bar.insert(0,
                                f'Search result for "{self.search_bar.get()}" in {os.path.split(self.current_dir)[1]}')
            self.browser_list.focus_set()
