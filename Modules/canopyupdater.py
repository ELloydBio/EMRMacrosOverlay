if not __name__ == "__main__":
    from Modules.dependencies import *
else:
    from dependencies import *

#### NOTES

'''
TO DO:
    GET PT INFO:
        DEMOGRAPHICS
        LABS
        VITALS
        OTHER?

KNOWN TEST PT CODES 
551435
850977
'''
#### CONFIG
username = "carlton.lloyd"
##password = "lorum_ipsum"      #This is here partially as a joke, but partially as a placeholder if I ever bother to store an encrypted password
table_class = "v-table__wrapper"
#"//*[@id='inspire']/div/div/main/div/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[3]/div[1]/table/tbody/tr"
#KNOWN ISSUE: This XPATH is not robust to changes in the page structure. 
#Consider using a more stable locator strategy, such as CSS selectors or IDs if available.


#### Functions

#Consider adding a function call MRNs from appointments.csv

def web_init():
    global driver
    driver = webdriver.Chrome()

def web_init_headless():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

def focus():
        # Force focus to the active Selenium window
    driver.switch_to.window(driver.current_window_handle)
    driver.maximize_window()  # Optional: maximize to ensure visibility
    pya.click(128, 128)

def ctrl_a_ctrl_c():
    pyperclip.copy("")  # Clear the clipboard before copying
    pya.hotkey('ctrl', 'a')
    sleep(0.1)
    pya.hotkey('ctrl', 'c')
    print("PDF viewer loaded successfully.")
    sleep(0.1)
    pdf_text = pyperclip.paste()
    print(f"debug: {pdf_text}")
    return pdf_text  # Return the extracted text

def numbers_to_list():
    try:
        """
        Takes a string of numbers separated by newlines and converts it into a list of integers.
        """
        print("Enter numbers, one per line. Press Enter on an empty line to finish.")
        
        numbers_str = ""
        while True:
            line = (simpledialog.askstring("Input", "Enter a number (or leave blank to finish):"))
            if not line:  # Check if the line is empty
                break
            numbers_str += line + "\n"  # Append the line and a newline character

        # Split the string by newline characters, filter out empty strings, and convert to integers
        numbers_list = [int(num) for num in numbers_str.strip().split('\n') if num.strip()]
        
        return numbers_list
    except Exception as e:
        raise ValueError(f"Invalid input: {e}. Please enter valid numbers separated by newlines.")

def createurl(input_list): 

    # Create a list of URLs based on the input list
    # Designed to call the list from numbers to list

    url_list = []
    for input in input_list:
        url = "https://onecanopy.oakstreethealth.com/#/charts/" + str(input) + "/documents"
        url_list.append(url)
        print("Debug: URL created - " + url)
    return url_list


def login(password_input): 
    web_init()
    #Initialize Canopy to log in. Required each time the script is run
    #KNOWN ISSUE: no password error handling
    #TO DO: add error for no password and wrong password
    driver.get("https://onecanopy.oakstreethealth.com/#/tracker")  # Opens canopy tracker page

    try:
        # Wait for the username field to be present and visible
        username_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "Username")) # Replace "username" with the actual ID or other locator strategy
        )
        username_field.send_keys(username)

        # Wait for the password field to be present and visible
        password_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "Password")) # Replace "password" with the actual ID or other locator strategy
        )
        password_field.send_keys(password_input)

        # Wait for the login button to be clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login-btn")) # Replace "login-button" with the actual ID or other locator strategy
        )
        login_button.click()

        # Wait for the dashboard page to load (e.g., check for a specific element or title)
        WebDriverWait(driver, 10).until(
            EC.title_contains("Canopy") # Replace with a relevant title or element on the logged-in page
        )
        print("Login successful!")

    except Exception as e:
        print(f"Login failed: {e}")
        raise Exception("Login failed. Please check your credentials or the page structure.")

def get_XPATH(elm):
    # Expects a Selenium WebElement as input and returns its XPath
    try:
        if not hasattr(elm, "tag_name"):
            raise TypeError("get_XPATH expects a Selenium WebElement, not a string or other type.")
        e = elm
        xpath = elm.tag_name
        while e.tag_name != "html":
            e = e.find_element(By.XPATH, "..")
            neighbours = e.find_elements(By.XPATH, "../" + e.tag_name)
            level = e.tag_name
            if len(neighbours) > 1:
                level += "[" + str(neighbours.index(e) + 1) + "]"
            xpath = level + "/" + xpath
        return "/" + xpath
    except Exception as ex:
        print(f"Error finding XPath for element: {ex}")
        return None

