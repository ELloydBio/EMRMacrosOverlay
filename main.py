#TO DO
# Implement error handling for login failures (May fall under canopy updater module)
#### Including ways to validate the password, possibly by storing a salt+hash?
#Flesh out the main GUI
#### Improve layout and user experience

#Custom modules
import Modules.csvgenerator as csvgenerator
from Modules.canopyupdater import login, get_schedule, init_module
from Modules.functions import *

#Basic modules
from Modules.dependencies import *  # Import all from required modules


#CORE FUNCTION

#Creates a simple dialog to prompt the user for text input
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
       
def error_handler(user_input):
###handles the error for when someone inevitably types a macro that doesn't exist
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

def copy_to_clipboard():
    rawtext = prompt_for_text("")
    if isinstance(rawtext, str) == True:
        text = error_handler(rawtext)
        if text is None:
            return None
        else:
            pyperclip.copy(text)
            return text
        #print("Copied to clipboard: " + text)
        #uncomment for debug


def autofill(content):
    """Replaces placeholders in the content."""
    content = content.replace("[date]", datetime.now().strftime("%m/%d/%Y"))
    content = content.replace("[time]", datetime.now().strftime("%I:%M %p"))
    content = content.replace("[provider]", provider)
    return content

def paste_macro():
    if copy_to_clipboard() is not None:
        paste_text()

#ACCESSORY FUNCTION

def defineprovider(Default_Provider):
    provider = simpledialog.askstring("Provider", "Enter your provider", initialvalue=Default_Provider)
    if provider is None:
        provider = Default_Provider  # Fallback if no input is given
    print("Today's provider is " + provider)
    return provider

def create_csv():
    raw_data = simpledialog.askstring("Input", "Please enter the appointment data:")
    if raw_data:
        csvgenerator.convert_to_spreadsheet(raw_data)

def morning_initialization(password):
    global provider
    global Default_Provider
    if provider is None:
        provider = defineprovider(Default_Provider)  # Prompt for provider
    else:
        provider = defineprovider(provider)  # Use existing provider if defined
    pt_data = init_module(password, provider) #Open the canopy tracker page and get the schedule data
    csvgenerator.convert_to_spreadsheet(pt_data) # Convert the raw appointment data to a CSV file
    #theoretically this function shouldn't fail even if no appointments are found.
    return provider
 
def define_password():
    password = simpledialog.askstring("Password", "Enter your password", show='*')
    if password is None:
        raise Exception("No password entered.")
        password = "NULL STRING"
    return password

def clipboard_to_caps():
    text = pyperclip.paste()
    if text:
        if text == text.upper():
            print("Text is already in uppercase. No conversion needed.")
        else:
            caps_text = text.upper()
            pyperclip.copy(caps_text)
            print("Converted to uppercase and copied to clipboard.")

    else:
        print("Clipboard is empty. Nothing to convert.")


def hotkey(globalhotkeys):
    try:
        keyboard.remove_all_hotkeys()  # Clear existing hotkeys
    except:
        print("Running initial hotkey setup...")

    for key, function in globalhotkeys:
        print(f"Debug: Registering hotkey {key} for function {function.__name__}")
        keyboard.add_hotkey(key, function)


#GUI

def settingsGUI():
    global password
    if password is None:
        password = define_password()
    try:
        print("Debug: Settings GUI opening")
        root = tk.Tk()
        root.title("EMR Macros")
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
        copy_button = ttk.Button(root, text="Copy macro", command=copy_to_clipboard)
        copy_button.pack(pady=10)
        new_button = ttk.Button(root, text="New macro", command=create_new_macro)
        new_button.pack(pady=10)
        button = ttk.Button(root, text="Close", command=root.destroy)
        button.pack(pady=10)
        init = ttk.Button(root, text="Initialize", command=lambda: (morning_initialization(password), root.destroy()))
        init.pack(pady=10)

        root.mainloop()
    except Exception as e:
        exception_handler(e)

def create_new_macro():
    def cleanup():
        new_macro_root.destroy()
        hotkey(globalhotkeys)
        terminal_ctrl()

    try:
        new_macro_root = tk.Tk()
        new_macro_root.title("New Macro")
        new_macro_root.geometry("600x700")
        new_macro_root.protocol("WM_DELETE_WINDOW", cleanup)

        label = ttk.Label(new_macro_root, text="Enter macro name.")
        label.pack(pady=20)
        macro_entry = ttk.Entry(new_macro_root)
        macro_entry.pack(pady=10)

        details_entry = tk.Text(new_macro_root, height=12, width=40)
        details_entry.pack(pady=30)

        def save_macro(): ###LOGIC FOR CREATING MACRO FILE
            new_macro_name = macro_entry.get()
            filename = new_macro_name.lower() + ".txt"
            filepath= "Macros\\" + filename
            try:
                if new_macro_name is not None:
                    if os.path.isfile(filepath) == False:
                        # Create a new file for the macro
                        with open(filepath, 'w') as file:
                            file.write(details_entry.get("1.0", tk.END))
                        print("New macro created: " + filename)
                        simpledialog.messagebox.showinfo("Info", "Macro created successfully.")
                        new_macro_root.destroy()
                    else:
                        print("Macro already exists: " + filename)
                else:
                    print("No macro name entered.")
            except Exception as e:
                simpledialog.messagebox.showinfo("Error", "An error occurred: " + str(e))
                exception_handler(e)
        #END MACRO CREATION

        save_button = ttk.Button(new_macro_root, text="Save", command=save_macro)
        save_button.pack(pady=10)
        button = ttk.Button(new_macro_root, text="Close", command=new_macro_root.destroy)
        button.pack(pady=10)
    except Exception as e:
        print(f"Something went wrong: {str(e)}")
    # Do not call terminal_ctrl() here, as it will block after the GUI is opened.

def terminal_ctrl(): #MANAGES TERMINAL COMMANDS (NAIVE APPROACH, FIX LATER)
    try:    
        command = str.lower(input("EMR Macros>"))
        if command == "reset":
            print("Resetting application...")
            hotkey(globalhotkeys)

        elif command == "exit":
            print("Exiting application...")
            exit()
        elif command == "copy":
            copy_to_clipboard()
        elif command == "gui":
            settingsGUI()
        elif command == "help" or command == "--help" or command == "-h":
            print("reset - resets keybinds if program stops accepting input")
            print("exit - exits the application")
            print("copy - copies the selected text to clipboard")
            print("GUI - opens the settings GUI")
        else:
            print("Unknown command.")
        terminal_ctrl()
    except Exception as e:
        exception_handler(e)

if __name__ == "__main__":

    globalhotkeys = [ #Edit this list to change keybinds
        #as ('shortcut', function)
        ('ctrl+alt+c', copy_to_clipboard),
        ('ctrl+alt+v', paste_text),
        ('ctrl+alt+s', settingsGUI),
        ('ctrl+alt+e', create_csv),
        ('ctrl+alt+u', clipboard_to_caps)
    ]
    Default_Provider = "Gregory House, MD"  # Default provider name


    #BODY
    provider = defineprovider(Default_Provider)
    password = define_password()
    hotkey(globalhotkeys) # Register global hotkeys
    #sync([settingsGUI, terminal_ctrl]) #INTRODUCES SERIOUS BUGS TEST LATER
    settingsGUI(); terminal_ctrl()


    #EXIT
    try:
        while True:
            keyboard.wait()
    except KeyboardInterrupt:

        print("Keyboard interrupt received. Exiting...")
