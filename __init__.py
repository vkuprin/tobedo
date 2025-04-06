# -*- coding: utf-8 -*-

# Create a mock Filters class for testing
class Filters:
    class command:
        @staticmethod
        def filter(update):
            return update.message and update.message.text and update.message.text.startswith('/')

    def __invert__(self):
        return ~self

Filters = Filters()
