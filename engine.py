#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      milo
#
# Created:     10/03/2020
# Copyright:   (c) milo 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import tcod as libtcod
import math
import textwrap
import shelve

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 45

MAP_WIDTH = 80
MAP_HEIGHT = 38

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

#spell amount
MIN_HEAL = 1
MAX_HEAL = 20
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5

FIREBALL = {"max_range" : 8, "movable" : True, "damage" : 12, "spell_pene" : False, "pattern" : [(-1, -1),(0, -1),(1,-1),(-1,0),(0, 0),(1,0),(-1, 1),(0,1),(1,1)], "line_color" : libtcod.red, "pattern_color" : libtcod.red }
FREEZE = {"max_range" : 5, "movable" : True, "damage" : 5, "spell_pene" : True, "pattern" : [(0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1,0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)],
    "line_color" : False, "pattern_color" : libtcod.red, "duration" : 5}
ARCANE_BEAM = {"max_range" : 9, "movable" : True, "damage" : 10, "spell_pene" : True, "pattern" : False, "line_color" : libtcod.red, "pattern_color" : False}
BOMB = {"max_range" : 5, "movable" : True, "damage" : 30, "spell_pene" : True, "pattern" : [(-1, -1),(0, -1),(1,-1),(-1,0),(0, 0),(1,0),(-1, 1),(0,1),(1,1)],
    "line_color" : False, "pattern_color" : libtcod.red}


FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

LIMIT_FPS = 20  #20 frames-per-second maximum

MAX_ROOMS_MONSTERS = 3
MAX_ROOM_ITEMS = 3

#for GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50

LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30


#custom tiles. 256
a = 256

####jungle level
#tiles
jungle_wall = 256
jungle_floor_1 = 257
jungle_floor_2 = 258
jungle_pond_large = (259, 260, 261, 262)
jungle_pond_small = 263
jungle_floor_3 = 264 #dirt

#sand level
sand_wall = 265
sand_floor_1 = 266
sand_floor_2 = 267

#snow level
snow_wall = 268
snow_floor_1 = 269
snow_floor_2 = 270

#hell level
hell_wall = 271
hell_floor_1 = 272
hell_floor_2 = 273
hell_pool_small = 274
hell_pool_large = (275, 276, 277, 278)

#alien level
alien_floor_1 = 279
alien_wall_1 = 280
alien_wall_2 = 281
alien_wall_3 = 282
alien_floor_2 = 283
alien_floor_3 = 284

#boss level
boss_wall_1 = 285
boss_wall_2 = 286 #moss
boss_floor_1 = 287 #box
boss_floor_2 = 288 #vent
boss_floor_3 = 289 #stone
boss_floor_4 = 290 #pattern
boss_floor_5 = 291 #normal

#characters
knight = 292
ranger = 293
mage = 294

goblin = 295
goblin_dead = 296
green_slime = 297
tribal = 298
tribal_dead = 299

sand_elemental = 300
stone_golem = 301
stone_golem_dead = 302
sand_slime = 303

water_elemental = 304
water_elemental_dead = 305
evil_snowman = 306
evil_snowman_dead = 307
ice_slime = 308

fire_elemental = 309
imp = 310
imp_dead = 311
fire_slime = 312

alien = 313
alien_dead = 314
ghost = 315
ghost_dead = 316
consumer = 317
consumer_dead = 318

#items
fire_scroll = 320
lightning_scroll = 321
ice_scroll = 322
ice_book = 323
fire_book = 324
lightning_book = 325
wooden_sword = 326
iron_sword = 327
excalibur = 328
bow = 329
demon_bow = 330
shield = 331
ring = 332
major_red_potion = 333
major_green_potion = 334
major_blue_potion = 335
red_potion = 336
blue_potion = 337
green_potion = 338
ice_cream = 339
cola = 340
coin = 341
emerald = 342
amethyst = 343
nuclear_warhead = 344
bomb = 345
door = 346
arcane_scroll = 347


#480
#fireball animation 3x3
blank = " "
fireball_frame1 = (blank, blank, blank,
                    blank, 352, blank,
                    blank, blank, blank,)

fireball_frame2 = (blank, blank, blank,
                    blank, 353, blank,
                    blank, blank, blank)
