import datetime
import shelve
from config import PROMPTS

class Database:
    def __init__(self):
        self.db = shelve.open('db')

    def __del__(self):
        self.db.close()

    def __getitem__(self, key):
        return self.db[key]
    
    def __setitem__(self, key, value):
        self.db[key] = value

    def get(self, key, default=None):
        if key in self.db:
            return self.db[key]
        else:
            return default
        
    def clear(self):
        self.db.clear()

    def contains(self, key):
        return key in self.db

    def is_whitelisted(self, chat_id: int) -> bool:
        white_list = self.db['whitelist']
        return chat_id in white_list

    def add_to_whitelist(self, chat_id: int):
        white_list = self.db['whitelist']
        white_list.add(chat_id)
        self.db['whitelist'] = white_list

    def del_from_whitelist(self, chat_id: int):
        white_list = self.db['whitelist']
        white_list.discard(chat_id)
        self.db['whitelist'] = white_list

    def get_whitelist(self) -> set[int]:
        return self.db['whitelist']

    def prompt(self, id: int = 0) -> str:
        s = PROMPTS[id] + "当前时间: {current_time}"
        return s.replace('{current_time}', (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'))

db = Database()
