import pygame
import random
import os
import sys
from utilities import Spritesheet, re_roll, write, Logger

images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
# Game logger
logger = Logger()


def display_textlines(lines, screen, color=(0, 0, 255), image=None, center=True, imagex=0, imagey=0):
    offset = 0
    pygame.display.set_caption("Press ENTER to ext, UP / DOWN to scroll")
    lines.extend(("", "", "", "press [Enter] to continue"))
    while True:
        screen.fill((0, 0, 0))
        if image:
            if not center:
                screen.blit(image, (imagex, imagey))
            else:
                screen.blit(image, (Gameplay.width // 2 - image.get_rect().width // 2,
                                    Gameplay.height // 2 - image.get_rect().height // 2))
        y = 0
        for textline in lines:
            line = write(textline, color, 24)
            screen.blit(line, (20, offset + 14 * y))
            y += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type != pygame.KEYDOWN:
                continue
            elif event.key == pygame.K_DOWN:
                offset -= 14
            elif event.key == pygame.K_UP:
                offset += 14
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                return
        pygame.display.flip()


class Block(object):
    """Map immobile object"""

    def __init__(self):
        self.visible = True
        self.bloody = False


class Floor(Block):
    def __init__(self):
        Block.__init__(self)
        self.picture = random.choice((Gameplay.FLOOR, Gameplay.FLOOR1))


class Wall(Block):
    def __init__(self):
        Block.__init__(self)
        self.picture = random.choice((Gameplay.WALL, Gameplay.WALL1, Gameplay.WALL2))


class Mob(object):
    """Active  moving objects"""

    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        self.x = x
        self.y = y
        self.xp = xp
        self.kills = 0
        self.killdict = {}
        self.hunger = 0
        self.level = level
        self.rank = ""
        self.damaged = False
        if hp == 0:
            self.hitpoints = random.randint(10, 20)
        else:
            self.hitpoints = hp
        self.hpmax = self.hitpoints
        if picture == "":
            self.picture = Gameplay.MONSTERPICTURE
        else:
            self.picture = picture
        self.strength = random.randint(1, 6)
        self.dexterity = random.randint(1, 6)
        self.intelligence = random.randint(1, 6)
        self.inventory = {"fist": 1}
        self.sight_radius = 2
        for z in ["knife", "shield", "armor", "sword", ]:
            if random.random() < 0.1:
                self.inventory[z] = 1

    def update_inventory(self):
        zeroitems = [k for k, v in self.inventory.items() if v < 1]
        for key in zeroitems:
            del self.inventory[key]

    def update_health(self):
        self.health = self.hitpoints / self.hpmax


    def ai(self, player):
        """Simple ai for finding player and haunting him"""
        if abs(player.x - self.x) < self.sight_radius and abs(player.y - self.y) < self.sight_radius:
            dx, dy = 0, 0
            if self.x < player.x:
                dx = 1
            elif self.x > player.x:
                dx = -1
            if self.y < player.y:
                dy = 1
            elif self.y > player.y:
                dy = -1
            if dx != 0 and dy != 0:
                dx, dy = random.choice([(dx, 0), (0, dy)])
        else:
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        return dx, dy


class Boss(Mob):
    '''Strong and smart enemy'''

    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        Mob.__init__(self, x, y, xp, level, hp, picture)
        self.sight_radius = 7
        self.picture = random.choice(
            (Gameplay.DRAGON, Gameplay.SLENDERMAN, Gameplay.GOP, Gameplay.BOSS, Gameplay.DART ))
        self.hitpoints = 35
        self.hpmax = self.hitpoints
        self.inventory["sword"] = 1


class Immobile(Mob):
    """Not moving enemy"""

    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        Mob.__init__(self, x, y, xp, level, hp, picture)
        self.picture = Gameplay.WITCH
        self.hitpoints = 50
        self.hpmax = self.hitpoints

    def ai(self, player):
        return 0, 0


class Weak_enemy(Mob):
    """Weak enemy"""

    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        Mob.__init__(self, x, y, xp, level, hp, picture)
        self.picture = random.choice((Gameplay.ZOMBIE, Gameplay.KNIGHT ))
        self.strength = random.randint(3, 4)
        self.hitpoints = random.randint(15, 20)
        self.hpmax = self.hitpoints
        self.inventory = {"fangs": 1}


class Player(Mob):
    def __init__(self, x, y, xp=0, level=1, hp=0, picture=""):
        Mob.__init__(self, x, y, xp, level, hp, picture)
        self.inventory = {"shield": 1, "fist": 1}
        self.dressed = []
        self.z = 0
        self.keys = []
        self.saved_cats = 0
        self.mana = 0
        if hp == 0:
            self.hitpoints = random.randint(5, 10)
        else:
            self.hitpoints = hp
        self.hpmax = self.hitpoints
        if picture == "":
            self.picture = Gameplay.PLAYERPICTURE
        else:
            self.picture = picture

    def detect(self):
        return random.gauss(0.5 + self.intelligence * 0.066 + self.dexterity * 0.033, 0.2)

    def evade(self):
        return random.gauss(0.5 + self.dexterity * 0.1, 0.2)

    def ai(self, player=None):
        return 0, 0

    def show_inventory(self):
        """show inventory, return lines of text"""
        lines = ["you carry this stuff with you:"]
        if len(self.inventory) == 0:
            lines.append("you carry nothing")
        else:
            lines.append("amount, description")
            lines.append("===================")
            for thing in self.inventory:
                lines.append(str(self.inventory[thing]) + ".........." + str(thing))
        return lines

    def take(self, item):
        """increase amount of a item in the inventory"""
        if item in self.inventory:
            self.inventory[item] += 1
        else:
            self.inventory[item] = 1
        self.xp += 1

    def undress(self):
        """remove the last item in the inventory"""
        last = None
        if len(self.dressed) > 0:
            last = self.dressed.pop()
        return last

    def dress(self):
        """dress inventory"""
        for k in self.inventory.keys():
            if k not in self.dressed and k in ['shield', 'armor', 'helm']:
                self.dressed.append(k)


class Item(object):
    """Objects that can be cacnged by player"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = True
        self.hitpoints = 1
        self.picture = Gameplay.LOOT
        self.carried = False


class Trap(Item):
    """Trap, decreases hp and disappears"""

    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.level = random.randint(1, 6)
        self.hitpoints = self.level * 2
        self.picture = Gameplay.TRAP
        self.visible = False

    def detect(self):
        return random.gauss(0.5 + self.level * 0.1, 0.25)

    def damage(self):
        damage = 0
        for _ in range(self.level):
            damage += random.randint(1, 7)
        return damage


class Food(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.picture = random.choice(
            (Gameplay.PIZZA, Gameplay.COFFEE, Gameplay.MILK, Gameplay.CAKE, Gameplay.BURGER, Gameplay.ICECREAM ))


class Cat(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.picture = random.choice((Gameplay.CAT1, Gameplay.CAT2, Gameplay.CAT3))


class Key(Item):
    def __init__(self, x, y, color="dull"):
        Item.__init__(self, x, y)
        self.color = color
        self.picture = Gameplay.KEY


class Door(Item):
    def __init__(self, x, y, color="dull"):
        Item.__init__(self, x, y)
        self.locked = True
        self.closed = True
        self.picture = Gameplay.DOOR
        self.color = color


class Loot(Item):
    """Useful inventory"""

    def __init__(self, x, y, descr=""):
        Item.__init__(self, x, y)
        if descr == "":
            self.text = random.choice(["trash", "coin", "helm", "rags",
                                       "whiskas", "stone", "armor", "gem",
                                       "healing potion", "shield"])
        else:
            self.text = descr


class Map(object):
    """Loads level with map"""
    LEGEND = {
        "#": "wall",
        "D": "door",
        ".": "floor",
        "T": "trap",
        "M": "monster",
        "B": "Boss",
        "S": "immobile",
        "L": "loot",
        "a": "food",
        "k": "key",
        "C": "cat",
        "H": "house"
    }

    @staticmethod
    def load_level(filename):
        """loads text and returns list"""
        lines = []
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "levels", filename), "r") as f:
            for line in f:
                if line.strip() != "":
                    lines.append(line[:-1])  # exclude newline char
        return lines

    @staticmethod
    def check_errors(filename):
        """check for level errors """
        lines = Map.load_level(filename)
        if len(lines) == 0:
            raise ValueError("{}: level has no lines".format(filename))
        width = len(lines[0])
        line_number = 1
        good_lines = []
        for line in lines:
            if len(line) != width:
                raise ValueError("{}: bad line length".format(filename) +
                                 " in line number {}".format(line_number))
            x = 1
            for char in line:
                if char not in Map.LEGEND:
                    raise ValueError("{}: line {} pos {}:".format(filename, line_number, x) +
                                     "char {} is not in Level.LEGEND".format(char) +
                                     "\n allowed Symbols are numbers for warning signs and:\n" +
                                     str(Map.LEGEND.keys()))
                x += 1
            good_lines.append(line)
            line_number += 1
        return good_lines

    def __init__(self, lines, signsdict=LEGEND):
        self.lines = lines
        self.layout = {}
        self.signsdict = signsdict
        self.mobs = []
        self.signs = []
        self.traps = []
        self.doors = []
        self.fruits = []
        self.loot = []
        self.keys = []
        self.cats = []
        self.width = 0
        self.depth = 0
        y = 0
        for line in self.lines:
            x = 0
            for char in line:
                self.layout[(x, y)] = Floor()
                if char == "M":
                    self.mobs.append(Weak_enemy(x, y))
                elif char == "C":
                    self.cats.append(Cat(x, y))
                elif char == "B":
                    self.mobs.append(Boss(x, y))
                elif char == "S":
                    self.mobs.append(Immobile(x, y))
                elif char == "T":
                    self.traps.append(Trap(x, y))
                elif char == "D":
                    self.doors.append(Door(x, y))
                elif char == "a":
                    self.fruits.append(Food(x, y))
                elif char == "L":
                    self.loot.append(Loot(x, y))
                elif char == "k":
                    self.keys.append(Key(x, y))
                elif char == ".":
                    pass
                elif char == "#":
                    self.layout[(x, y)] = Wall()

                x += 1
            y += 1
            self.width = max(self.width, x)
            self.depth = max(self.depth, y)

        for sign in self.signs:
            sign.text = self.signsdict[sign.char]

    def update(self):
        self.mobs = [m for m in self.mobs if m.hitpoints > 0]
        self.traps = [t for t in self.traps if t.hitpoints > 0]
        self.fruits = [f for f in self.fruits if not f.carried > 0]
        self.keys = [k for k in self.keys if not k.carried]
        self.loot = [i for i in self.loot if not i.carried]
        self.cats = [i for i in self.cats if not i.carried]
        self.doors = [d for d in self.doors if d.closed]

    def is_monster(self, x, y):
        for monster in self.mobs:
            if monster.hitpoints > 0 and monster.x == x and monster.y == y:
                return monster
        return False


class Text_fly(pygame.sprite.Sprite):
    """Notes about game on map"""

    def __init__(self, x, y, text="hi", rgb=(255, 0, 0), blockxy=True,
                 dx=0, dy=-50, duration=2, acceleration_factor=0.96, delay=0):
        self._layer = 7
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.text = text
        self.r, self.g, self.b = rgb[0], rgb[1], rgb[2]
        self.dx = dx
        self.dy = dy
        if blockxy:
            self.x, self.y = Gameplay.scrollx + x * 32, Gameplay.scrolly + y * 32
        else:
            self.x, self.y = x, y
        self.duration = duration
        self.acc = acceleration_factor
        self.image = write(self.text, (self.r, self.g, self.b), 22)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100, -100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc
            self.dx *= self.acc
            self.rect.center = (self.x, self.y)

            if self.time > self.duration:
                self.kill()


class FlyImage(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, image, duration=1, acceleration_factor=1.00):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = image
        self.rect = self.image.get_rect()
        self.x, self.y = Gameplay.scrollx + start_x * 32, Gameplay.scrolly + start_y * 32 + 16
        self.tx, self.ty = Gameplay.scrollx + target_x * 32, Gameplay.scrolly + target_y * 32 + 16
        self.duration = duration
        self.acc = acceleration_factor
        self.dx = (self.tx - self.x) / self.duration
        self.dy = (self.ty - self.y) / self.duration
        self.rect.center = (self.x, self.y)
        self.time = 0

    def update(self, seconds):
        self.y += self.dy * seconds
        self.x += self.dx * seconds
        self.dy *= self.acc
        self.dx *= self.acc
        self.rect.center = (self.x, self.y)
        self.time += seconds
        if self.time > self.duration:
            self.kill()


class Gameplay(object):
    scrollx = 0
    scrolly = 0

    def __init__(self, checked_list_of_levels, width=650, height=420, x=1, y=1, xp=0, level=1, hp=50):
        pygame.init()
        self.clock = pygame.time.Clock()

        Gameplay.width = width
        Gameplay.height = height

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.fps = 30
        pygame.display.set_caption("Press ESC to quit")
        self.gui_height = 100
        self.gui_width = 150
        self.map = pygame.Surface((self.gui_width, self.gui_height))
        self.mapzoom = 3

        Gameplay.WALLS = Spritesheet("walls.png")
        Gameplay.FLOORS = Spritesheet("floors.png")
        Gameplay.FOOD = Spritesheet("food2.png")

        # MAP
        Gameplay.WALL = Gameplay.WALLS.image_at((0, 0, 32, 32))
        Gameplay.WALL1 = Gameplay.WALLS.image_at((448, 0, 32, 32))
        Gameplay.WALL2 = Gameplay.WALLS.image_at((416, 160, 32, 32))
        Gameplay.FLOOR = Gameplay.FLOORS.image_at((0, 96, 32, 32))
        Gameplay.FLOOR1 = Gameplay.FLOORS.image_at((64, 96, 32, 32))
        Gameplay.TRAP = Gameplay.WALLS.image_at((384, 319, 32, 32), (0, 0, 0))

        #FOOD
        Gameplay.PIZZA = Gameplay.FOOD.image_at((10, 0, 32, 32), (0, 0, 0))
        Gameplay.CAKE = Gameplay.FOOD.image_at((10, 256, 34, 34), (0, 0, 0))
        Gameplay.MILK = Gameplay.FOOD.image_at((160, 164, 32, 32), (0, 0, 0))
        Gameplay.COFFEE = Gameplay.FOOD.image_at((56, 260, 36, 34), (0, 0, 0))
        Gameplay.BURGER = Gameplay.FOOD.image_at((10, 196, 32, 34), (0, 0, 0))
        Gameplay.ICECREAM = Gameplay.FOOD.image_at((10, 132, 32, 34), (0, 0, 0))

        #ITEMS
        Gameplay.DOOR = pygame.image.load(os.path.join(images_dir, "door.png"))
        Gameplay.LOOT = pygame.image.load(os.path.join(images_dir, "tresure.png"))
        Gameplay.KEY = pygame.image.load(os.path.join(images_dir, "key.png"))

        #CATS
        Gameplay.CAT1 = pygame.image.load(os.path.join(images_dir, "cat1.png"))
        Gameplay.CAT2 = pygame.image.load(os.path.join(images_dir, "cat2.png"))
        Gameplay.CAT3 = pygame.image.load(os.path.join(images_dir, "cat3.png"))

        #PLAYER
        Gameplay.PLAYERPICTURE = pygame.image.load(os.path.join(images_dir, "programmer.png"))


        #BOSSES
        Gameplay.GOP = pygame.image.load(os.path.join(images_dir, "gop1.png"))
        Gameplay.SLENDERMAN = pygame.image.load(os.path.join(images_dir, "slender.png"))
        Gameplay.BOSS = pygame.image.load(os.path.join(images_dir, "boss.png"))
        Gameplay.DRAGON = pygame.image.load(os.path.join(images_dir, "dragon.png"))
        Gameplay.DART = pygame.image.load(os.path.join(images_dir, "dart.png"))

        #ENEMIES
        Gameplay.KNIGHT = pygame.image.load(os.path.join(images_dir, "knight2.png"))
        Gameplay.MONSTERPICTURE = pygame.image.load(os.path.join(images_dir, "knight2.png"))
        Gameplay.WITCH = pygame.image.load(os.path.join(images_dir, "witch.png"))
        Gameplay.ZOMBIE = pygame.image.load(os.path.join(images_dir, "zombie.png"))


        # GAMEOVER
        Gameplay.GAMEOVER = pygame.image.load(os.path.join(images_dir, "crying_cat.png"))
        Gameplay.WINNER = pygame.image.load(os.path.join(images_dir, "happy_cat.png"))
        # create player instance
        self.player = Player(x, y, xp, level, hp)

        self.level = Map(checked_list_of_levels)
        self.total_cats = len(self.level.cats)
        self.seconds = 0
        self.turns = 0
        self.mo1 = 0
        self.mo2 = 0
        self.background = pygame.Surface((self.level.width * 32, self.level.depth * 32))

        self.flytextgroup = pygame.sprite.Group()
        self.flyimagegroup = pygame.sprite.Group()

        self.allgroup = pygame.sprite.LayeredUpdates()

        Text_fly.groups = self.flytextgroup, self.allgroup
        FlyImage.groups = self.flytextgroup, self.flyimagegroup, self.allgroup

        #help
        self.hilftextlines = []
        self.hilftextlines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self.hilftextlines.append("commands:")
        self.hilftextlines.append("[w] [a] [s] [d]......move player up/left/down/right")
        self.hilftextlines.append("[i]..................show inventory")
        self.hilftextlines.append("[r]..................remove last inventory")
        self.hilftextlines.append("[d]..................dress inventory")
        self.hilftextlines.append("[Esc]................exit game")
        self.hilftextlines.append("[h]..................show help, (this text)")
        self.hilftextlines.append("[q]..................drink healing poison")
        self.hilftextlines.append("- - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    def draw_map(self):
        self.map.fill((20, 20, 20))
        scrollx = self.gui_width / 2 - self.player.x * self.mapzoom
        scrolly = self.gui_height / 2 - self.player.y * self.mapzoom
        y = 0
        for line in self.level.lines:
            x = 0
            for char in line:
                if char == "#":
                    pygame.draw.rect(self.map, (150, 150, 150), (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                                                 self.mapzoom, self.mapzoom))
                else:
                    pygame.draw.rect(self.map, (50, 50, 50), (x * self.mapzoom + scrollx, y * self.mapzoom + scrolly,
                                                              self.mapzoom, self.mapzoom))
                # player pixel
                pygame.draw.rect(self.map, (255, 0, 0), (self.player.x * self.mapzoom + scrollx,
                                                         self.player.y * self.mapzoom + scrolly, self.mapzoom,
                                                         self.mapzoom))
                x += 1
            y += 1

        line = write("zoom = {} press + or -".format(self.mapzoom), (0, 0, 255), 18)
        self.map.blit(line, (0, self.gui_height - 12))

    def draw(self):
        for y in range(self.level.depth):
            for x in range(self.level.width):
                try:
                    self.background.blit(self.level.layout[(x, y)].picture, (x * 32, y * 32))
                    for sign in [s for s in self.level.signs if s.x == x and s.y == y]:
                        self.background.blit(sign.picture, (x * 32, y * 32))
                    for trap in [t for t in self.level.traps if t.x == x and t.y == y and t.hitpoints > 0
                    and t.visible]:
                        self.background.blit(trap.picture, (x * 32, y * 32))
                    for door in [d for d in self.level.doors if d.x == x and d.y == y and d.closed]:
                        self.background.blit(door.picture, (x * 32, y * 32))
                    for loot in [l for l in self.level.loot if l.x == x and l.y == y and not l.carried]:
                        self.background.blit(loot.picture, (x * 32, y * 32))
                    for fruit in [f for f in self.level.fruits if f.x == x and f.y == y and not f.carried]:
                        self.background.blit(fruit.picture, (x * 32, y * 32))
                    for cat in [f for f in self.level.cats if f.x == x and f.y == y and not f.carried]:
                        self.background.blit(cat.picture, (x * 32, y * 32))
                    for key in [k for k in self.level.keys if k.x == x and k.y == y and not k.carried]:
                        self.background.blit(key.picture, (x * 32, y * 32))
                except:
                    pass

        Gameplay.scrollx = (self.width - self.gui_width) / 2 - self.player.x * 32
        Gameplay.scrolly = (self.height - self.gui_height) / 2 - self.player.y * 32
        self.screen.fill((0, 0, 0))  # make all black
        self.screen.blit(self.background, (Gameplay.scrollx, Gameplay.scrolly))

        # draw mobs
        for monster in self.level.mobs:
            monster.update_health()
            self.screen.blit(monster.picture, (Gameplay.scrollx + monster.x * 32, Gameplay.scrolly + monster.y * 32))
            health = int(monster.health * 32)
            pygame.draw.rect(self.screen, (255, 0, 0), (Gameplay.scrollx + monster.x * 32,
                                                        Gameplay.scrolly + monster.y * 32 - 15, 32, 5))

            pygame.draw.rect(self.screen, (0, 255, 0), (Gameplay.scrollx + monster.x * 32,
                                                        Gameplay.scrolly + monster.y * 32 - 15, health, 5))
        #draw player
        self.screen.blit(self.player.picture,
                         (Gameplay.scrollx + self.player.x * 32, Gameplay.scrolly + self.player.y * 32))
        #GUI
        pygame.draw.rect(self.screen, (0, 0, 0), (self.width - self.gui_width, 0, self.gui_width, self.height))
        self.draw_map()
        self.screen.blit(self.map, (self.width - self.gui_width, 0))
        #minimap:
        line = write("HP: {}".format(self.player.hitpoints), (0, 255, 0), 18)
        y = self.gui_height + 5
        self.screen.blit(line, (self.width - self.gui_width, y))

        pygame.draw.rect(self.screen, (0, 255, 0), (self.width - self.gui_width + 50, y, self.player.hitpoints, 10))

        #BAR MANA
        y += 15
        line = write("MP: {:.0f}".format(self.player.mana), (0, 0, 255), 18)
        self.screen.blit(line, (self.width - self.gui_width, y))
        pygame.draw.rect(self.screen, (0, 0, 255), (self.width - self.gui_width + 50, y, self.player.mana, 10))
        #HUNGER BAR
        y += 15
        line = write("Hu: {:.0f}".format(self.player.hunger), (255, 255, 0), 18)
        self.screen.blit(line, (self.width - self.gui_width, y))
        pygame.draw.rect(self.screen, (255, 255, 0), (self.width - self.gui_width + 50, y, self.player.hunger, 10))

        #CATS BAR
        y += 15
        line = write("Cats: %d/%d   " % (self.player.saved_cats, self.total_cats ), (237, 28, 36), 18)
        self.screen.blit(line, (self.width - self.gui_width, y))
        for number in range(-7, 0, 1):
            if self.status[number][:6] == "combat:":
                r, g, b = 255, 0, 255
            else:
                r, g, b = 0, 0, 255
            line = write("{}".format(self.status[number]), (r, g, b + 30 * number), 24)
            self.screen.blit(line, (0, self.height + number * 14))

    def count_monsters(self):
        self.mo1 = len(self.level.mobs)
        self.mo2 = len(self.level.mobs)


    def update_doors(self):
        '''Open doors if user has key'''
        for door in [d for d in self.level.doors if
                     d.x == self.player.x + self.player.dx and d.y == self.player.y + self.player.dy and d.closed]:
            if len(self.player.keys) > 0:
                mykey = self.player.keys.pop()
                door.closed = False  # unlocked !
                self.status.append("{}: door unlocked! 1 key used up)".format(self.turns))
            else:
                self.player.dx, self.player.dy = 0, 0
                self.status.append("{}: Ouch! You bump into a door".format(self.turns))
                self.player.hitpoints -= 1
                self.player.damaged = True
                Text_fly(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")

    def update_food(self):
        '''Take and eat foood'''
        for fruit in self.level.fruits:
            if fruit.x == self.player.x and fruit.y == self.player.y:
                fruit.carried = True
                Text_fly(self.player.x, self.player.y, "Yummy! - hunger", (0, 200, 0))
                self.player.hunger -= random.randint(5, 30)
                self.player.hunger = max(0, self.player.hunger)

    def update_cats(self):
        """ Update saved cats number"""
        for cat in self.level.cats:
            if cat.x == self.player.x and cat.y == self.player.y:
                cat.carried = True
                Text_fly(self.player.x, self.player.y, "Yeah! You saved a cat", (0, 200, 0))
                self.player.saved_cats += 1
                logger.add_record("Kitten was saved")

    def update_traps(self):
        """Traps on map, damage players and disappear"""
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for (dx, dy) in dirs:
            traps = [t for t in self.level.traps if
                     t.x == self.player.x + dx and t.y == self.player.y + dy and not t.visible]
            for t in traps:
                if self.player.detect() > t.detect():
                    t.visible = True
                    self.status.append("Trap spotted")

            traps = [t for t in self.level.traps if t.x == self.player.x and t.y == self.player.y]
            for t in traps:
                damage = t.damage()
                self.status.append("You step into a trap!")
                if self.player.evade() > t.detect():
                    damage *= 0.5
                    damage = round(damage, 0)
                    self.status.append("Your high dexterity allows you to take only half the damage")
                    self.status.append("The trap is hurting you for {} damage!".format(self.turns, damage))
                    self.player.hitpoints -= damage
                    self.player.damaged = True
                    Text_fly(self.player.x, self.player.y, "A trap! Dmg: {}".format(damage))
                    t.hitpoints -= random.randint(0, 4)  # damage to trap
                    if t.hitpoints < 1:
                        self.status.append("{}: trap destroyed!".format(self.turns))

    def update_keys(self):
        """Checks if player found door and has key"""
        for key in self.level.keys:
            if key.x == self.player.x and key.y == self.player.y:
                key.carried = True
                self.player.keys.append(key)
                self.status.append("{} key found".format(self.turns))
                Text_fly(self.player.x, self.player.y, "a key", (0, 200, 0))


    def update_inventory(self):
        """Inventory was found"""
        for i in self.level.loot:
            if i.x == self.player.x and i.y == self.player.y and not i.carried:
                i.carried = True
                if i.text in self.player.inventory:
                    self.player.inventory[i.text] += 1
                else:
                    self.player.inventory[i.text] = 1
                    self.status.append("{} Loot found! ({})".format(self.turns, i.text))
                    Text_fly(self.player.x, self.player.y, i.text + " found!", (0, 200, 0))

    def update_monsters(self):
        """"Update monters and their hp"""
        for monster in self.level.mobs:
            x, y = monster.x, monster.y
            dx, dy = monster.ai(self.player)
            if self.level.is_monster(x + dx, y + dy):
                continue
            if x + dx == self.player.x and y + dy == self.player.y:
                self.status.extend(battle(monster, self.player, self.level))
                self.status.extend(battle(self.player, monster, self.level))
                self.count_monsters()
                continue
            try:
                whereto = self.level.layout[(x + dx, y + dy)]
            except:
                pass
            if type(whereto).__name__ == "Wall":
                continue
            if len([t for t in self.level.traps if t.x == x + dx and t.y == y + dy]) > 0:
                continue
            if len([d for d in self.level.doors if d.x == x + dx and d.y == y + dy]) > 0:
                continue
            monster.x += dx
            monster.y += dy

    def run(self):
        """"Main loop of game"""
        logger.add_record("Start the game!")
        running = True
        self.newturn = False
        self.count_monsters()
        self.status = ["The game begins!", "Hello", "Hint: goto x:5 y:5",
                       "Hint: avoid traps", "q for health point", "press ? for help", "good luck!"]
        while running and self.player.hitpoints > 0:
            self.seconds = self.clock.tick(self.fps) / 1000.0

            if self.total_cats == self.player.saved_cats:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    where = self.level.layout[(self.player.x, self.player.y)]
                    self.status.append("Turn {}".format(self.turns))
                    if event.key == pygame.K_ESCAPE:
                        if self.firemode:
                            self.firemode = False
                        else:
                            running = False
                            break
                    elif event.key == pygame.K_i:  # drink healing poison
                        display_textlines(self.player.show_inventory(), self.screen)
                        continue
                    elif event.key == pygame.K_r:
                        last = self.player.undress()
                        if last is not None:
                            Text_fly(self.player.x, self.player.y, "{} was removed from inventory".format(last),
                                     (0, 0, 255))
                        continue

                    elif event.key == pygame.K_d:
                        self.player.dress()
                        Text_fly(self.player.x, self.player.y, "Dress inventory".format(), (0, 0, 255))
                        continue
                    elif event.key == pygame.K_PLUS:
                        self.mapzoom += 1
                        continue
                    elif event.key == pygame.K_MINUS:
                        self.mapzoom -= 1
                        self.mapzoom = max(2, self.mapzoom)
                        continue

                    self.newturn = True
                    self.player.dx = 0
                    self.player.dy = 0
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player.dy -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player.dy += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.dx -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.dx += 1
                    elif event.key == pygame.K_QUESTION or event.key == pygame.K_h:
                        display_textlines(self.hilftextlines, self.screen)
                        continue
                    elif event.key == pygame.K_q:
                        if ("healing potion" in self.player.inventory and
                                    self.player.inventory["healing potion"] > 0):
                            self.player.inventory["healing potion"] -= 1
                            effect = re_roll()
                            self.player.hitpoints += effect
                            self.status.append("{}: You drink the healing potion und gain {} hitpoints".format(
                                self.turns, effect))
                            Text_fly(self.player.x, self.player.y, "heal: +{} hp".format(effect),
                                     (0, 0, 255))
                            self.player.hitpoints = min(self.player.hpmax, self.player.hitpoints)  # limit healing
                            if self.player.hitpoints == self.player.hpmax:
                                self.player.damaged = False
                            else:
                                self.player.damaged = True
                        else:
                            self.status.append("{}: You have no healing potion. Gather more loot!".format(
                                self.turns))
                    try:
                        whereto = self.level.layout[(self.player.x + self.player.dx, self.player.y + self.player.dy)]
                    except:
                        pass
                    monster = self.level.is_monster(self.player.x + self.player.dx, self.player.y + self.player.dy)
                    if monster:
                        self.status.extend(battle(self.player, monster, self.level))
                        self.status.extend(battle(monster, self.player, self.level))
                        self.player.dx, self.player.dy = 0, 0
                        self.count_monsters()

                    elif type(whereto).__name__ == "Wall":
                        self.status.append("{}: Please don't run into walls!".format(self.turns))
                        self.player.hitpoints -= 1
                        self.player.damaged = True
                        Text_fly(self.player.x, self.player.y, "Ouch! Dmg: 1 hp")
                        self.player.dx, self.player.dy = 0, 0

                    self.update_doors()
                    self.player.x += self.player.dx
                    self.player.y += self.player.dy

                    try:
                        where = self.level.layout[(self.player.x, self.player.y)]
                    except:
                        pass

                    self.update_food()
                    self.update_cats()
                    self.update_traps()
                    self.update_keys()
                    self.update_inventory()

            if len(self.flyimagegroup) > 0:
                pass
            elif self.newturn:
                self.newturn = False
                self.turns += 1
                if self.player.mana < 32:
                    self.player.mana += 0.1
                self.player.hunger += 0.25
                if self.player.hunger > 100:
                    self.player.hitpoints -= 1
                    self.player.damaged = True
                    Text_fly(self.player.x, self.player.y, "Hunger: dmg 1")
                self.level.update()

                self.update_monsters()

            pygame.display.set_caption("  press Esc to quit. Fps: %.2f (%i x %i)" % (
                self.clock.get_fps(), self.width, self.height))
            self.draw()

            self.allgroup.update(self.seconds)
            self.allgroup.draw(self.screen)

            pygame.display.flip()
        lines = ["", "Game Over!", '',
                 "Hitpoints: {}".format(self.player.hitpoints),
                 "Victories: {}".format(self.player.kills), "", ""]
        if self.player.hitpoints < 1:
            lines.append("You are dead.")
            logger.add_record("Game over, player is dead")
        else:
            lines.append("You win!")
            logger.add_record("Player won")
        lines.append("")
        lines.append("-------------Saved kittens:----------")
        lines.append(str(self.player.saved_cats) + " from " + str(self.total_cats))
        lines.append("")
        lines.append("------------ You killed: ------------")
        for v in self.player.killdict:
            lines.append("{} {}".format(self.player.killdict[v], v))
        if self.player.hitpoints < 1:
            display_textlines(lines, self.screen, (255, 255, 255), Gameplay.GAMEOVER)
        else:
            display_textlines(lines, self.screen, (255, 255, 255), Gameplay.WINNER)

        for line in lines:
            print(line)
        pygame.quit()
        sys.exit()


def battle(attacker, defender, level):
    txt = []
    attackername = type(attacker).__name__
    defendername = type(defender).__name__
    if attacker.hitpoints > 0 and defender.hitpoints > 0:

        stats = {"sword": (2, 5, 0.1, 0.01),
                 "knife": (2, 3, 0.05, 0.01),
                 "fangs": (1, 3, 0.15, 0.00),
                 "fist": (1, 2, 0.01, 0.00)}

        for weapon in ["sword", "knife", "fangs", "fist"]:
            if weapon in attacker.inventory:
                damage = random.randint(stats[weapon][0], stats[weapon][1])

                if random.random() < stats[weapon][2]:
                    txt.append("{} makes double damage!".format(weapon))
                    damage *= 2

                if random.random() < stats[weapon][3]:
                    txt.append("{} is destroyed!".format(weapon))
                    attacker.inventory[weapon] -= 1
                    attacker.update_inventory()
                damage += attacker.level
                txt.append("{} attacks {} with {} for {} raw damage".format(
                    attackername, defendername, weapon, damage))
                break
        blocked_damage = 0
        stats = {"armor": (0.75, 1, 0.01),
                 "shield": (0.5, 2, 0.04),
                 "helm": (0.3, 1, 0.01)}
        for piece in ["armor", "shield", "helm"]:
            if piece in defender.inventory:
                if random.random() < stats[piece][0]:
                    blocked_damage += stats[piece][1]
                    txt.append("{} of {} blocks {} damage".format(piece, defendername, stats[piece][1]))
                if random.random() < stats[piece][2]:
                    txt.append("{} is shattered!")
                    defender.inventory[piece] -= 1  # remove armor piece
                    defender.update_inventory()

        damage -= blocked_damage
        damage = max(0, damage)
        fly_dx, fly_dy = 0, -30
        if defender.x > attacker.x:
            fly_dx = 50
        elif defender.x < attacker.x:
            fly_dx = -50
        if defender.y > attacker.y:
            fly_dy = 50
        elif defender.y < attacker.y:
            fly_dy = -50
        Text_fly(defender.x, defender.y, "dmg: {}".format(damage), dx=fly_dx,
                 dy=fly_dy)  # Text fly's away from opponent
        if blocked_damage > 0:
            Text_fly(defender.x, defender.y + 1, "blocked: {}".format(blocked_damage), (0, 255, 0), dx=fly_dx)
        if damage > 0:
            defender.hitpoints -= damage
            defender.damaged = True
            txt.append("combat: {} looses {} hitpoints ({} hp left)".format(defendername, damage,
                                                                            defender.hitpoints))
            if defender.hitpoints < 1:
                exp = random.randint(7, 10)
                attacker.xp += exp
                attacker.kills += 1
                victim = defendername
                if victim in attacker.killdict:
                    attacker.killdict[victim] += 1
                else:
                    attacker.killdict[victim] = 1
                logger.add_record("%s was killed" % victim)
                txt.append("combat: {} has {} hp left, {} gains {} Xp".format(defendername, defender.hitpoints,
                                                                              attackername, exp))
        else:
            txt.append("combat: {} is not harmed".format(defendername))
    attacker.hunger += 1
    defender.hunger += 1
    return txt