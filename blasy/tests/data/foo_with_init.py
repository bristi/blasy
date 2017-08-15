from blasy.blasy import IPlugin

class Foo(IPlugin):

    def __init__(self, favourite_colour="Yellow"):

        self.i_live = 1
        self.favourite_colour = favourite_colour

    def say_hi(self):

        return "Hi!"