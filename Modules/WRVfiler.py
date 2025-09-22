try:
    if not __name__ == "__main__":
        from Modules.dependencies import *
        from Modules.canopyopener import *
    else:
        from dependencies import *
        from canopyopener import *
except ImportError:
    print("Error: Could not import required modules.")
    exit(1)


'''
HealthIX	Blue Button	Quest	LHR 	WV Medical Records 	Lab Actions
CIS missing access,No BB,CIS Missing Access,No records found in EMR ,Requested all records,Completed Labs,
'''






def WRVfilermain():
    MRN_list=numbers_to_list()
    for MRN in MRN_list:
        Healthix="CIS missing access"
        BlueButton="No BB"
        Quest="CIS Missing Access"
        LHR="No records found in EMR"
        WVMedicalRecords="Requested all records"
        LabActions="Completed Labs"
        line = (f"{Healthix}, {BlueButton}, {Quest}, {LHR}, {WVMedicalRecords}, {LabActions}\n")
        list.append(line)   
    pd.DataFrame(list, columns=["HealthIX", "Blue Button", "Quest", "LHR", "WV Medical Records", "Lab Actions"]).to_csv(f"WRVS_{datetime.today().strftime('%Y-%m-%d')}.csv", index=False)

if __name__ == "__main__":
    WRVfilermain()