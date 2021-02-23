# Scraping from the JCDecaux website

import requests
import time

APIKEY = ""
NAME = "Dublin"
STATIONS = "https://api.jcdecaux.com/vls/v1/stations"


def main():

    while True:
        import json

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
