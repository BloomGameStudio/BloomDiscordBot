# -*- coding: UTF-8 -*-

class bold(str):
    def __new__(cls, content):
        return super().__new__(cls, '**' + content + '**')