try:
    from Modules.dependencies import *
except ImportError:
    from dependencies import *
import base64
from selenium.webdriver.common.print_page_options import PrintOptions


chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.getcwd(), # Set download directory to current working directory
    "download.prompt_for_download": False, # Prevents download pop-up
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

#driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome()

class patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.qualityBP = None
        self.status = None
        self.noteBPs = []
        self.notedate = None
        self.success = False
    
    def __repr__(self):
        return f"Patient(ID: {self.patient_id}, Quality BP: {self.qualityBP}, Quality Status: {self.status}, Note BPs: {self.noteBPs}, Note Date: {self.notedate}, Success: {self.success})"
    
def login(): #Initialize Canopy. Required once each time the script is run. User must manually log in. 
    driver.get("https://onecanopy.oakstreethealth.com/#/tracker")  # Opens canopy tracker page
    sleep(3)  # Wait for page to load
    try:
        WebDriverWait(driver, 60).until(
            EC.title_contains("Canopy") # Replace with a relevant title or element on the logged-in page
        )
        print("Login successful!")

    except Exception as e:
        print(f"Login failed: {e}")
        raise Exception("Login failed. Please check your credentials or the page structure.")

def get_patients():#Create GUI for login credentials
    root = tk.Tk()
    root.title("Patient input")
    root.geometry("600x400")
    tk.Label(root, text="Enter Patient IDs (separated by spaces):").grid(row=0, column=0, columnspan=2)
    patient_entry = tk.Text(root, width=25, height=15)
    patient_entry.grid(row=1, column=0, columnspan=2)
    patient_data_holder = {'data': ''}
    def paste():
        patient_entry.delete(1.0, tk.END)
        patient_entry.insert(1.0, pyperclip.paste())
    def submit():
        patient_data_holder['data'] = str(patient_entry.get(1.0, tk.END)).strip()
        root.destroy()
    paste_button = tk.Button(root, text="Paste from Clipboard", command=paste)
    paste_button.grid(row=2, column=0)
    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.grid(row=2, column=1)

    root.mainloop()
    return patient_data_holder.get('data', '')

def create_patients(patient_data): #Creates patient list from input string
    patient_ids = patient_data.split()
    patients = [patient(pid) for pid in patient_ids]
    return patients

def get_gaps_BP(patient_id): #Pulls blood pressure from gaps
    url = f"https://onecanopy.oakstreethealth.com/#/charts/{patient_id}/quality"
    driver.get(url)
    sleep(3)  # Wait for page to load
    try:
        WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.TAG_NAME, "tr"))    
    )
    except Exception as e:
        print(f"Failed to load patient quality page for {patient_id}: {e}")
        return None
    rows = driver.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 1 and "Blood Pressure" in cells[0].text:
            openclosed = cells[1].text
            bp_raw= cells[2].text
            print(f"Patient ID: {patient_id} - Status: {openclosed} - {bp_raw}")
            return (openclosed, bp_raw)

def extract_blood_pressures(text): #Extracts blood pressures from text. Used within get_note_BP
    # Regex Breakdown:
    # \b       : Word boundary (ensures we don't catch numbers inside other strings)
    # \d{2,3}  : Matches 2 to 3 digits (the systolic)
    # /        : Matches the literal forward slash
    # \d{2,3}  : Matches 2 to 3 digits (the diastolic)
    # \b       : Word boundary
    # \s?     : Matches optional whitespace around the slash
    
    pattern = r'\b\d{2,3}\s?/\s?\d{2,3}\b'
    
    # findall returns a list of all matches found in the text
    matches = re.findall(pattern, text)
    clean_bps = []
    for match in matches:
        parts = match.split('/')
        systolic = int(parts[0])
        diastolic = int(parts[1])
        
        # 2. Only keep it if BOTH numbers are greater than 31
        # This excludes dates like 12/25 or 01/30
        if systolic > 31 and diastolic > 31:
            clean_bps.append(match)
            
    return clean_bps

