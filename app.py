import getpass, datetime, os, sys, time, base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
baseFolder = "notes/"

logo = "\033[35m   ________    _  __     __        \n  / __/ __/___/ |/ /__  / /____ ___\n _\ \/ _//___/    / _ \/ __/ -_|_-<\n/___/_/     /_/|_/\___/\__/\__/___/\n\n\033[0m"
outlineHeight = 8
outlineWidth = 2

class _Getch:
    def __init__(self):
        try: self.impl = _GetchWindows()
        except ImportError: self.impl = _GetchUnix()
    def __call__(self): return self.impl()
class _GetchUnix:
    def __init__(self): import tty, sys
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode("UTF-8")
class _GetchWindows:
    def __init__(self): import msvcrt
    def __call__(self):
        import msvcrt
        return msvcrt.getch()
getch = _Getch()

if sys.platform == "win32":
    import subprocess
    subprocess.run("", shell=True) #to fix a bug with windows

def drawMenu(content,subText):
    termSize = os.get_terminal_size()
    contentLines = content.split("\n")
    contentLines += [""]*(termSize.lines-outlineHeight-len(contentLines))
    output = logo+"╔"+"═"*(termSize.columns-2)+"╗\n"
    for i in range(min(len(contentLines),termSize.lines-outlineHeight)):
        if i < termSize.lines-outlineHeight-1 or len(contentLines) < termSize.lines-outlineHeight+1: temp = "║ "+contentLines[i]
        else: temp = "║ ..."
        if len(temp) > termSize.columns - outlineWidth: temp = temp[:-(len(temp)-(termSize.columns-outlineWidth)+3)]+"..."
        elif len(temp) < termSize.columns - outlineWidth: temp += " "*(termSize.columns-outlineWidth-len(temp))
        output += temp+" ║\n"
    output += "╚"+"═"*(termSize.columns-2)+"╝\n"+subText+"\033[?25l"
    sys.stdout.write("\033c"+output)

def getChoice(choices, text):
    scroll = 0
    cursor = 0
    going = True
    while going:
        termSize = os.get_terminal_size()

        display = text+"\n"
        for i in range(scroll,min(len(choices),termSize.lines-outlineHeight-2+scroll)):
            if i == cursor: display += "> "
            else: display += "  "
            display += choices[i]+"\n"
        if sys.platform == "win32": bottomTxt = "up/down/left/right enter/esc"
        else: bottomTxt = "up/down/left/right enter/backspace"
        drawMenu(display, bottomTxt)

        key = getch()
        if (sys.platform == "win32" and key == b'\x1b') or (sys.platform != "win32" and key == b'\x7f'): return -1
        elif key == b'\r': return cursor
        elif key == b'\x00' or key == b'\xe0' or key == b'\x1b':
            key2 = getch()
            if key2 == b'[': key3 = getch()
            else: key3 = ""
            if key2 == b'H' or key3 == b'A':
                cursor = max(0,cursor-1)
                if cursor < scroll: scroll = max(0,scroll-1)
            elif key2 == b'P' or key3 == b'B':
                cursor = min(cursor+1,len(choices)-1)
                if cursor-scroll > termSize.lines-outlineHeight-3: scroll = min(scroll+1,len(choices)-(termSize.lines-outlineHeight)+2)
                

def genKey(passkey):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt = b"Cn\xd6\x9e'N+\xe7\x9e;\xa9Q\x18\x91`\x88",
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(passkey.encode())
    return base64.urlsafe_b64encode(key)

def encrypt(key,data):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())
def decrypt(key,data):
    fernet = Fernet(key)
    return fernet.decrypt(data).decode()

isOpen = True
while isOpen:
    choice = getChoice(os.listdir(baseFolder),"pick folder:")
    if choice == -1: isOpen = False
    else:
        currentFolder = os.listdir(baseFolder)[choice]
        folder = baseFolder+currentFolder+"/"

        drawMenu("password: ","type password (you cant see)")
        Pass = genKey(getpass.getpass(""))

        inFolder = True
        while inFolder:
            files = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
            #files = os.listdir(folder)
            today = datetime.datetime.now()
            name = today.strftime("%m-%d-%y.txt")
            time = today.strftime("--%b/%d/%y %I:%M %p--")

            option = getChoice(["write","read","edit","read all"],"choose an option:")

            if option == 0:
                choice = getChoice(["yes","no"],"would you like to add todays date in file name?")
                if choice == 1:
                    drawMenu("type the file name.","name> ")
                    name = sys.stdin.readline()+".txt"

                choice = getChoice(["yes","no"],"would you like to add date and time in file?")
                if choice == 0: output = time
                else: output = ""
                
                print("\033[? 25h\033c")
                if name in files:
                    print("continuing file...")
                    output = decrypt(Pass, open(folder+name, "rb").read()) + "\n\n" + output
                else: print("creating new file...")

                with open(folder+name, "wb") as f:
                    print(output)
                    output = output+"\n"+input("write: ")
                    f.write(encrypt(Pass, output))
                drawMenu('saved.',"press enter to continue...")
                input()

            elif option == 1:
                name = files[getChoice(files,"choose a file to read:")]
                if sys.platform == "win32": os.system("cls")
                else: os.system("clear")
                print(decrypt(Pass, open(folder+name, "rb").read()))
                input("\npress enter to continue...")

            elif option == 2:
                name = files[getChoice(files,"choose a file to edit:")]

                with open(folder+name, "rb") as f:
                    data = decrypt(Pass, f.read())
                with open(baseFolder+"temp.txt","w") as f :
                    f.write(data)

                if sys.platform == "win32":
                    drawMenu('openned a text editor save and close when done.',"close notepad when done.")
                    os.system("notepad.exe "+baseFolder+"temp.txt")
                else:
                    drawMenu("go to "+baseFolder+"temp.txt to edit file\npress enter when done.","press enter when done...")
                    os.system("nano "+baseFolder+"temp.txt")

                with open(baseFolder+"temp.txt", "r") as f:
                    output = f.read()
                with open(folder+name, "wb") as f:
                    f.write(encrypt(Pass, output))
                os.remove(baseFolder+"temp.txt")

                drawMenu('saved.',"press enter to continue...")
                input()

            elif option == 3:
                if sys.platform == "win32": os.system("cls")
                else: os.system("clear")
                for i in range(len(files)):
                    print(decrypt(Pass, open(folder+files[i], "rb").read()))
                input("\npress enter to continue...")
            
            elif option == -1: inFolder = False
