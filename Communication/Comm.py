class MsgBoard(object):
    def __init__(self):
        self.board = []

    def send_message(self,message):
        self.board.append(message)

    def get_message(self):
        if len(self.board) > 0:
            return self.board.pop()
        else:
            return None


