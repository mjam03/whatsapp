import re
from zipfile import ZipFile


def extract_whatsapp_zip(input_zip):
    """ Accepts str filepath to whatsapp export zip and returns the chat

    Args:
        input_zip (str): string filepath to the WhatsApp export

    Returns:
        str: string of the WhatsApp chat
    """
    # convert whatsapp zip file to text
    input_zip = ZipFile(input_zip)
    cont_dict = {name: input_zip.read(name) for name in input_zip.namelist()}
    # get the chat from the extracted zip
    chat = cont_dict['_chat.txt']
    # decode the chat
    chat = chat.decode('utf-8')
    return chat


def starts_with_auth(s):
    """Checks is string s starts with standard name type

    Args:
        s (str): WhatsApp message string

    Returns:
        bool: True if matches regex for name, False if not
    """
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


def convert_chat_to_list(chat):
    """Converts str whatsapp chat to list of str using regex to identify date. Date is of format '[18/06/17, 22:47:15]'


    Args:
        chat (str): WhatsApp string chat

    Returns:
        list: list of msg strings where they have been split by date regex
    """
    # wa timestamps all messages - use that to separate
    WA_DATETIME_FMT = r'\[([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)(\d{2}|\d{4}), ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])\]'
    # form start and end str indices of all messages
    msg_starts = [m.start() for m in re.finditer(WA_DATETIME_FMT, chat)]
    msg_ends = msg_starts[1:]
    msg_ends.append(len(chat))
    # use these to get messages as list of strings
    msgs = [chat[x:y] for x, y in zip(msg_starts, msg_ends)]
    return msgs


def parse_msg(mess):
    """parse a given WhatsApp message to form list of date, time, author, message

    Args:
        mess (str): WhatsApp msg string (including date and time)

    Returns:
        list: returns msg element-wise of date, time, author, message all as str
    """
    # first replace \n with ' ' for multi-line msg
    # and strip of funny whitespace
    mess = mess.replace('\n', ' ').replace('\r', '').strip()
    # split of date and time at start of mess
    msg_split = mess.split('] ')
    # fetch the date time and parse
    date_time = msg_split[0][1:]  # date_time = '18/06/17, 22:47:15'
    date, time = date_time.split(', ')  # date = '18/06/17'; time = '22:47:15'
    # store rest of mess as str again
    message = ' '.join(msg_split[1:])
    author = None

    # check if dt-stripped message starts with auth name
    if ":" in message:
        if starts_with_auth(message):
            # split before and after auth
            split_mess = message.split(': ')
            author = split_mess[0]
            message = ' '.join(split_mess[1:])
    else:
        # else issue so split by ' '
        sub_m = message.split(' ')
        # assume auth is first 2 words
        author = " ".join(sub_m[:2])

    # remove funny char from author
    author = author.replace('\u200e', '')
    return date, time, author, message


def parse_chat(chat):
    """Parses one long WhatsApp chat string into list of lists of strings of date, time, author, message

    Args:
        chat (str): WhatsApp exported chat string

    Returns:
        list: list of lists of date, time, author, message all as strings
    """
    # parse chat str to list of str split by datetime stamp
    chat_list = convert_chat_to_list(chat)
    # first message is always creation message - remove
    chat_list = chat_list[1:]
    # iterate through messages and parse into list of 4
    msg_list = []
    for msg in chat_list:
        date, time, author, message = parse_msg(msg)
        msg_list.append([date, time, author, message])
    return msg_list


def extract_and_parse_whatsapp(fp):
    """Wrapper function to extract chat from str filepath to WhatsApp .zip export then parse

    Args:
        fp (str): filepath to WhatsApp exported .zip file

    Returns:
        list: list of msgs where each msg is a list of str: date, time, author, message
    """
    # extract chat from zip
    chat = extract_whatsapp_zip(fp)
    # parse chat into list of lists
    parsed_chat = parse_chat(chat)
    return parsed_chat


if __name__ == '__main__':
    print('Running...')
