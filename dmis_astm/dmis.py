from datetime import datetime


class Dmis(object):

    def __init__(self):
        pass

    def new_messages(self):
        """Returns an ordered list of messages."""
        messages = []
        messages.append(self.header)
        return messages

    @ property
    def header(self):
        return {
            'type': 'H',
            'values': {
                'type': 'H',
                'sender': [b'dmis-astm', b'0.1.0', b'', b''],
                'timestamp': datetime.now()
            }
        }
