import json
import random

try:  # For python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:  # For python 2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

ACTIONS = ["move", "eat", "load", "unload"]
DIRECTIONS = ["up", "down", "right", "left"]


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        payload = self.rfile.read(int(self.headers['Content-Length']))

        # Hive object from request payload
        hive = json.loads(payload)
        
        print(hive, file=open("log.txt", "a")) #Make log file
        
        # Loop through ants and give orders
        orders = {}
        # HERE I FIND HIVE'S LIMITS'
        hivexmax = -1
        hiveymax = -1
        hivexmin = -1
        hiveymin = -1

        for i in range (hive['map']['width']):
            for d in range(hive['map']['height']):
                if hive['map']['cells'][i][d]['hive'] == hive['id']:
                    hivexmin = hive['map']['cells'][i]
                    hiveymin = hive['map']['cells'][i][d]
                    break
        for i in reversed(hive['map']['width']):
            for d in reversed(hive['map']['height']):
                if hive['map']['cells'][i][d]['hive'] == hive['id']:
                    hivexmax = hive['map']['cells'][i]
                    hiveymax = hive['map']['cells'][i][d]

        for ant in range (hive['ants']):
            if hive['ants'][ant]['health'] < 9:
                orders[ant] = {
                    "act": ACTIONS['eat'],
                    "dir": DIRECTIONS['left']
                }

            if hive['ants'][ant]['event'] != 'death':
                x = hive['ants'][ant]['x']
                y = hive['ants'][ant]['y']

                #ЧАСТЬ, В КОТОРОЙ МЫ ПОЛНОСТЬЮ ЗАБИТОГО МУРАВЬЯ ВЕДЕМ В УЛЕЙ.
                if hive['ants'][ant]['payload'] == 9:
                    if x>=hivexmin and x<=hivexmax:
                        if y+1<hiveymin:

                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['down']
                            }
                        elif y-1>hiveymax:

                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['up']
                            }
                        elif y+1 == hiveymin:

                            orders[ant] = {
                                "act": ACTIONS['unload'],
                                "dir": DIRECTIONS['down']
                            }
                        elif y-1 == hiveymax:

                            orders[ant] = {
                                "act": ACTIONS['unload'],
                                "dir": DIRECTIONS['up']
                            }
                    elif y>=hiveymin and x<=hiveymax:
                        if x+1<hivexmin:

                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['right']
                            }
                        elif x-1>hivexmax:

                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['left']
                            }
                        elif x+1 == hivexmin:

                            orders[ant] = {
                                "act": ACTIONS['unload'],
                                "dir": DIRECTIONS['right']
                            }
                        elif x-1 == hivexmax:

                            orders[ant] = {
                                "act": ACTIONS['unload'],
                                "dir": DIRECTIONS['left']
                            }
                    else:
                        if x<hivexmin:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['right']
                            }
                        if x>hivexmax:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['left']
                            }

                #ЧАСТЬ, В КОТОРОЙ МУРАВЕЙ ИЩЕТ ЕДУ
                else:
                    #ЕСЛИ ЕДА В НЕПОСРЕДСТВЕННОЙ БЛИЗОСТИ ОТ МУРАВЬЯ
                    if (hive['map']['cells'][x-1][y]['food'] > 0 ):
                        orders[ant] = {
                            "act": ACTIONS['load'],
                            "dir": DIRECTIONS['left']
                        }
                    elif(hive['map']['cells'][x+1][y]['food'] > 0 ):
                        orders[ant] = {
                            "act": ACTIONS['load'],
                            "dir": DIRECTIONS['right']
                        }
                    elif(hive['map']['cells'][x][y-1]['food'] > 0 ):
                        orders[ant] = {
                            "act": ACTIONS['load'],
                            "dir": DIRECTIONS['up']
                        }
                    elif(hive['map']['cells'][x][y+1]['food'] > 0 ):
                        orders[ant] = {
                            "act": ACTIONS['load'],
                            "dir": DIRECTIONS['down']
                        }
                    else:
                        #ЕСЛИ ЕДА ДАЛЬШЕ ОТ МУРАВЬЯ, НЕЖЕЛИ СОВСЕМ РЯДОМ
                        koth = [10000000,10000000]
                        for i in range [hive['map']['width']]:
                            for d in range [hive['map']['height']]:
                                try:
                                    if ['map']['cells'][i][d]['food'] >0:

                                        if  abs(hive['ants'][ant][x] - i) < abs(hive['ants'][ant][x] - koth[0]):
                                            koth[0] = i

                                        if  abs(hive['ants'][ant][y] - d) < abs(hive['ants'][ant][y] - koth[1]):
                                            koth[1] = d

                                except:
                                    continue
                        if hive['ants'][ant][x] > koth[0]:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['right']
                            }
                        elif hive['ants'][ant][x] < koth[0]:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['left']
                            }
                        elif hive['ants'][ant][y] < koth[1]:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['down']
                            }
                        elif hive['ants'][ant][y] > koth[1]:
                            orders[ant] = {
                                "act": ACTIONS['move'],
                                "dir": DIRECTIONS['up']
                            }
        response = json.dumps(orders)
        print(response)

        try:  # For python 3
            out = bytes(response, "utf8")
        except TypeError:  # For python 2
            out = bytes(response)

        self.wfile.write(out)

        # json format sample:
        # {"1":{"act":"load","dir":"down"},"17":{"act":"load","dir":"up"}}
        return


def run():
    server_address = ('0.0.0.0', 7070)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


run()
