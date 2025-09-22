if not __name__ == "__main__":
    from Modules.dependencies import *
else:
    from dependencies import *

def parse_appointment_data(data_string):
    """
    Parses a multiline string containing appointment information
    and extracts time, name (last two words), and ID.

    Args:
        data_string (str): The raw text data of appointments.

    Returns:
        list of dict: A list where each dictionary represents an appointment
                      with 'Time', 'Name', and 'ID' keys.
    """
    appointments = []
    plain_text_list=""
    # Regular expression to find blocks of appointment data based on time
    appointment_blocks = re.split(r'(\d{1,2}:\d{2}\s(?:AM|PM))', data_string)

    for i in range(1, len(appointment_blocks), 2):
        time_str = appointment_blocks[i].strip()
        content_str = appointment_blocks[i+1].strip()

        # Regular expression to find the name and ID within the content block.
        # It looks for any characters (including newlines and leading/trailing spaces around the ID)
        # that are not part of a "time" pattern, followed by a name, then the ID in parentheses.
        name_id_match = re.search(r'([\w\s\.]+?)\s*\((\d+)\)', content_str, re.DOTALL)

        if name_id_match:
            full_extracted_name = name_id_match.group(1).strip().replace('\n', ' ')

            # --- NEW LOGIC TO GET ONLY THE LAST TWO WORDS OF THE NAME ---
            # Split the name by spaces and filter out empty strings
            name_parts = [part for part in full_extracted_name.split(' ') if part]

            # Special handling for "Pooja Jaisingh..." if it's at the beginning of the extracted name
            if name_parts and name_parts[0] == 'Pooja' and len(name_parts) > 1 and name_parts[1].startswith('Jaisingh'):
                # If "Pooja Jaisingh..." is detected, we'll try to find the actual patient name after it.
                # This is a heuristic based on your provided data structure.
                # We'll skip "Pooja Jaisingh..." and then take the last two words.
                # Find the index where the actual patient name likely starts
                try:
                    jaisingh_index = name_parts.index('Jaisingh...') # Adjust if 'Jaisingh' only
                    if jaisingh_index + 1 < len(name_parts):
                        name_parts = name_parts[jaisingh_index + 1:] # Slice from after "Jaisingh..."
                    else:
                        name_parts = [] # No patient name found after "Pooja Jaisingh..."
                except ValueError:
                    # 'Jaisingh...' not found, proceed with original name_parts
                    pass

            # If after cleanup, there are still parts, take the last two
            if len(name_parts) >= 2:
                final_name = ' '.join(name_parts[-2:])
            elif len(name_parts) == 1:
                final_name = name_parts[0]
            else:
                final_name = "" # No valid name parts found

            # Clean up the name for common suffixes/ellipses if they are the last "words"
            # This is done *after* taking the last two words to ensure they aren't incorrectly included
            if final_name.lower().endswith('sr'):
                final_name = final_name[:-2].strip() + ' SR'
            if final_name.endswith('...'):
                final_name = final_name[:-3].strip()

            patient_id = name_id_match.group(2).strip()

            appointments.append({
                'Time': time_str,
                'Name': final_name,
                'ID': patient_id
            })
    plain_text_list = "\n- [ ] ".join([f"{appt['Time']} - {appt['Name']} (ID: {appt['ID']})" for appt in appointments])
    plain_text_list = "- [ ] " + plain_text_list
    pyperclip.copy(plain_text_list)
    print("Debug: Parsed appointment data:\n" + plain_text_list)
    return appointments

def convert_to_spreadsheet(data_string, output_filename="appointments.csv"):
    """
    Converts raw appointment data into a CSV spreadsheet.

    Args:
        data_string (str): The raw text data of appointments.
        output_filename (str): The name of the CSV file to save.
    """
    parsed_data = parse_appointment_data(data_string)

    if not parsed_data:
        print("No appointment data found to process.")
        return

    df = pd.DataFrame(parsed_data)
    df.to_csv(output_filename, index=False)
    print(f"Appointment data successfully converted and saved to '{output_filename}'")




# --- Example Usage ---
if __name__ == "__main__":
    raw_data = simpledialog.askstring("Input", "Please enter the appointment data:")
    convert_to_spreadsheet(raw_data)