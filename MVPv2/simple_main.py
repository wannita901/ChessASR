# Command line interface
import time
import os
import subprocess
import json
from ChessWrapper import ChessWrapper

class Pipe(object):
    class __Inner(object):
        def __init__(self):
            self.state = 0
            self.isRunning = False
            self.round = 1
            self.result = []
            self.Chess = ChessWrapper()
            print("[Opening Chess Game...]")
            self.Chess.open_game()

        def record(self):
            self.state = 1
            self.isRunnung = True
            os.system("python record.py")
            # _ = subprocess.check_output("python record.py", shell=True) # record out.wav
            self.state = 2
            self.isRunning = False

        def processing(self):
            self.state = 3
            self.isRunning = True
            # time.sleep(3) # mock upload to docker
            cmd = "python2.7 client.py -u ws://localhost:8080/client/ws/speech -r 32000 out.wav".split(" ")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            out = p.stdout.read()
            data = self.parseData(out.decode("utf-8"))
            print("data: {}".format(data))
            self.state = 4
            self.isRunning = False

        def parseData(self, str_m):
            print("Parse Data!")
            responses = (str_m.split("}{"))
            data = []
            for idx, response in enumerate(responses):
                if idx == 0:
                    response += "}"
                elif idx == len(responses) - 1:
                    response = "{" + response
                else:
                    response = "{" + response + "}"
                if len(response) == 0:
                    continue
                try:
                    response = json.loads(str(response))
                except:
                    # try:
                    #     print("Outer: {}".format(response.decode('unicode_escape')))
                    # except:
                    #     print("Outer 2: {}".format(response))
                    continue
                if response['status'] == 0:
                    if 'result' in response:
                        trans = response['result']['hypotheses'][0]['transcript']
                        if response['result']['final']:
                            # print("Done: {}".format(trans.replace("\n", "\\n")))
                            data.append(trans.replace("\n", "\\n")[:-1])
                        else:
                            print_trans = trans.replace("\n", "\\n")[:-1]
                            data.append(print_trans)
                            if len(print_trans) > 80:
                                print_trans = "... %s" % print_trans[-76:]
                            # print("Almost: {}".format(print_trans))
                else:
                    print("Received error from server (status %d)" % response['status'])
                    if 'message' in response:
                        print("Error message: {}".format(response['message']))
            return data

        def mock_playing(self):
            tmp = {
                1: ["b2", "b3"],
                2: ["c2", "c3"],
                3: ["d2", "d3"],
                4: ["e2", "e3"]
            }
            self.result = tmp[self.round]
            self.playing(*self.result)
        
        def playing(self, a, b):
            self.state = 5
            self.isRunning = True
            self.Chess.white_move(a, b)
            self.state = 0
            self.isRunning = False

        def addRound(self):
            self.round += 1
    
    # Singleton
    instance = None
    def __init__(self, *args, **kwargs):
        if not Pipe.instance:
            Pipe.instance = Pipe.__Inner(*args, **kwargs)
        else:
            Pipe.instance.val = args
    def __getattr__(self, name):
        return getattr(self.instance, name)

if __name__ == '__main__':
    pipeline = Pipe()
    isDebug = True
    print("[Initializing...]")
    count = 0
    print("[Round {}]".format(pipeline.round))
    while True:
        print("{}\t[Recording...]".format(pipeline.round))
        pipeline.record()
        print("{}\t[Processing...]".format(pipeline.round))
        pipeline.processing()
        print("{}\t[Playing...]".format(pipeline.round))
        if isDebug:
            pipeline.mock_playing()
        else:
            pipeline.playing()
        pipeline.addRound()
        print("[Round {}]".format(pipeline.round))
        if isDebug and count >= 2:
            break
        if isDebug:
            count += 1