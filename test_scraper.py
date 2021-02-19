import requests
import time
import json


APIKEY = "faa0b3cb4ae90aba340567484b057e59c72b1a37"
NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"


def main():

    while True:

        try:
            print("working")
            r = requests.get(STATIONS, params={"apiKey": APIKEY, "contract": NAME})
            x = json.loads(r.text)
            json = json.dumps(x)
            f = open("testloop2.json", "w")
            f.write(json)
            f.close()
            print(x)
            time.sleep(5 * 60)

        except:
            print("not connecting...nooooo")


main()
