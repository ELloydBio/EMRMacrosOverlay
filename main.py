import tkinter as tk
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
###GUI Imports
import keyboard
import pyperclip
from datetime import datetime
import configparser 
###Functional Imports


def settingsGUI():
    print("Debug: Settings GUI opening")
    root = tk.Tk()
    root.title("Settings")
    root.geometry("600x400")

    label = ttk.Label(root, text="Enter provider name.")
    label.pack(pady=20)
    provider_entry = ttk.Entry(root)
    provider_entry.pack(pady=10)
    provider_entry.insert(0, provider)  # Pre-fill with current provider
    def save_provider():
        global provider
        provider = provider_entry.get()
        print("Provider updated to: " + provider)
        simpledialog.messagebox.showinfo("Info", "Provider updated successfully.")
        root.destroy()

    save_button = ttk.Button(root, text="Save", command=save_provider)
    save_button.pack(pady=10)  
    button = ttk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)

    root.mainloop()




def prompt_for_text():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", "Enter macro")
    if user_input == None:
        return
    else:
        print(f"You entered: {user_input}")
        copy_to_clipboard(user_input)
        root.destroy()
       
#Creates a simple dialog to prompt the user for text input

def copy_to_clipboard(user_input):
    try:
        filename = "Macros\\" + user_input.lower() + ".txt" ### appends file extension and folder
    except:
        print("Error: Invalid macro name.")
        filename = None
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
    content = content.replace("[date]", datetime.now().strftime("%m/%d/%Y"))
    content = content.replace("[time]", datetime.now().strftime("%I:%M %p"))
    content = content.replace("[provider]", provider)
    return content

def defineprovider():
    provider = simpledialog.askstring("Provider", "Enter your provider")
    print("Today's provider is " + provider)
    return provider


if __name__ == "__main__":

    shortcut = 'ctrl+alt+c'  # Define the keyboard shortcut
    settings =  'ctrl+alt+s'  # Define the settings shortcut
    provider = defineprovider()  # Prompt for provider
    keyboard.add_hotkey(shortcut,prompt_for_text)
    keyboard.add_hotkey(settings, settingsGUI)
    keyboard.wait()