fireball_frame3 = (354, 355, 356,
                357, 358, 359,
                360, 361, 362)

fireball_frame4 = (363, 364, 365,
                366, 367, 368,
                369, 370, 371)

fireball_frame5 = (372, 373, 374,
                375, 376, 377,
                378, 379, 380)

fireball_frame6 = (381, 382, 383,
                384, 385, 386,
                387, 388, 389)


fireball_animation = [
fireball_frame1,
fireball_frame2,
fireball_frame3,
fireball_frame4,
fireball_frame5,
fireball_frame6,
]

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
color_pointer = libtcod.red



def load_customfont():
     #the index of the first custom tile in the file.
    a = 256

    #The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5,14):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32


class Tile:
    def __init__(self, blocked, tile, block_sight = None):
        self.blocked = blocked
        self.explored = False
        self.tile = tile

        if block_sight is None:
            block_sight = blocked
            self.block_sight = block_sight

class Rect:
    def __init__(self, x, y, w, h):
        #a rectangle on the map. used to characterize a room.
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #generic object for  a player,  a monster, an item etc
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None, score_item = None):
        self.is_target = False
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.score_item = score_item

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.score_item:
            self.score_item.owner = self

    def move(self, dx, dy):
        #move given distance
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

            for object in objects:
                if object.score_item and object.x == player.x and object.y == player.y:
                    object.score_item.pick_up()

    def move_towards(self, target_x, target_y):
        global fov_recompute
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy **2 )

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase character
        libtcod.console_set_char_background(con, self.x, self.y, libtcod.white, libtcod.BKGND_NONE)

    def targeted(self, line_color):
        self.color = line_color
        if self.fighter: #check if target is a fighter
            self.is_target = True

    def clear_targeted(self):
        self.is_target = False


class Fighter:

    def __init__(self, hp, mp, defense, power, magic, xp, score,  corpse=None, death_function=None, stun_recovery = 1, fire_resistance = 0, frost_resistance = 0, air_resistance = 0, earth_resistance = 0):
        self.max_hp = hp
        self.hp = hp

        self.max_mp = mp
        self.mp = mp
        self.defense = defense
        self.power = power
        self.magic = magic
        self.xp = xp
        self.score = score
        self.corpse = corpse
        self.death_function = death_function
        self.stun_recovery = stun_recovery
        self.fire_resistance = fire_resistance
        self.frost_resistance = frost_resistance
        self.air_resistance = air_resistance
        self.earth_resistance = earth_resistance
        self.stunned = 0

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                if self.owner != player:
                    player.fighter.xp += self.xp
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def attack(self, target):
        #simple formula to count attack damage
        damage = self.power - target.fighter.defense
        if damage > 0:
            #make the target take damage
            message(self.owner.name.capitalize() + "attacks " + target.name + " for " + str(damage) + " hit points.")
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + " attacks " + target.name + " but it has no effect!")
    def heal(self, amount):
        #heal the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def regen_mana(self, amount):
        #regen mana the given amount, without going over the maximum
        self.mp += amount
        if self.mp > self.max_mp:
            self.mp = self.max_mp

    def spend_mana(self, amount):
        self.mp -= amount
        if self.mp < 0:
            message("You dont have enough mana to cast that", libtcod.red)
            self.mp += amount

    def recover_status(self):
        self.stunned -= self.stun_recovery
        if self.stunned <= 0:
            self.stunned = 0

    def set_stunned(self, duration, stun_message):
        message(stun_message, libtcod.amber)
        if self.stunned < duration:
            self.stunned = duration

class BasicMonster():
    #ai for basic monster
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.fighter.stunned == 0: #can't attack if stunned
                if monster.distance_to(player) >= 2:
                    monster.move_towards(player.x, player.y)
                elif player.fighter.hp > 0:
                    monster.fighter.attack(player)
        monster.fighter.recover_status()

