class HMDEntry:
    # pid = process id, tid = thread id
    def __init__(self, pid, tid, data, timestamp):
        self.pid = pid
        self.tid = tid
        self.data = data
        self.timestamp = timestamp