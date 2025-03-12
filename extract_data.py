from HMDEntry import HMDEntry
from SysmonEntry import SysmonEntry
from OculusEntry import OculusEntry
from datetime import datetime


def extractData():
    
    #reading the logcat file in utf-16 format, contains all HMD logs (logcat, openxr api logs are redirected to logcat as well, and application logs are defaulted to appear in logcat)
    with open('Logs/hmd.txt', 'r', encoding='utf-16', errors='ignore') as f1:
        hmd_lines = f1.readlines()

    #reading the sysmon file
    with open('Logs/sysmon.txt', 'r', encoding='utf-8-sig', errors='ignore') as f2:
        sysmon_lines = f2.readlines()

    with open('Logs/oculuslog.txt', 'r', encoding='utf-8-sig', errors='ignore') as f3:
        oculus_lines = f3.readlines()
    
    #removing tags from HMD logs
    count = 0 #counter to ensure that the list index doesn't go out of range
    while count < len(hmd_lines):
        if hmd_lines[count][1:3] == "--":
            hmd_lines.pop(count)
        count += 1
    
    # initialize array for storing HMD log entries
    hmd_entries = []

    # loop through each line of HMD, storing appropriate information in hmd_entries array
    for i in range(0,len(hmd_lines)):
        pid = hmd_lines[i][19:24].strip()
        tid = hmd_lines[i][25:30].strip()
        data = hmd_lines[i][33:].strip()
        timestamp = hmd_lines[i][6:19].strip()
        hmd_entries.append(HMDEntry(pid, tid, data, timestamp))

    # initialize array for storing sysmon log entries
    sysmon_entries = []

    #cycle through all lines in sysmon log
    for j in range (0, len(sysmon_lines)):
        #if information log entry (relevant data)
        if (sysmon_lines[j][:11] == 'Information'):
            #extract event id, timestamp and pid
            event_id = int(sysmon_lines[j].split()[5])
            timestamp = sysmon_lines[j+2][-13:].strip()
            pid = sysmon_lines[j+4][-6:].strip()
            # event ids: 1 = process create, 3 = network connection, 11 = file created
            # only process create nodes have a parent process id
            if event_id == 1:
                ppid = sysmon_lines[j+20][-6:].strip()
            else:
                ppid = None
            #extract process details and name
            process_details = sysmon_lines[j+5].strip().split('\\')
            process_name = process_details[len(process_details)-1]
            # check for event types to extract relevant parts of string for data
            if event_id == 1:
                data = sysmon_lines[j+11][13:].strip()
            elif event_id == 3:
                data = sysmon_lines[j+15].split()[1]
            elif event_id == 11:
                data = sysmon_lines[j+6].split('\\')[-1]
            else:
                data = "None"
            sysmon_entries.append(SysmonEntry(timestamp, pid, ppid, process_name, data, event_id))

    oculus_entries = []

    k = 0
    for line in oculus_lines:
        if "oculus_etw_usb_event" in line:
            parts = line.split()
            if len(parts) < 2:
                continue
            
            timestamp_candidate = parts[1]
            data = parts[-1]
            
            try:
                datetime.strptime(timestamp_candidate, "%H:%M:%S.%f")
                oculus_entries.append(OculusEntry(timestamp_candidate, data))
            except ValueError:
                pass


    # return arrays containing HMD and sysmon log data
    return hmd_entries, sysmon_entries, oculus_entries


def displayUniquehmd_pids(hmd_pids):
    #check for unique hmd_pids
    unique_hmd_pids = set(hmd_pids)
    print(list(unique_hmd_pids))
