import tkinter as tk
from tkinter import simpledialog
import keyboard
import pyperclip

input_text = None


def prompt_for_text():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", "Enter macro")
    if user_input is not None:
        print(f"You entered: {user_input}")
        copy_to_clipboard(user_input)
        root.destroy()
    else: 
        print("No input provided.")
        simpledialog.messagebox.showinfo("Info", "Please enter text.")
#Creates a simple dialog to prompt the user for text input

def copy_to_clipboard(user_input):
    filename = user_input.lower() + ".txt" ### appends file extension 
    try:
        file = open(filename, 'r')
        content = file.read() ### reads file
        print("Successfully copied " + user_input)
        pyperclip.copy(content) ### copies content to clipboard
    except FileNotFoundError:
        print("Error: File not found.") 
        simpledialog.messagebox.showinfo("Info", "Macro does not exist.")
        prompt_for_text()
        ###handles the error for when someone inevitably types a macro that doesn't exist

if __name__ == "__main__":

    shortcut = 'ctrl+alt+c'  # Define the keyboard shortcut
    keyboard.add_hotkey(shortcut,prompt_for_text)
    keyboard.wait()