def get_note_BP(patient_id): #webscrapes notes for blood pressures
    url = f"https://onecanopy.oakstreethealth.com/#/charts/{patient_id}/documents"
    driver.get(url)
    sleep(3)  # Wait for page to load
    try:
        WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.TAG_NAME, "tr"))    
    )
    except Exception as e:
        print(f"Failed to load patient documents page for {patient_id}: {e}")
        return None
    rows = driver.find_elements(By.TAG_NAME, "tr")
    bp_list = []
    pdf_urls = []
    date_list = []
    try:
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 1:
                try:
                    if "History and Physical" in cells[2].text or "Progress Note" in cells[2].text:
                        cells[2].click()
                        sleep(2)  # Wait for document to load
                        iframe_element = driver.find_element(By.TAG_NAME, 'iframe')
                        pdf_url = iframe_element.get_attribute("src")
                        print(f"Found PDF URL: {pdf_url}")
                        date = (cells[0].text)
                        break
                except Exception as e:
                    print(f"Error processing row for patient {patient_id}: {e}")
                    continue
    except Exception as e:
        print(f"Error extracting BP from notes for patient {patient_id}: {e}")
        bp_list = ["Error: {e}"]
        return None                
    try:
            if pdf_url: #Logic to extract text from PDF via clipboard
                driver.get(pdf_url)
                sleep(2)  # Wait for PDF to load
                pya.click(x=400, y=300)  # Click to focus on the PDF viewer
                sleep(0.5)  # Wait for focus
                keyboard.press_and_release('ctrl+a')
                sleep(0.5)  # Wait for selection to complete
                keyboard.press('ctrl+c')
                sleep(0.5)  # Wait for clipboard to update
                keyboard.release('ctrl+c')
                sleep(0.5)
                pdf_text = pyperclip.paste()
                print(f"Extracted PDF text for patient {patient_id}:\n{pdf_text[:100]}\n")
                bp_list = extract_blood_pressures(pdf_text)
                if len(bp_list) > 0:
                    return bp_list, date
            else:
                print(f"No matching document found for patient {patient_id}.")
                return None
    except Exception as e:
        print(f"Error extracting text from PDF for patient {patient_id}: {e}")
        return None

def is_bp_controlled(bp_list): #Checks if BP is under 140/90
    """
    Checks if at least one BP in the list is < 140/90.
    Returns True if a match is found, False otherwise.
    """
    for bp in bp_list:
        try:
            # Split the string '120/80' into ['120', '80']
            parts = bp.split('/')
            systolic = int(parts[0])
            diastolic = int(parts[1])
            
            # Check the condition: Both must be strictly under the limit
            if systolic < 140 and diastolic < 90:
                return True 
                
        except (ValueError, IndexError):
            # This handles cases where the string might be malformed
            continue
            
    return False



if __name__ == "__main__":
    login()
    patient_data = get_patients()
    patients = create_patients(patient_data)
    all_parsed_data = []
    for p in patients:
        try:
            print("Patient object created:", p.patient_id)
            p.status, p.qualityBP = get_gaps_BP(p.patient_id)
            print(f"Updated Patient: {p}")
            p.noteBPs, p.notedate = get_note_BP(p.patient_id)
            if p.noteBPs:
                print(f"BP found in note: {p.noteBPs}")
                p.success = is_bp_controlled(p.noteBPs)
            print(f"Final Patient Data: {p}\n")
            parsed_data = [str(p.patient_id), str(p.status), str(p.qualityBP), str(p.noteBPs), str(p.notedate), str(p.success)]
        except Exception as e:
            print(f"Error processing patient {p.patient_id}: {e}")
            parsed_data = [str(p.patient_id), "Error", "Error", "Error", "Error", "Error"]
        all_parsed_data.append(parsed_data)
    df = pd.DataFrame(all_parsed_data, columns=['Patient ID', 'Status', 'Quality BP', 'Note BPs', 'Note Date', 'Success'])
    df.to_csv("output.csv", index=False)
    print(f"BP data successfully converted and saved to 'output.csv'")
    driver.quit()
        