class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function
    def use(self):
        if self.use_function is None:
            message("The " + self.owner.name + " cannot be used.")
        else:
            if self.use_function(self) != "cancelled":
                inventory.remove(self.owner)
    def pick_up(self):
        if len(inventory) >= 26:
            message("Your inventory is full, cannot pick up" + self.owner.name + ".", libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message("You picked up a " + self.owner.name + "!", libtcod.green)

class Score_item:
    def __init__(self, value):
        self.value = value
    def pick_up(self):
        parent = self.owner
        message("You found " + parent.name + " it's worth " + str(self.value) + " points!", libtcod.gold)
        player.fighter.score += self.value
        objects.remove(self.owner)




class Targetting_functions():
    pass





def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    if header == '':
        header_height = 0

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

     #blit the contents of "window" to the root console
    x = int(SCREEN_WIDTH/2 - width/2)
    y = int(SCREEN_HEIGHT/2 - height/2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

        #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item






def is_blocked(x, y):
    if map[x][y].blocked:
        return True
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    return False

def generate_tile():
    global dungeon_level
    dice = libtcod.random_get_int(0, 0, 100)

    if dungeon_level == 1:
        if dice <= 70:
            tile = jungle_floor_1
        elif dice <= 70 + 20:
            tile = jungle_floor_2
        else:
            tile = jungle_floor_3

    if dungeon_level == 2:
        if dice <= 70:
            tile = sand_floor_1
        else:
            tile = sand_floor_2

    if dungeon_level == 3:
        if dice <= 70:
            tile = snow_floor_1
        else:
            tile = snow_floor_2

    if dungeon_level == 4:
        if dice <= 70:
            tile = hell_floor_1
        else:
            tile = hell_floor_2

    if dungeon_level == 5:
        if dice <= 60:
            tile = alien_floor_2
        elif dice <= 60 + 40:
            tile = alien_floor_3

    if dungeon_level == 6:
        if dice <= 99:
            tile = boss_floor_3
        else:
            tile = boss_floor_2


    return tile

def create_room(room):
    global map

    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            dice = libtcod.random_get_int(0, 0, 100)

            map[x][y].blocked = False
            map[x][y].block_sight = False
            map[x][y].tile = generate_tile()

def create_h_tunnel(x1, x2, y):
    global map
    #vertical tunnel
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        map[x][y].tile = generate_tile()

def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        map[x][y].tile = generate_tile()

def next_level():
    global dungeon_level
    dungeon_level += 1

    #advance to the next level
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%

    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    make_map()  #create a fresh new level!
    initialize_fov()


def generate_wall():
    global dungeon_level
    if dungeon_level == 1:
        wall = jungle_wall
    if dungeon_level == 2:
        wall = sand_wall
    if dungeon_level == 3:
        wall = snow_wall
    if dungeon_level == 4:
        wall = hell_wall
    if dungeon_level == 5:
        dice = libtcod.random_get_int(0, 0, 100)
        if dice <= 34:
            wall = alien_wall_1
        elif dice <= 34 + 33:
            wall = alien_wall_2
        elif dice <= 34 + 33 + 33:
            wall = alien_wall_3
    if dungeon_level == 6:
        dice = libtcod.random_get_int(0,0, 100)
        if dice <= 70:
            wall = boss_wall_1
        else:
            wall = boss_wall_2
    return wall



def make_map():
    global map, objects, dungeon_level, stairs

    #the list of objects with just the player
    objects = [player]

    map = [[ Tile(True, None)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    for y in range(MAP_HEIGHT): #randomize tiles
        for x in range(MAP_WIDTH):
            wall = generate_wall()
            tile = Tile(True, wall)
            map[x][y] = tile


    rooms = []
    num_rooms = 0
    for r in range (MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position, without going outside the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x,y,w,h)
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            create_room(new_room)
            place_objects(new_room)
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:  #first room set player there
                player.x = new_x
                player.y = new_y

            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                if libtcod.random_get_int(0, 0, 1) == 1:
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            rooms.append(new_room)
            num_rooms += 1
    #if dungeon_level < 6:
        #stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white)
        #objects.append(stairs)
        #stairs.send_to_back()


def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    strings = list(chances_dict.keys())
    chances = chances_dict.values()
    index = random_choice_index(chances)
    return strings[index]


def place_objects(room):
#place monster
    global all_monster_chances, dungeon_level, all_monsters, all_item_chances
    monster_chances = all_monster_chances[dungeon_level]

    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOMS_MONSTERS)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        if not is_blocked(x, y):

            choice = random_choice(monster_chances)
            monster = all_monsters[choice]
            name = choice
            tile, hp, mp, defense, power, magic, xp, score, corpse, death_function, stun_recovery, fire_resistance, frost_resistance, air_resistance, earth_resistance = monster


            fighter_component = Fighter(hp, mp, defense, power, magic, xp, score, corpse, death_function, stun_recovery,
                fire_resistance, frost_resistance, air_resistance, earth_resistance)

            ai_component = BasicMonster()
            monster = Object(x, y, tile, name, libtcod.white,
                blocks=True, fighter=fighter_component, ai=ai_component)
            objects.append(monster)


#place items
    item_chances = all_item_chances[dungeon_level]
    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)
    #choose a item in random and repeat it for num_items

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            category = random_choice(item_category_chances) #roll for caregory

             #if score choose from score items
            if category == "score":
                choice = random_choice(score_chances)#roll for item
                item = all_score_items[choice]
                name = choice
                tile, value = item

                score_component = Score_item(value)
                item = Object(x, y, tile, name, libtcod.white, score_item = score_component)

            #if consumable choose from consuable items
            elif category == "consumable":
                choice = random_choice(item_chances)
                item = all_items[choice]
                name = choice
                tile, use_function = item

                item_component = Item(use_function)
                item = Object(x, y, tile, name, libtcod.white, item=item_component)

            objects.append(item)
            item.send_to_back()  #items appear below other objects




def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
            name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    names = [obj.name for obj in objects
    if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.name != None]
    #create a list with names of all the objects in mouse's cordinate and in fov.
    names =  ", ".join(names)
    return names.capitalize()


###############################################################################################
## RENDER_ALL
################################################################################################

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y )
                wall = map[x][y].block_sight
                tile = map[x][y].tile
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, tile, libtcod.grey, libtcod.black)
                        else:
                            libtcod.console_put_char_ex(con, x, y, tile, libtcod.grey, libtcod.black)
                else:
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, tile, libtcod.white, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(con, x, y, tile, libtcod.white, libtcod.black)
                        #since it's visible, explore it
                    map[x][y].explored = True

    #draw objects
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit default console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1


    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)
    render_bar(1, 2, BAR_WIDTH, "MP", player.fighter.mp, player.fighter.max_mp,
        libtcod.light_blue, libtcod.darker_blue)

        #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

