import getpass, datetime, os, sys, time
baseFolder = "C:/Users/mail/Desktop/random shi/pyFiles/"

letters = [" ","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M","q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m","1","2","3","4","5","6","7","8","9","0","!","@","#","$","%","^","&","*","(",")","-","_","=","+","[","]","{","}",":",";","'",'"',",",".","/","<",">","?","|", "\n"]


logo = "\033[35m   ________    _  __     __        \n  / __/ __/___/ |/ /__  / /____ ___\n _\ \/ _//___/    / _ \/ __/ -_|_-<\n/___/_/     /_/|_/\___/\__/\__/___/\n\n\033[0m"
outlineHeight = 8
outlineWidth = 2

class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

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
        drawMenu(display,"up/down/left/right enter/esc")

        key = getch()
        if key == b'\x1b': return -1
        elif key == b'\r': return cursor
        elif key == b'\x00' or key == b'\xe0':
            key2 = getch()
            if key2 == b'H':
                cursor = max(0,cursor-1)
                if cursor < scroll: scroll = max(0,scroll-1)
            elif key2 == b'P':
                cursor = min(cursor+1,len(choices)-1)
                if cursor-scroll > termSize.lines-outlineHeight-3: scroll = min(scroll+1,len(choices)-(termSize.lines-outlineHeight)+2)
                

def toNumbers(string):
    output = []
    for i in string:
        if i in letters:
            for x in range(len(letters)):
                if letters[x] == i:
                    output.append(x)
                    break
        else:
            print('warning: unrecognized character "'+i+'". skipping.')
    return(output)

def encrypt(add,multiply,message):
    nums = toNumbers(message)
    out = ""
    for num in nums:
        finalNum = (num+add)*multiply
        rollOverNum = 0
        while finalNum > len(letters)-1:
            rollOverNum += 1
            finalNum -= len(letters)-1
        out = out+str(rollOverNum)+"\\"+letters[finalNum]+"\\"
    return(out)

def decrypt(add,multiply,message):
    msg = message.split("\\")
    msg.pop(len(msg)-1)
    out = ""
    for i in range(int(len(msg)/2)):
        charNum = toNumbers(msg[i*2+1])[0]
        num = int(msg[i*2])
        charNum += (len(letters)-1)*num
        charNum /= multiply
        charNum -= add
        try: out = out+letters[int(charNum)]
        except: print(charNum)
    return(out)
    

isOpen = True
while isOpen:
    choice = getChoice(os.listdir(baseFolder),"pick folder:")
    if choice == -1: isOpen = False
    else:
        currentFolder = os.listdir(baseFolder)[choice]
        folder = baseFolder+currentFolder+"/"

        drawMenu("password: ","type password (you cant see)")
        Pass = toNumbers(getpass.getpass(""))
        add = 0
        for num in Pass:
            add += num
        drawMenu("number: ","type number (you cant see)")
        multiply = int(getpass.getpass(""))

        inFolder = True
        while inFolder:
            files = os.listdir(folder)
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
                    output = decrypt(add, multiply, open(folder+name, "r").read()) + "\n\n" + output
                else: print("creating new file...")

                with open(folder+name, "w") as f:
                    print(output)
                    output = output+"\n"+input("write: ")
                    f.write(encrypt(add, multiply, output))
                drawMenu('saved.',"press enter to continue...")
                input()

            elif option == 1:
                name = files[getChoice(files,"choose a file to read:")]
                if sys.platform == "win32": os.system("cls")
                else: os.system("clear")
                print(decrypt(add, multiply, open(folder+name, "r").read()))
                input("\npress enter to continue...")

            elif option == 2:
                name = files[getChoice(files,"choose a file to edit:")]

                with open(folder+name, "r") as f:
                    data = decrypt(add, multiply, f.read())
                with open(baseFolder+"temp.txt","w") as f :
                    f.write(data)

                if sys.platform == "win32":
                    drawMenu('openned a text editor save and close when done.',"close notepad when done.")
                    os.system("notepad.exe "+baseFolder+"temp.txt")
                else:
                    drawMenu("go to "+baseFolder+"temp.txt to edit file\npress enter when done.","press enter when done...")

                with open(baseFolder+"temp.txt", "r") as f:
                    output = f.read()
                with open(folder+name, "w") as f:
                    f.write(encrypt(add, multiply, output))
                os.remove(baseFolder+"temp.txt")

                drawMenu('saved.',"press enter to continue...")
                input()

            elif option == 3:
                if sys.platform == "win32": os.system("cls")
                else: os.system("clear")
                for i in range(len(files)):
                    print(decrypt(add, multiply, open(folder+files[i], "r").read()))
                input("\npress enter to continue...")
            
            elif option == -1: inFolder = False
