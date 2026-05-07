import cmd

class SSDebugShell(cmd.Cmd):  #Ski Sensor Debug Shell

    prompt : str = 'SSDebugShell > '

    def do_echo(self, txt : str) -> None:
        '''echos the input from the user back to stdout'''
        print(txt)


if __name__ == '__main__':

    SSDebugShell().cmdloop()