def find_last_note():
    # Find the last progress note or H&P note on the page
    # This code is an absolute mess, but it works :)
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, table_class))
        )
        elm = driver.find_element(By.CLASS_NAME, table_class)
        table_xpath = get_XPATH(elm)
        print(f"Debug: Found table XPath - {table_xpath}")
        table_r1_XPATH = f"{table_xpath}/table/tbody/tr"
        last_note = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, table_r1_XPATH))
            )
            # Obtain the number of rows in body
        print("Debug: Attempting to find the last note in the table.")
        table_data_xpath = table_r1_XPATH + "[1]/td"
        rows = 1+len(driver.find_elements(By.XPATH, table_r1_XPATH))
        if rows > 25:
            rows = 25 #limit search to 25 rows
        # Obtain the number of columns in table
        cols = len(driver.find_elements(By.XPATH, table_data_xpath))
            # Print rows and columns
        print(rows)
        print(cols)

        #define data structure for storing document data 
        dt = numpy.dtype([("Date", "datetime64[ns]"), ("Author", "U100"), ("Type", "U100"), ("Title", "U100")])
        document_array = numpy.empty((0,), dtype=dt)
        # Printing the data of the table
        for r in range(1, rows):
            line = []
            for p in range(1, cols+1):
                # obtaining the text from each column of the table
                value = driver.find_element(By.XPATH,
                    table_r1_XPATH + "[" +str(r)+ "]/td["+str(p)+"]").text
                if p == 1:
                    try:  # Attempts to convert a date into a numpy datetime64 object
                        dt_object_pandas = pd.to_datetime(value)
                        dt_object_numpy = dt_object_pandas.to_numpy()
                        line.append(dt_object_numpy)
                    except Exception:
                        print(f"Warning: Unable to parse date from '{value}'.")
                        line.append(numpy.datetime64('NaT'))
                else:
                    line.append(value)
            try:
                document_array = numpy.append(document_array, numpy.array([tuple(line)], dtype=dt))
            except ValueError:
                document_array = numpy.array([tuple(line)], dtype=dt)
        print(document_array)

        title_mask = (document_array['Type'] == "History and Physical") | (document_array['Type'] == "Progress Note")
        filtered_data = document_array[title_mask]
        print(filtered_data)
        # 2. Find the index of the most recent date within the filtered data
        if filtered_data.size > 0:
            most_recent_index_in_filtered = numpy.argmax(filtered_data['Date'])
            # Get the index in the original array
            indices_in_original = numpy.where(title_mask)[0]
            most_recent_index_in_original = indices_in_original[most_recent_index_in_filtered]
            
            # 3. Select the row based on this index
            most_recent_row = filtered_data[most_recent_index_in_filtered]
            print(most_recent_row)
        else:
            print(f"No recent documents found")

        last_note = table_r1_XPATH + "[" + str(most_recent_index_in_original + 1) + "]"
        target_final = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, last_note))) 
        target_final.click()
        print("Clicked on the last note. DEBUG: INDEX = ", most_recent_index_in_original + 1)
        sleep(1)
    except Exception as e:
        print(f"Failed to find or click on the last note: {e}")
        raise Exception("Failed to find or click on the last note.")

def get_pdf_text():
    """Extracts text from the PDF document."""
    try:
        # Wait for the PDF viewer to load
        iframe_locator = (By.CSS_SELECTOR, 'iframe.iframe.fs-exclude')

        iframe_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(iframe_locator)
        )

        # Now that the iframe element is found, get the value of its 'src' attribute.
        src_value = iframe_element.get_attribute('src')
        driver.get(src_value)
        sleep(1)
        focus()
        pdf_text = ctrl_a_ctrl_c()
        if not pdf_text or pdf_text == "":
            sleep(5)  # Wait for the PDF viewer to load completely
            pdf_text = ctrl_a_ctrl_c()
            if not pdf_text or pdf_text == "":
                raise Exception("No text extracted from the PDF. Ensure the PDF viewer is loaded correctly.")
        else:
            print("Text extracted from PDF successfully.")
            pyperclip.copy(pdf_text)  # Copy the text to clipboard for debugging
            return pdf_text  # Return the extracted text
    except Exception as e:
        print(f"Error loading PDF viewer: {e}")
        raise Exception("Failed to load PDF viewer or extract text.")








# MORNING INITIALIZATION MODULE

def get_schedule(provider):
    try:
        TO = 10  # int timeout in seconds, higher for debugging lower for production
        # Gets raw schedule data from the main canopy tracker page
        schedule_data = ""
        try:
            driver.get("https://onecanopy.oakstreethealth.com/#/tracker")
            WebDriverWait(driver, TO).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div[2]/header/div/button[1]"))
            )
            button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div[2]/header/div/button[1]")
            button.click()

            WebDriverWait(driver, TO).until(
                EC.presence_of_element_located((By.ID, "provider-filter-autocomplete"))
            )
            provider_field = driver.find_element(By.ID, "provider-filter-autocomplete")
            provider_field.send_keys(provider)  # Set the provider field
            sleep(3)  # Wait for the input to be processed
            #suboptimal, better to wait for provider name to appear in the dropdown
            keyboard.send(keyboard.KEY_DOWN)
            keyboard.send('enter')  # Simulate pressing Enter to apply the filter

            WebDriverWait(driver, TO).until(
                EC.presence_of_element_located((By.CLASS_NAME, "schedule-view-default-tr"))
            )
            schedule_data = driver.find_element(By.TAG_NAME, "body").text
            print("Data retreived from canopy")
        except Exception as e:
            print(f"Error getting schedule data: {e}")
        driver.quit()  # Close the browser after getting the schedule data
        return schedule_data
    except Exception as e:
        print(f"Error getting schedule data: {e}")
        return None

def init_module(password, provider):
    web_init()
    login(password)
    schedule_data = get_schedule(provider)
    return schedule_data




#### BODY

def main(pwd):
        login(pwd) #initializes login with user-provided password
        for url in url_list: # for each url, open the documents page
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until( #wait until the document is fully loaded
                    EC.presence_of_element_located((By.CLASS_NAME, "document-sub-tab-container")) # Replace with an actual element ID!! Could be literally anything as long as its on the page
                )
                print("Document fully loaded.")
                find_last_note() 
                get_pdf_text() 
                sleep(60)
                #parse_pdf_data()
                #update_canopy()
                #these currently do nothing, uncomment after completion
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                continue

if __name__ == "__main__":
    driver = webdriver.Chrome() 
    my_list = numbers_to_list() #user input for MRNs, may need to be ammended to read from a file or other source
    url_list = createurl(my_list)
    pwd = simpledialog.askstring("Input", "Enter Password:", show='*')  #Calls for userinput for password prior to log in - required because I'm too lazy/stupid to salt and hash a password corectly

    main(pwd)  # Call the main function with the user-provided password

    driver.quit()  # Close the browser after processing all URLs