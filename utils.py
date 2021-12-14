from tkinter import *
from tkinter import ttk


# Classes
class _InputDialog(Toplevel):

    def __init__(self, title, prompt, theme='vista'):
        super().__init__()

        self.style = ttk.Style(self)
        self.style.theme_use(theme)
        self.title(title)

        self.frame = ttk.Frame(self, relief=FLAT, padding=15)
        self.frame.pack()
        self.prompt = ttk.Label(self.frame, text=prompt)
        self.prompt.grid(row=0, column=0, columnspan=2, sticky=N)
        self.text = StringVar()
        self.text.trace_add('write', callback=lambda arg1, arg2, arg3: self.trace_entry())
        self.entry = ttk.Entry(self.frame, textvariable=self.text, width=30, exportselection=0)
        self.entry.grid(row=1, column=0, columnspan=2)
        self.entry.bind('<Return>', self.ok_button_pressed)
        self.ok_button = ttk.Button(self.frame, text='OK', state=DISABLED, command=self.ok_button_pressed)
        self.ok_button.grid(row=2, column=0, stick=S+E)
        self.cancel_button = ttk.Button(self.frame, text='Cancel', command=self.cancel_button_pressed)
        self.cancel_button.grid(row=2, column=1, sticky=S+W)

        self.entry.focus_force()
        self.wait_window()

    def trace_entry(self):
        if self.entry.get():
            self.ok_button.config(state=NORMAL)
        else:
            self.ok_button.config(state=DISABLED)

    def destroy(self):
        # If you quit this dialog window then nothing will be returned
        self.entry.delete(0, END)
        Toplevel.destroy(self)

    def ok_button_pressed(self, event=None):
        # If quit using the ok button then the content in the entry will be returned
        if self.entry.get():
            Toplevel.destroy(self)

    def cancel_button_pressed(self, event=None):
        self.destroy()


# Functions
def input_string_dialog(title, prompt, theme='vista'):
    dialog = _InputDialog(title, prompt, theme)
    return dialog.text.get()
