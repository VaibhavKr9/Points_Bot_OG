import subprocess
import argparse
import threading


def run_script(script_name):
    subprocess.run(["python", script_name])


def getArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--branch", default="main")
    parser.add_argument("-ng","no-git", action='store_false', dest="git_run")
    parser.add_argument("-f","--files", nargs=2, default=["main.py", "api-caller/main.py"])
    return parser.parse_args()

if __name__ == "__main__":

    args : argparse.Namespace = getArgs()

    if(args.git_run == True):
        subprocess.run(["git","fetch"])
        subprocess.run(["git","checkout","-f","origin/" + args.branch])

    """ script1_thread = threading.Thread(target=run_script, args=(args.files[0],))
    script2_thread = threading.Thread(target=run_script, args=(args.files[1],))

    script1_thread.start()
    script2_thread.start()

    script1_thread.join()
    script2_thread.join() """

    threadList : list[threading.Thread] = []
    for script in args.files:
        threadList.append(threading.Thread(target=run_script, args=(script,)))
    
    for thread in threadList:
        thread.start()
    
    for thread in threadList:
        thread.join()