#######################################################################################################
#######################################################################################################


def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append((line, color))


def player_move_or_attack(dx, dy):
    global fov_recompute

    fov_recompute = True

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break


    #attack if target found, move otherwise

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)


def check_level_up():
    #see if experience is enough to level up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -= level_up_xp
        message("Your skills have improved You reached level " +str(player.level) + "!", libtcod.yellow)
        choice = None
        while choice == None: #keep asking until choise is made
            choice = menu('Level up! Choose a stat to raise:\n',
                ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                'Agility (+1 defense, from ' + str(player.fighter.defense) + ')',
                'Magic (+1 magic from' + str(player.fighter.magic) + ')'], LEVEL_SCREEN_WIDTH)
        if choice == 0:
            player.fighter.max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.power += 1
        elif choice == 2:
            player.fighter.defense += 1
        elif choice == 3:
            player.fighter.magic += 1


def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message(monster.name.capitalize() + ' is dead!', libtcod.orange)
    if monster.fighter.corpse:
        monster.char = monster.fighter.corpse
        monster.name = 'remains of ' + monster.name
        monster.send_to_back()
        monster.blocks = False
        monster.fighter = None
        monster.ai = None
    else:
        objects.remove(monster)


def closest_monster(max_range):
    #find the closest enemy, up to maximum ranege, and in the player's fov
    closest_enemy = None
    closest_dist = max_range + 1 #start with(slighty more than) maximum range
    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy


def cast_heal(item):
    if player.fighter.hp == player.fighter.max_hp:
        message("You are already at full health.", libtcod.red)
        return "cancelled"
    amount_healed = libtcod.random_get_int(0, MIN_HEAL, MAX_HEAL)
    message("Your wounds start to feel better. " + item.owner.name.capitalize() +" heals you for " + str(amount_healed), libtcod.green)
    player.fighter.heal(amount_healed)

