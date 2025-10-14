from flask import Flask
from Frontend import main

web = Flask(__name__)

@web.route('/')

def run_main():
    main()

if __name__ == "__main__":
    web.run(host="0.0.0.0", port=8000)
