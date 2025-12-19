if not __name__ == "__main__":
    from Modules.dependencies import *
else:
    from dependencies import *

def numbers_to_list():
    """
    Takes a string of numbers separated by newlines and converts it into a list of integers.
    """
    print("Enter numbers, one per line. Press Enter on an empty line to finish.")
    
    numbers_str = ""
    while True:
        line = input()
        if not line:  # Check if the line is empty
            break
        numbers_str += line + "\n"  # Append the line and a newline character

    # Split the string by newline characters, filter out empty strings, and convert to integers
    numbers_list = [int(num) for num in numbers_str.strip().split('\n') if num.strip()]
    
    return numbers_list


def createurl(input_list): 
    url_list = []
    for input in input_list:
        url = "https://onecanopy.oakstreethealth.com/#/charts/" + str(input) + "/suspects"
        url_list.append(url)
        print("Debug: URL created - " + url)
    return url_list

if __name__ == "__main__":
    try:
        my_list = numbers_to_list()
        print("The list of numbers is:", my_list)
        url_list=createurl(my_list)
        for url in url_list:
            webbrowser.open_new_tab(url)
            print(f"Opened patient chart: {url}")
            keyboard.wait('ctrl+shift+z')
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print("Error occurred:", e)