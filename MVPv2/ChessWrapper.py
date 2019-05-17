import time
import osascript
# pip install osascript

open_game = """tell application "Chess" to activate
delay 5
tell application "System Events" to tell process "Chess"
    try
        set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    on error errMsg
        keystroke "l" using {{command down}}
    end try
end tell"""

on_play_move = lambda x, y: """tell application "Chess" to activate
tell application "System Events" to tell process "Chess"
    try
        set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    on error errMsg
        keystroke "l" using {{command down}}
    end try
    tell group 1 of window 1
        click button "{}"
        click button "{}"
    end tell
end tell""".format(x, y)

on_check_move = """tell application "Chess" to activate
tell application "System Events" to tell process "Chess"
    try
        set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    on error errMsg
        keystroke "l" using {{command down}}
    end try
    set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    set lastItem to item (count of items in uiElems) of uiElems
    set lastText to title of lastItem
end tell"""

on_get_all_move = """tell application "Chess" to activate
tell application "System Events" to tell process "Chess"
    try
        set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    on error errMsg
        keystroke "l" using {{command down}}
    end try
    set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    set titles to {}
    repeat with anItem in uiElems
        set end of titles to title of anItem
    end repeat
    titles
end tell"""

on_get_game_state = """tell application "Chess" to activate
tell application "System Events" to tell process "Chess"
    try
        set uiElems to entire contents of group 1 of scroll area 1 of group 1 of group 2 of window 1
    on error errMsg
        keystroke "l" using {{command down}}
    end try
    set uiElems to entire contents of group 1 of window 1
    uiElems
end tell"""

def NiceTry(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return ""
        except ValueError as text:
            return text
    return wrapper

class ChessWrapper(object):
    class __OnlyOne(object):
        def __init__(self, size=8, maxTimeout=-1):
            self.size = size
            self.game_state = [[0 for i in range(size)] for j in range(size)]
            self.chars = ["blank", "pawn", "rook", "knight", "bishop", "queen", "king"]
            self.maxTimeout = maxTimeout

            # Init game board labels
            self.game_board_label = {}
            for n_idx, num in enumerate(range(size, 0, -1)):
                for l_idx, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()[:size]):
                    self.game_board_label["{}{}".format(letter, num)] = [n_idx, l_idx]

        def update_state(self):
            _, out, err = osascript.run(on_get_game_state)
            raw_state = list(map(lambda x: x.strip().split(" ")[1:4], out.split('process Chess,')))
            assert len(raw_state) == self.size*self.size
            sanitize = lambda x: x.strip()[:-1] if x[-1] == "," else x.strip()

            for item in raw_state:
                if item[-1] == "group":
                    loc = self.game_board_label[item[0]]
                    self.game_state[loc[0]][loc[1]] = 0
                elif item[0] == "white":
                    loc = self.game_board_label[item[-1]]
                    self.game_state[loc[0]][loc[1]] = self.chars.index(sanitize(item[1]))
                elif item[0] == "black":
                    loc = self.game_board_label[item[-1]]
                    self.game_state[loc[0]][loc[1]] = -1*self.chars.index(sanitize(item[1]))
                else:
                    raise ValueError('Invalid parsing condition')
            return self.game_state

        def open_game(self):
            osascript.run(open_game)

        def wait(self):
            if self.maxTimeout == -1:
                while True:
                    code, out, err = osascript.run(on_check_move)
                    if len(out.split("\n\n")) == 3:
                        break
                    time.sleep(1)
            else:
                count = int(round(self.maxTimeout))
                for i in range(count):
                    code, out, err = osascript.run(on_check_move)
                    if len(out.split("\n\n")) == 3:
                        break
                    time.sleep(1)

        def move(self, a, b):
            # e.g. a = "e2", b = "e4"
            loc = self.game_board_label[a[-2:]]
            if self.game_state[loc[0]][loc[1]] > 0:
                # White character exist at that spot
                white_char = self.chars[self.game_state[loc[0]][loc[1]]]
                # Target char
                target_loc = self.game_board_label[b[-2:]]
                target_char = b if self.game_state[target_loc[0]][target_loc[1]] == 0 else \
                                "black {}, {}".format(self.chars[-1*self.game_state[target_loc[0]][target_loc[1]]], b)
                _, out, err = osascript.run(on_play_move("white {}, {}".format(white_char, a[-2:]), target_char))
                if len(err) != 0:
                    raise ValueError('Illegal move')
            else:
                # Position does not exist
                raise ValueError('Position does not exist')

        def get_history(self):
            all_moves = list(map(lambda x: x.split("\n\n"), osascript.run(on_get_all_move)[1].split("..,")))
            sanitize = lambda x: x[:-2] if x[-2:] == ".." else x
            result = []
            for it in all_moves:
                if len(it[0]) == 0:
                    continue
                _, white, black = it
                white, black = sanitize(white), sanitize(black)
                white, black = self.parseChess(white), self.parseChess(black)
                result.append([white, black])
            return result
        
        @NiceTry
        def white_move(self, a, b):            
            while True:
                try:
                    self.update_state()
                    break
                except AssertionError:
                    time.sleep(1)
            self.move(a, b)
            self.wait()

        def parseChess(self, x):
            tmp = x.split(" ")
            result = [
                " ".join(tmp[:-5]),
                tmp[-5] + tmp[-4],
                tmp[-2] + tmp[-1]
            ]
            return result

    # Singleton
    instance = None
    def __init__(self, *args, **kwargs):
        if not ChessWrapper.instance:
            ChessWrapper.instance = ChessWrapper.__OnlyOne(*args, **kwargs)
        else:
            ChessWrapper.instance.val = args
    def __getattr__(self, name):
        return getattr(self.instance, name)

# Demo
def main():
    print("Demo Start!")
    Chess = ChessWrapper()
    # Initialize game once
    Chess.open_game()
    # Actively playing, maybe
    Chess.white_move("a2", "a3")
    Chess.white_move("b2", "b3")
    Chess.white_move("c2", "c3")
    print("Demo Finish!")

if __name__ == "__main__":
    main()