def cast_regen_mana(self):
    if player.fighter.mp == player.fighter.max_mp:
        message("You are already at full mana." , libtcod.red)
        return "cancelled"
    mana_gained = libtcod.random_get_int(10, MAX_HEAL)
    message("Some of your mana has been recharged. " +  "You gain  " + str(amount_healed) +  " Mana points", libtcod.green)
    player.fighter.regen_mana(mana_gained)

def cast_lightning(self):
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None: #no enemy, in range
        message('No enemy in range', libtcod.red)
        return 'cancelled'
    #strike
    message('A lightning bolt strikes the ' +monster.name + ' with a loud thunder! The damage is '
        + str(LIGHTNING_DAMAGE) + 'hit points.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_fireball(self):
    global fov_recompute

    boolean, pattern, line = spell_targetting(player, FIREBALL)
    damage = FIREBALL["damage"]

    if boolean == True:
        for obj in objects:
            if obj.is_target:
                message('The ' + obj.name + ' gets burned for ' + str(damage) + ' hit points.', libtcod.orange)
                obj.fighter.take_damage(damage)
        clear_targets()
##      Animation

        for frame in fireball_animation: #num of frames
            i = 0
            for tile in frame:
                x, y = pattern[i]
                libtcod.console_put_char(con, x, y, tile, libtcod.BKGND_NONE)
                i = i + 1
            libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
            libtcod.console_flush() #flush a frame

        fov_recompute = True #remove the explotion
        render_all()
        libtcod.console_flush()

    else:
        clear_targets()
        return "cancelled"

def cast_freeze(self):
    global fov_recompute

    boolean, pattern  = spell_targetting(player, FREEZE)
    damage = FREEZE["damage"]
    duration = FREEZE["duration"]

    if boolean == True:
        for obj in objects:
            if obj.is_target:
                message('The ' +obj.name + ' freezes in place and sufferes ' + str(damage) + ' hit points', libtcod.azure)
                obj.fighter.take_damage(damage)
                stun_message = 'The '+obj.name+ ' is frozen for '+ str(duration) +' turns'
                obj.fighter.set_stunned(duration, stun_message)
        clear_targets()
    else:
        clear_targets()
        return "cancelled"

def cast_arcane_beam(self):
    global fov_recompute

    boolean, line = spell_targetting(player, ARCANE_BEAM)
    DAMAGE = ARCANE_BEAM["damage"]
    if boolean == True:
        for obj in objects:
            if obj.is_target:
                message("The " +obj.name + " gets harmed by arcane beam for " + str(DAMAGE) + " hit points", libtcod.crimson)
                obj.fighter.take_damage(DAMAGE)
        clear_targets()
    else:
        clear_targets()
        return "cancelled"

def cast_bomb(self):
    global fov_recompute
    boolean, pattern = spell_targetting(player, BOMB)
    DAMAGE = BOMB["damage"]
    if boolean == True:
        for obj in objects:
            if obj.is_target:
                message("The " +obj.name + " gets hit by the explotion for  " + str(DAMAGE) + " hit points", libtcod.orange)
                obj.fighter.take_damage(DAMAGE)
        clear_targets()
        #animation
        for frame in fireball_animation: #num of frames
            i = 0
            for tile in frame:
                x, y = pattern[i]
                libtcod.console_put_char(con, x, y, tile, libtcod.BKGND_NONE)
                i = i + 1
            libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
            libtcod.console_flush() #flush a frame

        fov_recompute = True #remove the explotion
        render_all()
        libtcod.console_flush()
    else:
        clear_targets()
        return "cancelled"





############################################################################################################
## SPELL TARGETTING FUNCTION
############################################################################################################

def clear_targets():
    for object in objects:
         object.clear_targeted()

def clear_marked():
    for object in objects:
        object.color = libtcod.white


def spell_targetting(caster, spell):
    #Static variables

    MAX_RANGE = spell["max_range"]
    MOVABLE = spell["movable"]
    SPELL_PENE = spell["spell_pene"]
    PATTERN = spell["pattern"]
    LINE_COLOR = spell["line_color"]
    PATTERN_COLOR = spell["pattern_color"]

    def distance(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return math.sqrt(dx ** 2 + dy ** 2)

    def check_for_target_collision(x, y, object, color):
        if object.x == x and object.y == y: #check if line hits object, and target it.
            object.targeted(color)

    def check_for_spell_penetration(x, y, object):
        if object.x == x and object.y == y:
            if (SPELL_PENE == False) and object.fighter:
                return True
        return False

    def check_for_collition(x,y):
         #check if tile is blocked
        if map[x][y].blocked:
            return True
        #check if mouse line has reached mouse or if mouse is in max range
        if MAX_RANGE <= distance(player.x, player.y, x, y) or (x == mouse.cx and y == mouse.cy):
            return True
        return False

    def draw_line(x, y):

        def check_line_collition(x,y):
            stop = False
            # if draws a line, check if line x and y collide with enemy target
            if LINE_COLOR:
                libtcod.console_set_char_foreground(con, x, y, LINE_COLOR)
                for object in objects:
                    if object != caster:
                        check_for_target_collision(x, y, object, LINE_COLOR)
                        stop = check_for_spell_penetration(x, y, object)
                        if stop:
                            break
            if stop == False:
                stop = check_for_collition(x,y)
            return stop


        libtcod.line_init(player.x, player.y, x, y) #initialize a new line
        x, y = libtcod.line_step()

        if x == None:       #special case
            x = caster.x
            y = caster.y

        stop = check_line_collition(x, y)
        line = []
        line.append((x, y))

        while not stop:
            x, y = libtcod.line_step()
            line.append((x,y))
            stop = check_line_collition(x, y)

        return line, x, y

        #if line x, y hasn't collided with a monster, check if it collides with a wall or has reach the mouse position.


    def draw_targeting_pattern(x, y):
        pattern = []
        for cel in PATTERN: #count new x and y for each cel in pattern
            c_x, c_y = cel
            c_x = c_x + x
            c_y = c_y + y
            new_cel = (c_x, c_y)
            pattern.append(new_cel)
        for cel in pattern: #draw tagetting pattern and target objects in it
            c_x, c_y, = cel
            libtcod.console_set_char_foreground(con, c_x, c_y, PATTERN_COLOR)
            for object in objects:
                check_for_target_collision(c_x, c_y, object, PATTERN_COLOR)
        return pattern

    def draw_new_pattern(x, y):
        line, p_x, p_y = draw_line(x,y)

        if PATTERN:
            pattern = draw_targeting_pattern(p_x, p_y)
            return pattern, line
        else:
            return False, line


    def clear_old_pattern():
        global fov_recompute
        fov_recompute = True
        clear_marked()
        clear_targets()
        render_all()


    def target_movable_Spell(): #always cast by player
        global key, mouse
        global fov_recompute

        is_spell_cast = None
        pattern, line = draw_new_pattern(mouse.cx, mouse.cy)
        render_all()
        libtcod.console_flush()

        while True:
            x = mouse.cx
            y = mouse.cy
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse) #update the mouse status

            if x != mouse.cx or y != mouse.cy: #if mouse moved. remove the line and targets
                clear_old_pattern()
                pattern, line = draw_new_pattern(mouse.cx, mouse.cy)
                render_all()
                libtcod.console_flush()

            if mouse.lbutton_pressed:
                fov_recompute = True
                is_spell_cast = True
                clear_marked()
                render_all()

            if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
                fov_recompute = True
                is_spell_cast = False
                clear_marked()
                render_all()

            if is_spell_cast != None:
                if PATTERN and LINE_COLOR:  #return pattern and lines for drawing possible animations
                    return is_spell_cast, pattern, line
                if PATTERN:
                    return is_spell_cast, pattern
                if LINE_COLOR:
                    return is_spell_cast, line

    if caster == player and MOVABLE:
        retu = target_movable_Spell()
    return retu

#############################################################################################################
#############################################################################################################

def handle_keys():
    global key, fov_recompute

    player.fighter.recover_status()

    if player.fighter.stunned != 0:
        pass

    if key.vk == libtcod.KEY_ENTER and key.lalt: #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return "exit"  #exit game

    if game_state == 'playing':
        #Movement keys
        key_char = chr(key.c)

        if key.vk == libtcod.KEY_UP:
            player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT:
            player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT:
            player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_TAB:
            pass  #do nothing ie wait for the monster to come to you
            fov_recompute = True
        else:
            #test for other keys
            if key_char == "e":
                #pick up an item
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
            if key_char == 'i':
                #show the inventory
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
            if key_char == '<':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                    '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' + str(player.fighter.defense) +
                    '\nMagic: ' + str(player.fighter.magic), CHARACTER_SCREEN_WIDTH)
            return "didnt-take-turn"


