try: from Modules.dependencies import *
except ImportError: raise Exception("Dependencies not found")
if __name__ == "__main__":
    print("This script is not designed to be run directly.")
    print("Exiting script.")
    exit()

def convert_to_sentence_case(text):
    text = text.lower()  # Convert entire string to lowercase
    sentences = re.split(r'([.!?]\s*)', text) # Split by sentence-ending punctuation
    result = []
    for i, sentence_part in enumerate(sentences):
        if sentence_part.strip(): # Ensure the part is not empty
            if i % 2 == 0: # This is a sentence content part
                result.append(sentence_part.strip().capitalize())
            else: # This is a punctuation and space part
                result.append(sentence_part)
    return "".join(result)

def release_modifiers():
    keyboard.release('shift')
    keyboard.release('ctrl')
    keyboard.release('alt')

def paste_text(): #ctrl v presser
    release_modifiers()
    sleep(0.1)
    keyboard.press_and_release('ctrl+v')
    sleep(0.1)
    release_modifiers()

def exception_handler(e):
    if e == KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
    else:
        print(f"Something went wrong: {str(e)}")

def sync(fn_list):
    try:
        processes = []
        for fn in fn_list:
            p = threading.Thread(target=fn)
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("All functions completed.")
    except Exception as e:
        exception_handler(e)

