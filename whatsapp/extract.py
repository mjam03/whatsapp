import re
from zipfile import ZipFile


def extract_zip(input_zip):
    # convert whatsapp zip file to text
    input_zip = ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}


def startsWithAuthor(s):
    # checker if line starts with author and so is a valid message
    patterns = [
        r'([\w]+):',                        # 1st Name
        r'([\w]+[\s]+[\w]+):',              # 1st N + Last N
        r'([\w]+[\s]+[\w]+[\s]+[\w]+):',    # 1st N + Mid N + Last N
        r'([+]\d{1} \(\d{3}\) \d{3}-\d{4}):',  # ‪+1 (571) 324‑0857‬:
        r'([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
        r'([+]\d{2} \d{4} \d{7})'           # Mobile Number (Europe)
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


# convert a str (one line of convo) into sub-components
def getDataPoint(line):
    splitLine = line.split('] ')
    dateTime = splitLine[0][1:]  # dateTime = '18/06/17, 22:47'
    date, time = dateTime.split(', ')  # date = '18/06/17'; time = '22:47'
    message = ' '.join(splitLine[1:])
    author = None

    if ":" in message:
        if startsWithAuthor(message):  # True
            splitMessage = message.split(': ')
            author = splitMessage[0]
            message = ' '.join(splitMessage[1:])
    else:
        subM = message.split(' ')
        author = " ".join(subM[:2])
    return date, time, author, message


def startsWithDateTime(s):
    # check if starts with a time
    pattern = r'^\[([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])\]'
    result = re.match(pattern, s)
    if result or '\u200e' in s:
        return True
    return False


def parse_zip(wa_zip):
    # initialise parsed data as an empty list (to be populated)
    parsed_data = []
    convo_list = wa_zip['_chat.txt'].decode('utf-8').split('\n')

    for line in convo_list:
        line = line.strip()  # remove funny whitespaces
        line = line.replace("\u200e", "")
        if startsWithDateTime(line):  # if starts with date time then we're good to go
            date, time, author, message = getDataPoint(line)
            parsed_data.append([date, time, author, message])

    return parsed_data


if __name__ == "__main__":
    print("")
