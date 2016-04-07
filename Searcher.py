#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import sys;
import subprocess;
import shlex;
from os import system
from time import strftime
from time import sleep

pathToScript = "/Users/tbTennyson/User Documents/Computer/Called Upon/CodeSystem/Searcher/"; # must have / at end
whiteListName = "whitelist.txt";
blackListName = "blacklist.txt";
logName = "log.txt"
displayName = "filesToDisplay/" # must have / at end

whiteFiles = '';
blackFiles = '';
with open(pathToScript+whiteListName) as f:
    whiteFiles = f.read().splitlines();
with open(pathToScript+blackListName) as f:
    blackFiles = f.read().splitlines();
# print(blackFiles);

def log(string):
    with open(pathToScript+logName, "a") as f:
        f.write(strftime("%Y-%m-%d %H,%M,%S") + string + "\n")

def triggerCommandC():
     system('osascript -e \'tell application "System Events" to keystroke "c" using {command down}\'');

def triggerCommandW():
     system('osascript -e \'tell application "System Events" to keystroke "w" using {command down}\'');

def getClipboardData():
    p = subprocess.check_output("pbpaste");
    return p;

def decodeClipboardData(data):
    return data.decode("utf-8");

def setClipboardData(data):
    # http://www.macdrifter.com/2011/12/python-and-the-mac-clipboard.html
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    retcode = p.wait()

def getFilesFrom(filesStr):
    # filesStr is a string with multiple files each separated with a newline.
    # This must return a list of files
    files = filesStr.splitlines();
    files = [x for x in files if len(x) > 0];
    return files;

def checkInDirsList(file, dirs):
    # checks if the file is in one of the dirs pass in. dirs is a list of
    # strings, and file is a string
    # print("-"+str(file)+"-");
    for d in dirs:
        if file.find(d) == 0:
            return True;
    return False;

def openFile(file):
    # opens the file for the user
    # print(file)
    p = subprocess.run(shlex.split('open "'+file+'"'));

def displayFiles(files):
    # puts every files in a list into a textfiles and displays it to the user
    path = pathToScript+displayName+"results-"+strftime("%Y-%m-%d %H,%M,%S")+".txt";
    file = open(path,"w");
    s = '';
    for f in files:
        s = s + f + '\n';
    file.write(s);
    file.close()
    openFile(path);

def search(quary):
    p = subprocess.check_output(shlex.split("mdfind "+"'"+quary+"'"));
    output = p.decode("utf-8"); 
    files = getFilesFrom(output);
    if len(files) == 0:
        x = "No files found for quary: "+quary
        log(x)
        displayFiles([x])
        return;
    if len(files) == 1:
        openFile(files[0])
    # print("all: " +str(files));
    files = [x for x in files if not checkInDirsList(x, blackFiles)];
    # print("no black: "+str(files));
    white = [x for x in files if checkInDirsList(x, whiteFiles)];
    # return;
    # print("white: " + str(white));
    if len(white) > 0:
        if len(white) == 1:
            openFile(white[0]);
        else:
            openFile(white);
    elif len(files) > 0:
        if len(files) == 1:
            openFile(files[0]);
        else:
            displayFiles(files);

if __name__=='__main__':
    doClose = False;
    for arg in sys.argv:
        if arg == "doClose":
            doClose = True;
    before = getClipboardData();
    triggerCommandC();
    after = getClipboardData();
    i = 0;
    while (after == before && len(before) != 20):
        triggerCommandC();
        after = getClipboardData();
        sleep(.3);
        i += 1;
        if (i > 4):
            break;
    decodeAfter = decodeClipboardData(after);
    triggerCommandW();
    search('#'+decodeAfter);
    setClipboardData(before);

