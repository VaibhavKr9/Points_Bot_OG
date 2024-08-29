import subprocess
import argparse

def getArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--branch", default="main")
    parser.add_argument("-f","--file", default="main.py")
    return parser.parse_args()

if __name__ == "__main__":
    args : argparse.Namespace = getArgs()

    subprocess.run(["git","fetch"])
    subprocess.run(["git","checkout","-f","origin/" + args.branch])
    subprocess.run(["python",args.file])