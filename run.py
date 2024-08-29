import subprocess
import argparse

def parserInit() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--branch", default="main")
    parser.add_argument("-f","--file", default="main.py")

if __name__ == "__main__":
    parser : argparse.ArgumentParser = parserInit()

    subprocess.run(["git","checkout","-f","origin/" + parser.branch])
    subprocess.run(["python",parser.file])