#######################################################
# Initialization & Main Loop
#######################################################


libtcod.console_set_custom_font("TiledFont_organised.png", libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)
load_customfont()
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Gamer Quest", False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_key_color(con, libtcod.white)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

monster_chances_jungle = {"goblin" : 50, "tribal" : 30, "green slime" : 20}
monster_chances_sand = {"sand elemental" : 50, "sand slime" : 30, "stone golem" : 20}
monster_chances_ice = {"water elemental" : 50, "ice slime" : 30, "evil snowman" : 20}
monster_chances_hell = {"imp" : 50, "fire slime" : 30, "fire elemental" : 20}
monster_chances_alien = {"alien"  : 50, "consumer" : 30, "ghost" : 20}
monster_chances_boss = {"monster1"  : 50, "monster2" : 30, "monster3" : 20} #set these later
all_monster_chances =  {1 : monster_chances_jungle, 2 : monster_chances_sand, 3 : monster_chances_ice, 4 : monster_chances_hell, 5 : monster_chances_alien, 6 : monster_chances_boss}

all_monsters = {
                #tile, hp, mp, defense, power, magic, xp, score, corpse, death_function, stun_recovery, fire_resistance, frost_resistance, air_resistance, earth_resistance
    "goblin" : (goblin, 10, 0, 0, 3, 0, 20, 50,  goblin_dead, monster_death, 1, 0, 0, 0, 0),
    "tribal" : (tribal, 5, 0, 0, 5, 0, 50, 75, tribal_dead, monster_death, 1, 0, 0, 0, 0),
    "green slime" : (green_slime, 10, 0, 3, 3, 0, 75, 100, None, monster_death, 1, 0, 0, 0, 0),

    "sand elemental" : (sand_elemental, 20, 0, 6, 150, 50, 0, None, monster_death, 1, 0, 0, 10, 10),
    "sand slime" : (sand_slime, 15, 2, 6, 100, 35, 0, None, monster_death, 1, 0, 0, 0, 10),
    "stone golem" : (stone_golem, 30, 3, 6, 200, 50, 0, stone_golem_dead, monster_death, 1, 0, 0, 0, 10),

    "water elemental" : (water_elemental, 30, 0, 8, 250, 0, water_elemental_dead, monster_death, 2, 0, 10, 0, 0),
    "ice slime" : (ice_slime, 20, 3, 7, 200, 100, 0, None, monster_death, 1, 0, 10, 0, 0),
    "evil snowman" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),

    "imp" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "fire slime" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "fire elemental" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),

    "alien" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "consumer" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "ghost" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),

    "monster1" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "monster2" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
    "monster3" : (evil_snowman, 20, 0, 5, 300, 100, 0,  None, monster_death, 1, 0, 10, 0, 0),
}

