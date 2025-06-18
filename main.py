import tkinter as tk
from tkinter import simpledialog
import keyboard
import pyperclip
from datetime import datetime

def prompt_for_text():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", "Enter macro")
    if user_input == "":
        print("No input provided.")
        simpledialog.messagebox.showinfo("Info", "Please enter text.")
        prompt_for_text()
    else:
        print(f"You entered: {user_input}")
        copy_to_clipboard(user_input)
        root.destroy()
       
#Creates a simple dialog to prompt the user for text input

def copy_to_clipboard(user_input):
    filename = "Macros\\" + user_input.lower() + ".txt" ### appends file extension and folder
    print("Debug: file path - " + filename)
    try:
        file = open(filename, 'r')
        content = file.read() ### reads file
        finaltext = autofill(content)
        pyperclip.copy(finaltext) ### copies content to clipboard
        print("Successfully copied " + user_input)
    except FileNotFoundError:
        print("Error: File not found.") 
        simpledialog.messagebox.showinfo("Info", "Macro does not exist.")
        prompt_for_text()
        ###handles the error for when someone inevitably types a macro that doesn't exist


def autofill(content):
    """Replaces placeholders in the content."""
    content = content.replace("[date]", datetime.now().strftime("%m-%d-%Y"))
    content = content.replace("[time]", datetime.now().strftime("%I:%M %p"))
    content = content.replace("[provider]", provider)
    return content

def defineprovider():
    provider = simpledialog.askstring("Provider", "Enter your provider")
    print("Today's provider is " + provider)
    return provider


if __name__ == "__main__":

    shortcut = 'ctrl+alt+c'  # Define the keyboard shortcut
    provider = defineprovider()  # Prompt for provider
    keyboard.add_hotkey(shortcut,prompt_for_text)
    keyboard.wait()

