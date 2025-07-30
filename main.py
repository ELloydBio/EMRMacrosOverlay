import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
from turtle import reset
###GUI Imports
import keyboard
import pyperclip
from datetime import datetime
import configparser 
import time
import csvgenerator
from canopyupdater import login, get_schedule
###Functional Imports

def release_modifiers():
    keyboard.release('shift')
    keyboard.release('ctrl')
    keyboard.release('alt')

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




def prompt_for_text(input):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", "Enter macro", initialvalue=input)
    if user_input == None:
        return
    else:
        print(f"You entered: {user_input}")
        return user_input
        root.destroy()
       

#Creates a simple dialog to prompt the user for text input

def error_handler(user_input):
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
        return finaltext
    except FileNotFoundError:
        print("Error: File not found.") 
        simpledialog.messagebox.showinfo("Info", "Macro does not exist.") 
        ###handles the error for when someone inevitably types a macro that doesn't exist

def copy_to_clipboard():
    rawtext = prompt_for_text("")
    if isinstance(rawtext, str) == True:
        text = error_handler(rawtext)
        if text is None:
            return
        else:
            pyperclip.copy(text)
        #print("Copied to clipboard: " + text)
        #uncomment for debug

def paste_to_chart():
    copy_to_clipboard()
    time.sleep(0.1)
    pyperclip.paste()
    #print("Pasted text: " + text)
    #uncomment for debug

def autofill(content):
    """Replaces placeholders in the content."""
    content = content.replace("[date]", datetime.now().strftime("%m/%d/%Y"))
    content = content.replace("[time]", datetime.now().strftime("%I:%M %p"))
    content = content.replace("[provider]", provider)
    return content

def defineprovider(Default_Provider):
    provider = simpledialog.askstring("Provider", "Enter your provider", initialvalue=Default_Provider)
    if provider is None:
        provider = Default_Provider  # Fallback if no input is given
    print("Today's provider is " + provider)
    return provider

def PasteWCTM():
    print("WCTM")
    pyperclip.copy("Will continue to monitor")

def create_csv():
    raw_data = simpledialog.askstring("Input", "Please enter the appointment data:")
    if raw_data:
        csvgenerator.convert_to_spreadsheet(raw_data)

def morning_initialization(password):
    provider = defineprovider(Default_Provider)  # Prompt for provider
    login(password)  # Initialize login with user-provided password
    pt_data = get_schedule(provider) #Open the canopy tracker page and get the schedule data
    csvgenerator.convert_to_spreadsheet(pt_data) # Convert the raw appointment data to a CSV file
    #theoretically this function shouldn't fail even if no appointments are found.
    return provider
 
def define_password():
    password = simpledialog.askstring("Password", "Enter your password", show='*')
    if password is None:
        raise Exception("No password entered.")
        password = ""
    return password

if __name__ == "__main__":

    #GLOBALS
    shortcut = 'ctrl+alt+c'  # Define the copy shortcut
    settings =  'ctrl+alt+s'  # Define the settings shortcut
    #paste =  'ctrl+alt+v'  # Define the paste shortcut
    WCMT = 'alt+w'  # Define the WCMT shortcut
    CSV  = 'ctrl+alt+e'  # Define the CSV shortcut
    Default_Provider = "Justine Goldberg MD"  # Default provider name
    reinit = 'ctrl+alt+r'  # Define the reset shortcut
    
    #BODY
    password = define_password()  # Prompt for password at the start

    init = messagebox.askyesno("Initialization", "Do you want to initialize the application? (This will log you in and set up your provider.)")
    if init:
        provider = morning_initialization(password)  # Run the morning initialization function
    else:
        provider = defineprovider(Default_Provider)  # Prompt for provider if not initializing
    
    #setup hotkeys
    #keyboard.add_hotkey(reinit, morning_initialization(password)) this shit does not work
    keyboard.add_hotkey(shortcut,copy_to_clipboard)
    keyboard.add_hotkey(settings, settingsGUI)
    keyboard.add_hotkey(WCMT, PasteWCTM)
    #keyboard.add_hotkey(paste, paste_to_chart)
    keyboard.add_hotkey(CSV, create_csv)
    
    #EXIT
    try:
        while True:
            keyboard.wait()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")