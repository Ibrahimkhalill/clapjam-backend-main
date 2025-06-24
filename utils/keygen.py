from secrets import choice as c
from datetime import datetime as dt


class KeyGen:
    DATETIME_FORMAT_KEY = '%f%y%m%d%M%H%S'
    TXN_ID_HEAD = 'TXN'
    
    def random_az(self) -> str:
        return chr(c([x for x in range(65,123) if x not in range(91,97)]))
        
    def random_digit(self) -> int: 
        return c(range(10))
        
    def num_key(self, key_len=6) -> str:
        return ''.join(str(self.random_digit()) for i in range(key_len))

    def datetime_key(self) -> str:
        return dt.today().strftime(self.DATETIME_FORMAT_KEY)

    def transaction_id(self, head=TXN_ID_HEAD, tail_len=4) -> str:
        return  head + self.datetime_key() + self.alphanumeric_key(tail_len).upper()
    
    def alpha_key(self, key_len=69) -> str:
        return ''.join([self.random_az() for i in range(key_len)])

    def alphanumeric_key(self, key_len=69) -> str:
        return ''.join([
        str(c([self.random_az, self.random_digit])()) 
        for i in range(key_len)
        ])

    def timestamped_alphanumeric_id(self, head_len=10):
        return self.alphanumeric_key(head_len) + self.datetime_key() + self.alpha_key(head_len)