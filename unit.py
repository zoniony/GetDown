from datetime import datetime

def logger(text: str):
    time = datetime.fromtimestamp(int(datetime.now().timestamp())).isoformat()
    print(time, '\t', text)
