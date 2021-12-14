from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import os
import subprocess
import sys
import shutil
import win32api
import win32con
import pywintypes
import utils


# Classes
class _FileExplorerWindow(Tk):

    def __init__(self, title='File Explorer', size='640x480', theme='vista', directory=os.getcwd(),
                 data_path=None):
        super().__init__()
        # This variable is to keep track of the directory we're currently browsing
        self.current_dir = directory
        if not data_path:
            self.data_path = os.path.join(os.getcwd(), 'data/')
        else:
            self.data_path = data_path

        # These stacks are used to keep track of back/forward paths:
        self.back_stack = []
        self.forward_stack = []

        # This list is to keep track of recent directories
        self.recent_dirs_list = []
        try:
            with open(os.path.join(self.data_path, 'dirs_list.bin'), 'rb') as f:
                directories = f.read().decode('utf-8')
                self.recent_dirs_list = directories.split('\n')
        except FileNotFoundError:
            try:
                os.makedirs(self.data_path)
            except FileExistsError:
                pass

        # This list is to keep track of directories pinned to quick access
        self.pinned_list = []

        # This variable tells the program if the data in clipboard is for copy or cut (should be 'copy', 'cut')
        self.clipboard_type = StringVar()

        # root window.
        self.title(title)
        self.geometry(size)
        # We need a ttk.Style object to manage the style of widgets
        self.style = ttk.Style(self)
        self.theme = theme
        self.style.theme_use(self.theme)

        # Menu: including menus
        self.menu = Menu(self)
        self.config(menu=self.menu)
        # File menu contains basic options for an app like settings, help, exit...
        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open', command=None, state=DISABLED)
        self.file_menu.add_separator()  # Separator can be use to separate groups of options
        self.file_menu.add_command(label='Open new window',
                                   command=lambda: _FileExplorerWindow(data_path=self.data_path))
        self.file_menu.add_command(label='Refresh', command=self.refresh_browser)
        self.file_menu.add_command(label='New folder', command=self.new_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.destroy)
        # Edit menu contains options to work with, and/or manipulate files and folders
        self.edit_menu = Menu(self.menu)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Pin to quick access', state=DISABLED, command=self.pin_dir)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Select all', command=self.select_all)
        self.edit_menu.add_command(label='Select none', command=self.select_none)
        self.edit_menu.add_command(label='Invert selection', command=self.invert_selection)
        self.edit_menu.add_separator()

        self.edit_menu.add_command(label='Rename', state=DISABLED, command=self.browser_item_rename)
        self.edit_menu.add_command(label='Delete', state=DISABLED, command=self.browser_item_delete)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Copy', state=DISABLED, command=lambda: self.clipboard_item('copy'))
        self.edit_menu.add_command(label='Cut', state=DISABLED, command=lambda: self.clipboard_item('cut'))
        self.edit_menu.add_command(label='Paste', state=DISABLED, command=self.paste_item)
        # The Paste option should only be enabled whenever there is something in the clipboard
        self.clipboard_type.trace_add('write', callback=lambda a1, a2, a3: self.trace_clipboard())
        # I dunno why the callback requires 3 arguments nor what are they though.

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
        self.dir_bar = ttk.Combobox(self.upper_frame, text=self.current_dir, values=self.recent_dirs_list)
        self.dir_bar.grid(row=0, column=3, sticky=E+W)
        self.dir_bar.insert(0, self.current_dir)
        self.upper_frame.columnconfigure(3, weight=1)
        self.dir_bar.bind('<FocusIn>', self.dir_bar_focus_in)
        self.dir_bar.bind('<FocusOut>', self.dir_bar_focus_out)
        self.dir_bar.bind('<Return>', self.dir_browse)
        self.dir_bar.bind('<<ComboboxSelected>>', self.dir_select)
        self.dir_bar.bind('<Destroy>', self.dir_bar_destroy)
        # Search bar: You can search for a file name within the directory you're currently browsing
        self.style.configure('Search.TEntry', background='white', foreground='grey')
        self.search_bar = ttk.Entry(self.upper_frame, style='Search.TEntry')
        self.search_bar.grid(row=0, column=4, sticky=E)
        self.search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
        self.search_bar.bind('<FocusIn>', self.search_bar_focus_in)
        self.search_bar.bind('<FocusOut>', self.search_bar_focus_out)
        self.search_bar.bind('<Return>', self.search)

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
                                              selectmode=BROWSE,
                                              yscrollcommand=self.quick_access_scrollbar.set,
                                              show='')
        self.quick_access_list.pack(side=LEFT, fill=Y, expand=True)
        self.quick_access_scrollbar.config(command=self.quick_access_list.yview)
        self.quick_access_list['columns'] = 'Name'
        self.quick_access_list.column('#0', width=0, minwidth=0, stretch=NO)
        self.quick_access_list.column('Name')
        self.quick_access_list.tag_bind('pinned', '<Double-1>', self.open_pinned_dir)
        self.quick_access_list.tag_bind('pinned', '<Return>', self.open_pinned_dir)
        # My computer: lets you quickly access the disk drives (C, D, E...)
        self.my_computer = ttk.LabelFrame(self.left_frame, text='This PC')
        self.my_computer.pack(side=BOTTOM, fill=Y, expand=True)
        self.my_computer_scrollbar = ttk.Scrollbar(self.my_computer, orient=VERTICAL)
        self.my_computer_scrollbar.pack(side=RIGHT, fill=Y)
        self.my_computer_list = ttk.Treeview(self.my_computer,
                                             selectmode=BROWSE,
                                             yscrollcommand=self.my_computer_scrollbar.set,
                                             show='')
        self.my_computer_list.pack(fill=Y, expand=True)
        self.my_computer_scrollbar.config(command=self.my_computer_list.yview)
        self.my_computer_list['columns'] = 'Name'
        self.my_computer_list.column('#0', width=0, minwidth=0, stretch=NO)
        self.my_computer_list.column('Name')
        # on windows
        # Get the fixed drives
        # wmic logicaldisk get name,description
        if 'win' in sys.platform:
            drive_list = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
            drive_list, err = drive_list.communicate()
            drive_list = ''.join([chr(b) for b in drive_list]).replace('\r', '').strip().split('\n')[1:]
            for i in range(len(drive_list)):
                self.my_computer_list.insert(parent='',
                                             iid=i,
                                             tag='drive',
                                             index=END,
                                             values=(drive_list[i].strip(),))
        elif 'linux' in sys.platform:
            # To be updated (perhaps in the future... Or maybe not)
            pass
        elif 'macos' in sys.platform:
            # To be updated (perhaps in the future... Or maybe not)
            pass
        self.my_computer_list.tag_bind('drive', '<Double-1>', callback=self.open_drive)
        self.my_computer_list.tag_bind('drive', '<Return>', callback=self.open_drive)

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
        # Bindings:
        self.browser_list.tag_bind('file', '<Double-1>', callback=self.execute_file)
        self.browser_list.tag_bind('file', '<Return>', callback=self.execute_file)
        self.browser_list.tag_bind('file', '<<TreeviewSelect>>',
                                   callback=lambda event: self.browser_items_select(tag='file'))
        self.browser_list.tag_bind('folder', '<Double-1>', callback=self.open_folder)
        self.browser_list.tag_bind('folder', '<Return>', callback=self.open_folder)
        self.browser_list.tag_bind('folder', '<<TreeviewSelect>>',
                                   callback=lambda event: self.browser_items_select(tag='folder'))
        self.browser_list.bind('<BackSpace>', self.backspace_pressed)
        self.browser_list.bind('<Control-a>', self.select_all)
        self.browser_list.bind('<Delete>', self.browser_item_delete)
        self.browser_list.bind('<Control-c>', lambda event: self.clipboard_item('copy'))
        self.browser_list.bind('<Control-x>', lambda event: self.clipboard_item('cut'))
        self.browser_list.bind('<Control-v>', self.paste_item)
        # The browser view is the main component => Put more weight to it.
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        # TODO: add right click menu

        self.refresh_browser()
        self.mainloop()
    # __init__ ends here

    # Functions related to the main browser ()
    # An important function that is used very often
    def refresh_browser(self, event=None):
        # This function will refresh the browser and list all the items inside the current working directory
        # First we clear the current list
        for item in self.browser_list.get_children():
            self.browser_list.delete(item)
        # Then we change to the current working directory:
        os.chdir(self.current_dir)
        # ... and rewrite it to the directory bar:
        self.dir_bar.delete(0, END)
        current_dir = self.current_dir.split('\\')
        current_dir = ' > '.join(current_dir)
        self.dir_bar.insert(0, current_dir)
        # Stats viewed for each item include: Name, Date modified, Type, Size
        count = 0
        for item in sorted(os.listdir(self.current_dir)):
            # We'll ignore hidden files and system-protected files
            try:
                attribute = win32api.GetFileAttributes(os.path.join(self.current_dir, item))
                if attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM):
                    continue
            except pywintypes.error:
                continue
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
                                     values=(name, date_modified, file_type,
                                             str(size) + ' ' + size_unit if os.path.isfile(item) else '')
                                     )
            count += 1
        # Reset search bar, since the current directory has changed
        self.search_bar.delete(0, END)
        self.style.configure('Search.TEntry', foreground='grey')
        self.search_bar.insert(0, 'Search ' + os.path.split(self.current_dir)[1])
        # Reset menus, since all rows in the browser are now de-selected
        self.reset_menus()
        # Put the path in the head of recent directories list
        self.add_recent_dir()
        # Refresh quick access occasionally
        self.refresh_quick_access()
        # Remove focus from my computer
        for sel in self.my_computer_list.selection():
            self.my_computer_list.selection_remove(sel)
    # refresh_browser ends here

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
        self.current_dir = os.path.join(self.current_dir, folder_name).replace('/', '\\')
        self.title(folder_name)
        self.refresh_browser()

    def browser_items_select(self, tag, event=None):
        # This function is called when the selection that involves some items is changed in the browser
        if not self.browser_list.selection():
            # If nothing is selected on the browser, then deactivate some menu options
            self.reset_menus()
        else:
            # Enable menu options based on the type of the selected items (files/folders)
            if len(self.browser_list.selection()) == 1:
                # These options should only be applied to one item at a time
                if tag == 'file':
                    self.file_menu.entryconfig('Open', state=NORMAL, command=self.execute_file)
                    self.edit_menu.entryconfig('Pin to quick access', state=DISABLED)
                elif tag == 'folder':
                    self.file_menu.entryconfig('Open', state=NORMAL, command=self.open_folder)
                    self.edit_menu.entryconfig('Pin to quick access', state=NORMAL)
                self.edit_menu.entryconfig('Rename', state=NORMAL)
            self.edit_menu.entryconfig('Delete', state=NORMAL)
            self.edit_menu.entryconfig('Copy', state=NORMAL)
            self.edit_menu.entryconfig('Cut', state=NORMAL)

    def browser_item_delete(self, event=None):
        if len(self.browser_list.selection()) == 1:
            item = self.browser_list.selection()[0]
            if self.browser_list.item(item, 'tags')[0] == 'file':
                file_name = self.browser_list.item(item, 'values')[0]
                response = messagebox.askyesno(title='Delete File',
                                               message=f'Are you sure you want to permanently delete {file_name}?')
                if response:
                    os.remove(os.path.join(self.current_dir, file_name))
            elif self.browser_list.item(item, 'tags')[0] == 'folder':
                folder_name = self.browser_list.item(item, 'values')[0]
                response = messagebox.askyesno(title='Delete Folder',
                                               message=f'Are you sure you want to permanently delete {folder_name}?')
                if response:
                    # We use shutil here because os library can only remove empty folders for safety reasons
                    shutil.rmtree(os.path.join(self.current_dir, folder_name))
                    self.unpin_dir(os.path.join(self.current_dir, folder_name))
        else:
            response = messagebox.askyesno(title='Delete multiple items',
                                           message=('Are you sure you want to permanently delete these '
                                                    f'{len(self.browser_list.selection())} items?'))
            if response:
                for item in self.browser_list.selection():
                    if self.browser_list.item(item, 'tags')[0] == 'file':
                        file_name = self.browser_list.item(item, 'values')[0]
                        os.remove(os.path.join(self.current_dir, file_name))
                    elif self.browser_list.item(item, 'tags')[0] == 'folder':
                        folder_name = self.browser_list.item(item, 'values')[0]
                        os.rmdir(os.path.join(self.current_dir, folder_name))
                        self.unpin_dir(os.path.join(self.current_dir, folder_name))
        self.refresh_browser()

    def browser_item_rename(self, event=None):
        if len(self.browser_list.selection()) > 1:
            messagebox.showerror(title='Rename Item', message='You can only rename one item at a time')
        else:
            item_type = self.browser_list.item(self.browser_list.selection()[0], 'tags')[0]
            selected_item = self.browser_list.selection()[0]
            old_name = self.browser_list.item(selected_item, 'values')[0]
            old_name = os.path.join(self.current_dir, old_name)
            new_name = utils.input_string_dialog(title='Rename Item',
                                                 prompt='Please type the new name',
                                                 theme=self.theme)
            if new_name:
                # Retain file extension if the selected item is a file
                if os.path.isfile(old_name):
                    file_extension = os.path.splitext(old_name)[1]
                    if not new_name.endswith(file_extension):
                        new_name += file_extension
                # Check if new name already exists
                new_name = os.path.join(self.current_dir, new_name)
                if os.path.exists(new_name):
                    return messagebox.showerror(title='Rename Item',
                                                message=f'{item_type} name "{new_name}" already exists.')
                os.rename(old_name, new_name)
                self.refresh_browser()

    def new_folder(self, event=None):
        new_folder = utils.input_string_dialog(title='New Folder',
                                               prompt='Enter new folder name',
                                               theme=self.theme)
        if new_folder:
            # Check if folder name already exists
            if os.path.exists(os.path.join(self.current_dir, new_folder)):
                return messagebox.showerror(title='New Folder',
                                            message=f'Folder name "{new_folder}" already exists')
            os.makedirs(os.path.join(self.current_dir, new_folder))
            self.refresh_browser()

    def select_all(self, event=None):
        for item in self.browser_list.get_children():
            self.browser_list.focus(item)
            self.browser_list.selection_add(item)

    def select_none(self, event=None):
        for item in self.browser_list.selection():
            self.browser_list.selection_remove(item)

    def invert_selection(self, event=None):
        for item in self.browser_list.get_children():
            if item in self.browser_list.selection():
                self.browser_list.selection_remove(item)
            else:
                self.browser_list.focus(item)
                self.browser_list.selection_add(item)

    def clipboard_item(self, clipboard_type, event=None):
        assert clipboard_type in ('cut', 'copy'), 'Clipboard can only be either copy or cut'
        self.clipboard_clear()
        clipboard = ''
        for item in self.browser_list.selection():
            item = self.browser_list.item(item, 'values')[0]
            item = os.path.join(self.current_dir, item)
            clipboard += item + '|'
        if clipboard:
            self.clipboard_append(clipboard.strip('|'))
            self.clipboard_type.set(clipboard_type)
        self.update()

    def paste_item(self, event=None):
        clipboard = self.clipboard_get().split('|')
        if self.clipboard_type.get() == 'cut':
            for item in clipboard:
                item_name = os.path.split(item)[1]
                try:
                    os.rename(item, os.path.join(self.current_dir, item_name))
                except FileExistsError:
                    # Abort duplicated items
                    messagebox.showerror(title='Paste error', message=f'"{item_name}" already exixts in this directory')
            self.clipboard_clear()
            self.clipboard_type.set('')
            self.refresh_browser()
        elif self.clipboard_type.get() == 'copy':
            for item in clipboard:
                item_name = os.path.split(item)[1]
                dst_dir = os.path.join(self.current_dir, item_name)
                if not os.path.exists(dst_dir):
                    if os.path.isfile(item):
                        shutil.copyfile(item, dst_dir)
                    elif os.path.isdir(item):
                        shutil.copytree(item, dst_dir)
                else:
                    if self.current_dir == os.path.split(item)[0]:
                        pass    # Just ignore when user attempts to copy items and paste them into the exact same place
                    else:
                        messagebox.showerror(title='Paste error',
                                             message=f'"{os.path.split(item)[1]}" already exists in this directory')
            self.refresh_browser()

    # Functions related to menus (2 functions)
    def reset_menus(self, event=None):
        self.file_menu.entryconfig('Open', state=DISABLED, command=None)
        self.edit_menu.entryconfig('Pin to quick access', state=DISABLED)
        self.edit_menu.entryconfig('Rename', state=DISABLED)
        self.edit_menu.entryconfig('Delete', state=DISABLED)
        self.edit_menu.entryconfig('Copy', state=DISABLED)
        self.edit_menu.entryconfig('Cut', state=DISABLED)

    def trace_clipboard(self, event=None):
        if self.clipboard_type.get():
            self.edit_menu.entryconfig('Paste', state=NORMAL)
        else:
            self.edit_menu.entryconfig('Paste', state=DISABLED)

    # Function related to My Computer (1 function)
    def open_drive(self, event=None):
        # Add the current directory to back stack
        self.back_stack.append(self.current_dir)
        self.back_button.config(state=NORMAL)  # Also enable the back button
        # Clean forward stack and disable forward button
        self.forward_stack.clear()
        self.forward_button.config(state=DISABLED)
        # Get new directory from the select folder name
        selected_drive = self.my_computer_list.selection()[0]
        self.current_dir = self.my_computer_list.item(selected_drive, 'values')[0].split()[-1] + '\\'
        self.title(self.my_computer_list.item(selected_drive, 'values')[0])
        # Refresh the browser
        self.refresh_browser()

    # Functions related to the navigation buttons (back, forward, up) (3 functions)
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

    def backspace_pressed(self, event=None):
        print(self.back_button['state'])
        # I dunno why we need to print the state to actually get the state string from self.back_button['state']
        # Something hilarious must be inside tkinter source code and I don't wanna check it
        if self.back_button['state'] == DISABLED:
            self.up_button_clicked()
        else:
            self.back_button_clicked()

    # Functions related to quick access (4 functions)
    def refresh_quick_access(self, event=None):
        # Clear the current quick access
        for item in self.quick_access_list.get_children():
            self.quick_access_list.delete(item)
        # Read the directories stored in the data file
        try:
            with open(os.path.join(self.data_path, 'pinned_list.bin'), 'rb') as f:
                directories = f.read().decode('utf-8')
                self.pinned_list = directories.split('\n')
        except FileNotFoundError:
            try:
                os.makedirs(self.data_path)
            except FileExistsError:
                pass
        # Add read directories to quick access
        for i in range(len(self.pinned_list)):
            dir_name = os.path.split(self.pinned_list[i])[1]
            self.quick_access_list.insert(parent='',
                                          iid=i,
                                          tag='pinned',
                                          index=END,
                                          values=(dir_name,))

    def pin_dir(self, event=None):
        for selected_folder in self.browser_list.selection():
            # Only folders can be pinned
            if self.browser_list.item(selected_folder, 'tags')[0] == 'folder':
                selected_folder = self.browser_list.item(selected_folder, 'values')[0]
                selected_dir = os.path.join(self.current_dir, selected_folder)
                if selected_dir not in self.pinned_list:
                    self.pinned_list.append(selected_dir)
        with open(os.path.join(self.data_path, 'pinned_list.bin'), 'wb') as f:
            f.write('\n'.join(self.pinned_list).encode('utf-8'))
        self.refresh_quick_access()

    def unpin_dir(self, directory=None, event=None):
        if directory:
            # To unpin a folder given its directory
            if directory in self.pinned_list:
                self.pinned_list.remove(directory)
        else:
            # To unpin a folder directly from quick access selections
            selected_folder = self.quick_access_list.selection()[0]
            self.pinned_list.pop(selected_folder)
        with open(os.path.join(self.data_path, 'pinned_list.bin'), 'wb') as f:
            f.write('\n'.join(self.pinned_list).encode('utf-8'))
        self.refresh_quick_access()

    def open_pinned_dir(self, event=None):
        # Add the current directory to back stack
        self.back_stack.append(self.current_dir)
        self.back_button.config(state=NORMAL)  # Also enable the back button
        # Clean forward stack and disable forward button
        self.forward_stack.clear()
        self.forward_button.config(state=DISABLED)
        # Get new directory from the select folder name
        selected_dir = int(self.quick_access_list.selection()[0])
        self.current_dir = self.pinned_list[selected_dir]
        self.title(self.quick_access_list.item(selected_dir, 'values')[0])
        self.refresh_browser()

    # Functions related to search bar (3 functions)
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
        else:
            temp = self.search_bar.get()
            self.refresh_browser()
            self.search_bar.delete(0, END)
            self.style.configure('Search.TEntry', foreground='black')
            self.search_bar.insert(0, temp)
            for item in self.browser_list.get_children():
                if self.search_bar.get().lower() not in self.browser_list.item(item, 'values')[0].lower():
                    self.browser_list.delete(item)
            self.dir_bar.delete(0, END)
            self.dir_bar.insert(0,
                                f'Search result for "{self.search_bar.get()}" in {os.path.split(self.current_dir)[1]}')
        self.browser_list.focus_set()

    # Functions related to directory bar (6 functions)
    def dir_bar_focus_in(self, event=None):
        self.dir_bar.delete(0, END)
        self.dir_bar.insert(0, self.current_dir)
        self.dir_bar.select_range(0, END)

    def dir_bar_focus_out(self, event=None):
        self.dir_bar.delete(0, END)
        current_dir = self.current_dir.replace('/', '\\').split('\\')
        current_dir = ' > '.join(current_dir)
        self.dir_bar.insert(0, current_dir)

    def dir_browse(self, event=None):
        if self.dir_bar.get() == self.current_dir:
            pass
        else:
            try:
                # If an error is raised after this line, then the directory doesn't exist
                os.chdir(self.dir_bar.get())
                self.current_dir = self.dir_bar.get().replace('/', '\\')
                self.refresh_browser()
            except WindowsError:
                pass
        self.browser_list.focus_set()

    def dir_select(self, event=None):
        self.current_dir = self.dir_bar.get()
        self.refresh_browser()
        self.browser_list.focus_set()

    def dir_bar_destroy(self, event=None):
        with open(os.path.join(self.data_path, 'dirs_list.bin'), 'wb') as f:
            f.write('\n'.join(self.recent_dirs_list).encode('utf-8'))

    def add_recent_dir(self):
        if self.current_dir in self.recent_dirs_list:
            self.recent_dirs_list.remove(self.current_dir)
        self.recent_dirs_list.insert(0, self.current_dir)
        while len(self.recent_dirs_list) > 20:
            # We should only keep the latest 20 directories
            self.recent_dirs_list.pop()
        self.dir_bar['values'] = self.recent_dirs_list


# Functions
def new_file_explorer(title='File Explorer', size='640x480', theme='vista', directory=os.getcwd(), data_path=None):
    return _FileExplorerWindow(title, size, theme, directory, data_path)