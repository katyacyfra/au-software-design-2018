import pygame
import time
import random
import game
import sys, os

class Menu():
    def __init__(self):
        self.level = None
        self.levels_list = []
        self.menu_actions = {
       'main_menu': self.main_menu,
       '0': self.exit,
        }
        print(
    '''
    - -- .-.
- - /  |                - - /|_/|      .-------------------.
   /   |  - _______________| @.@|     /    Welcome          )
- |    |-- (______         >\_C/< ---/                     /
  |    |  -  -   / ______  _/____)  (   to Kitten Saver!  /
-- \   | -  -   / /\ \   \ \         `-------------------'
 -  \  |     - (_/  \_) - \_)
- -  | |

'''
        )

    def main_menu(self):
        print ("Please choose the level you want to start:")
        self.levels_list = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "levels"))
        print('-----------------')
        for i, name in enumerate(self.levels_list):
            print(str(i+1),name)
        print('-----------------')
        print("0 Quit")
        choice = input(" >>  ")
        self.exec_menu(choice)
        return

    def exec_menu(self, choice):
        ch = choice.lower()
        if ch == '':
            self.menu_actions['main_menu']()
        else:
            try:
                if int(ch) > 0:
                    ch = int(ch)
                    self.level = self.levels_list[ch - 1]
                else:
                    self.menu_actions[ch]()
            except KeyError:
                print("Invalid selection, please try again.\n")
                self.menu_actions['main_menu']()
        return


    def back(self):
       self.menu_actions['main_menu']()


    def exit(self):
       sys.exit()

if __name__ == "__main__":
    m = Menu()
    m.main_menu()
    if m.level:
        levels = game.Map.load_level(m.level)
        game.Gameplay(levels, 800, 600, 1, 1, 0, 1, 50).run()