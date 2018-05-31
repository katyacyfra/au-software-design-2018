import game
import pygame
import os
import unittest
import random
import utilities
import time, datetime


class MyTestCase(unittest.TestCase):
    def test_sprite(self):
        from utilities import Spritesheet

        screen = pygame.display.set_mode((50, 50))
        pygame.init()
        sp = Spritesheet("walls.png")
        sp = sp.image_at((64, 0, 32, 33))
        screen.blit(sp, ( 20, 30))
        pygame.display.flip()
        pygame.quit()

    def test_load_level(self):
        levels = game.Map.load_level('always_win.txt')
        self.assertEquals(levels[0][0], "#")

    def test_bad_level(self):
        levels = game.Map.load_level('bad_throws_exception.txt')
        self.assertRaises(ValueError)

    def test_write_line(self):
        pygame.init()
        screen = pygame.display.set_mode((50, 50))
        utilities.write("test", (0, 0, 255), 18)
        pygame.quit()

    def test_load_image(self):
        pygame.init()
        screen = pygame.display.set_mode((50, 50))
        cat = pygame.image.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), "images", "cat1.png"))
        screen.blit(cat, (0, 0))
        pygame.quit()

    def test_game(self):
        levels = game.Map.load_level('always_win.txt')
        g = game.Gameplay(levels, 800, 600, 1, 1, 0, 1, 50)
        self.assertEquals(g.total_cats, 1)
        self.assertEquals(g.mo1, 0)
        self.assertEquals(g.player.saved_cats, 0)

    def test_logger(self):
        l = utilities.Logger()
        l.add_record("Hello")
        with open('roguelike.log') as f:
            self.assertEquals(str(datetime.datetime.now())[:-7] + "  Hello\n", f.readlines()[-1])


if __name__ == '__main__':
    unittest.main()