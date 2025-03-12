class SysmonEntry:
    # pid = process id, ppid = parent process id
    def __init__(self, timestamp, pid, ppid, process_name, data, event_id):
        self.timestamp = timestamp
        self.pid = pid
        self.ppid = ppid
        self.process_name = process_name
        self.data = data
        self.event_id = event_id