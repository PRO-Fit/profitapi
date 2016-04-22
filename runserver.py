# from argparse import ArgumentParser
from app.api import *
if __name__ == "__main__":
    app.run()

# parser = ArgumentParser(description="Profit Bakend APIs")
# parser.add_argument("-p", "--port", default=5000, dest="port", type=int, help="Port to run on")
# args = parser.parse_args()
#
# app.run(host='0.0.0.0', debug=True, port=args.port)