#itmes
item_category_chances = {"score" : 60, "consumable" : 40}
score_chances = {"gold coin" : 69, "amethyst" : 20, "emerald" : 9, "strange artifact" : 1}
consuable_chances = {"healing potion" : 30, "mana potion" : 20, "fireball scroll" : 10, "arcane scroll" : 10, "freeze scroll" : 10, "shock scroll" : 10, "bomb" : 10}

all_score_items = {
    "gold coin" : (coin, 50),
    "amethyst" : (amethyst, 500),
    "emerald" : (emerald, 2000),
    "strange artifact" :(nuclear_warhead ,10000),
}

all_items = {
    "healing potion" : (red_potion, cast_heal),
    "mana potion" : (blue_potion, cast_regen_mana),
    "bomb" : (bomb, cast_bomb),
    "scroll of fireball" : (fire_scroll, cast_fireball),
    "scroll of lightning" : (lightning_scroll, cast_lightning),
    "scroll of freeze" : (ice_scroll, cast_freeze),
    "scroll of arcane beam" : (arcane_scroll, cast_arcane_beam),
    "major healing potion" : (major_red_potion, cast_heal), #edit later
    "major mana potion" : (major_blue_potion, cast_regen_mana), #
    "gamer quest cola" : (cola, cast_heal), #
    "ice cream" : (ice_cream, cast_heal), #
}

