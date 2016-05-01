#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
"""A module that is designed to search a mac for a code that is currently
selected by the user"""
import sys
import subprocess
import shlex
from os import system
from time import strftime
from time import sleep

PATH_TO_SCRIPT = "/Users/tbTennyson/UserDocuments/Computer/CalledUpon/" +\
    "CodeSystem/Searcher/"
# must have / at end
WHITE_LIST_NAME = "whitelist.txt"
BLACK_LIST_NAME = "blacklist.txt"
LOG_NAME = "log.txt"
DISPLAY_NAME = "filesToDisplay/"  # must have / at end

WHITE_FILES = ''
BLACK_FILES = ''
with open(PATH_TO_SCRIPT + WHITE_LIST_NAME) as f:
    WHITE_FILES = f.read().splitlines()
with open(PATH_TO_SCRIPT + BLACK_LIST_NAME) as f:
    BLACK_FILES = f.read().splitlines()
# print(BLACK_FILES);


def log(string: str):
    """saves the string to the log file"""
    with open(PATH_TO_SCRIPT + LOG_NAME, "a") as f:
        f.write(strftime("%Y-%m-%d %H,%M,%S: ") + string + "\n")


def triggerCommandC():
    """triggers coppy command"""
    system(
        'osascript -e \'tell application "System Events" to keystroke "c"' +
        ' using {command down}\'')


def triggerCommandW():
    system(
        'osascript -e \'tell application "System Events" to keystroke "w"' +
        ' using {command down}\'')


def setClipboardData(data: str):
    """found at
    http://www.macdrifter.com/2011/12/python-and-the-mac-clipboard.html"""
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    p.wait()


def getFilesFrom(filesStr: str) -> list:
    """filesStr is a string with multiple files each separated with a newline.
         This must return a list of files"""
    files = filesStr.splitlines()
    files = [x for x in files if len(x) > 0]
    return files


def checkInDirsList(file: str, dirs: list) -> bool:
    """checks if the file is in one of the dirs pass in. dirs is a list of
                strings, and file is a string
                print("-"+str(file)+"-");"""
    for d in dirs:
        if file.find(d) == 0:
            return True
    return False


def openFile(file: str):
    """opens the file for the user"""
    # print(file)
    subprocess.run(shlex.split('open "' + file + '"'))


def displayFiles(files: list):
    """puts every files in a list into a textfiles and displays it to the
    user"""
    path = PATH_TO_SCRIPT + DISPLAY_NAME + "results-" + \
        strftime("%Y-%m-%d %H,%M,%S") + ".txt"
    file = open(path, "w")
    s = ''
    for f in files:
        s = s + f + '\n'
    file.write(s)
    file.close()
    openFile(path)


def search(quary: str) -> list:
    p = subprocess.check_output(shlex.split("mdfind " + "'" + quary + "'"))
    output = p.decode("utf-8")
    files = getFilesFrom(output)
    if len(files) == 0:
        #literally the dumbest hack ever, it returns 2 things so it will
        #get handeled by displayFiles
        x = "No files found for quary:\n" + quary
        log(x)
        displayFiles([x])
        return
    if len(files) == 1:
        openFile(files[0])
    # print("all: " +str(files));
    files = [x for x in files if not checkInDirsList(x, BLACK_FILES)]
    # print("no black: "+str(files));
    white = [x for x in files if checkInDirsList(x, WHITE_FILES)]
    # return;
    # print("white: " + str(white));
    if len(white) > 0:
        return white
    elif len(files) > 0:
        if len(files) == 1:
            return files
        else:
            shortest = files[0]
            for f in files:
                if len(f) < len(shortest):
                    shortest = f
            subset = True  # true if all are a subpath of the shortest path
            for f in files:
                if f.find(shortest) == -1:
                    break
            if subset:
                return shortest
            else:
                return files


def getClipbard():
    return subprocess.check_output("pbpaste")


def getDecodeClipboard() -> str:
    return getClipbard().decode("utf-8")


def smartGetClipboard() -> str:
    """Gets (and restores the cliboard) the currently selected text"""
    before = getClipbard()
    triggerCommandC()
    sleep(.05)
    after = getDecodeClipboard()
    i = 0
    while after == before and len(before) != 15:
        log(str(len(after)))
        triggerCommandC()
        after = getDecodeClipboard()
        sleep(.3)
        i += 1
        if i > 4:
            break
    setClipboardData(before)
    return after


if __name__ == '__main__':
    doClose = False
    retrurnPath = False
    doOpen = True
    searchStr = ''
    for ind, arg in enumerate(sys.argv):
        if arg == "-close":
            doClose = True
        if arg == "-path":
            retrurnPath = True
        if arg == "-noOpen":
            doOpen = False
        if arg == "-search":
            searchStr = sys.argv[ind+1]

    if len(searchStr) == 0:
        searchStr = smartGetClipboard()

    if doClose:
        triggerCommandW()

    files = search('#' + searchStr)
    if doOpen:
        if len(files) == 1:
            openFile(files[0])
        else:
            displayFiles(files)

    if retrurnPath:
        for i, f in enumerate(files):
            print(f)
