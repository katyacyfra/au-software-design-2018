import pygame
import os
import random

images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"images")

class Spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(os.path.join(images_dir, filename)).convert()
        except pygame.error:
            print('Unable to load spritesheet image:'), filename

    def image_at(self, rectangle, colorkey=None):
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image


def re_roll(sides=6, number=1):
    dsum = 0
    for _ in range(number):
        while True:
            roll = random.randint(1, sides)
            if roll < sides:
                dsum += roll
                break
            dsum += roll-1
    return dsum


def write(msg="sd", fontcolor=(255, 0, 255), fontsize=42, font=None):
    myfont = pygame.font.SysFont(font, fontsize)
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext



