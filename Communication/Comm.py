import time

class MsgBoard(object):
    def __init__(self):
        self.board = []

    def send_message(self,message):
        message.timestamp = time.time()
        self.board.append(message)

        self.board = sorted(self.board,
                                 key=lambda a: a.timestamp, reverse=True)


    def get_message(self):
        if len(self.board) > 0:
            return self.board.pop()
        else:
            return None