##ALL ITEM SPAWN CHANCES FOR EVERY LEVEL
item_chances_jungle = {
    "healing potion" : 20, "mana potion" : 10, "bomb" : 30, "scroll of fireball" : 10, "scroll of lightning" : 10,
    "scroll of freeze" : 10, "scroll of arcane beam" : 10
}
item_chances_sand = {
    "healing potion" : 15, "mana potion" : 7, "bomb" : 30, "scroll of fireball" : 10, "scroll of lighning" : 10,
    "scroll of freeze" : 10, "scroll of arcane beam" : 10, "major healing potion" : 5, "major mana potion" : 3
}
item_chances_ice = {
  "ice cream" : 8, "mana potion" : 5, "bomb" : 30, "scroll of fireball" : 10, "scroll of lighning" : 10,
  "scroll of freeze" : 10, "scroll of arcane beam" : 10, "major healing potion" : 8, "major mana potion" : 5,
  "gamer quest cola" : 4
}
item_chances_hell  = {
  "healing potion" : 5, "mana potion" : 3, "bomb" : 30, "scroll of fireball" : 10, "scroll of lighning" : 10,
  "scroll of freeze" : 10, "scroll of arcane beam" : 10, "major healing potion" : 10, "major mana potion" : 7,
  "gamer quest cola" : 5
}
item_chances_alien  = {
  "bomb" : 30, "scroll of fireball" : 10, "scroll of lighning" : 10,
  "scroll of freeze" : 10, "scroll of arcane beam" : 10, "major healing potion" : 15, "major mana potion" : 10,
  "gamer quest cola" : 5
}
item_chances_boss  = {
  "bomb" : 30, "scroll of fireball" : 10, "scroll of lighning" : 10,
  "scroll of freeze" : 10, "scroll of arcane beam" : 10, "major healing potion" : 10, "major mana potion" : 10,
  "gamer quest cola" : 10
}
all_item_chances = {1 : item_chances_jungle, 2 : item_chances_sand, 3 : item_chances_ice, 4 : item_chances_hell, 5 : item_chances_alien, 6 : item_chances_boss}


def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file["player_index"] = player #index of player in objects list
    file["inventory"] = inventory
    file["game_msgs"] = game_msgs
    file["game_state"] = game_state
    file.close()

def load_game():
    #open the previously saved shelve and load the game data
    global map, objects, player, inventory, game_msgs, game_state

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    file.close()

    initialize_fov()

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def main_menu():
    #img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        #libtcod.image_blit_2x(img, 0, 0, 0)

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()

        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()

        elif choice == 2:  #quit
            break


def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level

    #create object representing the player
    fighter_component = Fighter(hp=30, mp=30, defense=2, power=30, magic=1, xp=0, score=0, death_function=player_death)
    player = Object(0, 0, mage, "player", libtcod.white, blocks=True, fighter=fighter_component)
    player.level = 1

    dungeon_level = 1

    #generate map
    make_map()

    initialize_fov()

    game_state = "playing"
    inventory = []

    #create the list of game messages and their colors
    game_msgs = []

    #create a list of objects. starting with the player
    objects = [player]

    #test, welcoming message!
    message('Welcome to gamer dungeon adventurer, stay as long as you like or stay FOREVER!', libtcod.red)


def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True
    libtcod.console_clear(con)

    #create the fov map, acording to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

def play_game():
    global key, mouse

    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

        libtcod.console_flush()

        check_level_up()

        for object in objects: #clear all the objects
            object.clear()

        player_action = handle_keys()
        if player_action == "exit":
            save_game()
            break

        if game_state == "playing" and player_action != "didnt-take-turn":
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

#show the game's title, and some credits!
libtcod.console_set_default_foreground(0, libtcod.light_yellow)
libtcod.console_print_ex(0, int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2-4), libtcod.BKGND_NONE, libtcod.CENTER, 'GAMER QUEST')
libtcod.console_print_ex(0, int(SCREEN_WIDTH/2), SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Milo Komulainen & Markus Suomela')

main_menu()

