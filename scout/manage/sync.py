from flask_script import Command

class Hello(Command):
    def run(self):
        print('Hello world!')
