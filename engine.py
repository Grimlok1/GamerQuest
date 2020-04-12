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

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

#spell amount
MIN_HEAL = 1
MAX_HEAL = 20
LIGHTNING_DAMAGE = 20
LIGHTNING_RANGE = 5

FIREBALL_RANGE = 8
FIREBALL_TARGETING_TYPE = 'lollipop'
FIREBALL_DAMAGE = 12
FIREBALL_IMPACT_AREA = (-1, -1, 2, 2)  # 3x3
impact = None

FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

LIMIT_FPS = 20  #20 frames-per-second maximum

MAX_ROOMS_MONSTERS = 3
MAX_ROOM_ITEMS = 2

#for GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

INVENTORY_WIDTH = 50


#custom tiles
wall_tile = 256
floor_tile = 257
player_tile = 258
orc_tile = 259
troll_tile = 260
scroll_tile = 261
healingpotion_tile = 262
sword_tile = 263
shield_tile = 264
stairsdown_tile = 265
dagger_tile = 266
fireball_scroll_tile = 267

#fireball animation 3x3
blank = " "

fireball_frame1 = (blank, blank, blank,
                    blank, 288, blank,
                    blank, blank, blank,)

fireball_frame2 = (blank, blank, blank,
                    blank, 289, blank,
                    blank, blank, blank)

fireball_frame3 = (290, 291, 292,
                293, 294, 295,
                296, 297, 298)

fireball_frame4 = (299, 300, 301,
                302, 303, 304,
                305, 306, 307)

fireball_frame5 = (308, 309, 310,
                311, 312, 313,
                314, 315, 316)

fireball_frame6 = (317, 318, 319,
                320, 321, 322,
                323, 324, 325)


fireball_animation = [
fireball_frame1,
fireball_frame2,
fireball_frame3,
fireball_frame4,
fireball_frame5,
fireball_frame6,
]


def load_customfont():
     #the index of the first custom tile in the file.
    a = 256

    #The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5,8):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32


color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
color_pointer = libtcod.red


class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

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
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None, item = None):
        self.is_target = False
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
    def move(self, dx, dy):
        #move given distance
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
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
        libtcod.console_put_char(con, self.x, self.y, " ", libtcod.BKGND_NONE)

    def targeted(self, line_color):
        self.color = line_color
        if self.ai: #check if target is a monster
            self.is_target = True

    def clear_targeted(self):
        self.is_target = False


class Fighter:
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function
    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
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
            messsage(self.owner.name.capitalize() + " attacks " + target.name + " but it has no effect!")
    def heal(self, amount):
        #heal the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster():
    #ai for basic monster
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function
    def use(self):
        if self.use_function is None:
            message("The " + self.owner.name + " cannot be used.")
        else:
            if self.use_function(self = None) != "cancelled":
                inventory.remove(self.owner)
    def pick_up(self):
        if len(inventory) >= 26:
            message("Your inventory is full, cannot pick up" + self.owner.name + ".", libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message("You picked up a " + self.owner.name + "!", libtcod.green)





def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

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

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global map
    #vertical tunnel
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map():
    global map


    map = [[Tile(True) #fill map with blocked tiles
        for y in range(MAP_HEIGHT)]
            for x in range(MAP_WIDTH) ]
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
##            room_no = Object(new_x, new_y, chr(65+num_rooms), 'room number', libtcod.white)
##            objects.insert(0, room_no)
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

def place_objects(room):
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOMS_MONSTERS)
    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
        if not is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) < 80:

                #create an orc
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x, y, orc_tile, "orc", libtcod.white,
                    blocks=True, fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
                ai_component = BasicMonster()
                monster = Object(x, y, troll_tile, "Troll", libtcod.white,
                    blocks=True, fighter=fighter_component, ai=ai_component)
            objects.append(monster)
        #choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            #trow a dice
            dice = libtcod.random_get_int(0, 0, 100)
##            if dice < 70:
##                item_component = Item(use_function=cast_heal)
##                item = Object(x, y, healingpotion_tile, 'healing potion', libtcod.white, item=item_component)
##            elif dice < 70 + 10:
##                #create a lightning bolt scroll(30% chance)
##                item_component = Item(use_function=cast_lightning)
##                item = Object(x, y, scroll_tile, 'scroll of lightning bolt', libtcod.white, item=item_component)
            if dice < 70:
                #create a fire bolt scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x,y, fireball_scroll_tile, "scroll of fireball", libtcod.white, item=item_component)

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

def render_cursor():
    global mouse
    libtcod.console_clear(cursos_panel) #clear old
    libtcod.console_set_char_background(cursos_panel, mouse.cx, mouse.cy, color_pointer, libtcod.BKGND_SET)

def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    names = [obj.name for obj in objects
    if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
    #create a list with names of all the objects in mouse's cordinate and in fov.
    names =  ", ".join(names)
    return names.capitalize()

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global animation_playing

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y )
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.grey, libtcod.black)
                        else:
                            libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.grey, libtcod.black)
                else:
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, wall_tile, libtcod.white, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(con, x, y, floor_tile, libtcod.white, libtcod.black)
                        #since it's visible, explore it
                    map[x][y].explored = True

    #draw objects
    if animation_playing == False:

        for object in objects:
            if object != player:
                object.draw()
        player.draw()

    animation_playing = False

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

        #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append((line, color))




def player_move_or_attack(dx, dy):
    global fov_recompute

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
        fov_recompute = True

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
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

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
    message("Your wounds start to feel better. " + item.owner.name.capitalize() +" heals you for " + str(amount_healed), libtcod.light_violet)
    player.fighter.heal(amount_healed)

def cast_lightning():
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
    global animation_playing

    message("you beging to channel the fireball", libtcod.desaturated_flame)
    boolean, impact = spell_targetting(FIREBALL_RANGE, FIREBALL_TARGETING_TYPE, FIREBALL_IMPACT_AREA)
    print(impact)
    if boolean == True:
        for obj in objects:
            if obj.is_target:
                message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
                obj.fighter.take_damage(FIREBALL_DAMAGE)

        clear_targets()
##      Animation
        x1, y1, x2, y2 = impact
        current_frame = 0
        for frame in fireball_animation: #num of frames
            dx = 0
            dy = 0

            for cel in frame:
                libtcod.console_put_char(con, x1 + dx, y1 + dy, cel, libtcod.BKGND_SET)
                if dx < 2: #x1 + dx < x2
                    dx = dx + 1
                else:
                    dx = 0
                    dy = dy + 1
            animation_playing = True
            render_all()
            libtcod.console_flush() #flush a frame
            current_frame = current_frame + 1

        fov_recompute = True #remove the explotion
        render_all()
        libtcod.console_flush()

    else:
        clear_targets()
        return "cancelled"



def clear_targets():
    for object in objects:
         object.clear_targeted()

def clear_marked():
    for object in objects:
        object.color = libtcod.white

def spell_targetting(MAX_RANGE, SPELL_TARGETING_TYPE, IMPACT_AREA=None, SPELL_PENETRATON=None):

    def distance(x1, y1, x2, y2):
     dx = x1 - x2
     dy = y1 - y2
     return math.sqrt(dx ** 2 + dy ** 2)
##
##    def draw_circle_impact(x,y):
##        dec = int((IMPACT_AREA - 1) / 2) #decrease to get to upper corner, from center
##        x1 = x - dec
##        y1 = y - dec
##        x2 =  x + IMPACT_AREA
##        y2 = y + IMPACT_AREA
##
##        for x in range(x1, x2):
##            for y in range(y1, y2):
##
##                libtcod.console_set_char_background(cursos_panel, x, y, libtcod.green, libtcod.BKGND_SET)
##                #check if object is targeted
##                for object in objects:
##                   if object.ai and (object.x == x and object.y == y):
##                       targets.append(object)

##    def draw_line_impact(x,y):
##
##
##        inc = int((IMPACT_AREA - 1)/ 2)
##
##        for x in range(x1, x2):
##            for y in range(y1, y2):
##                libtcod.console_set_char_background(cursos_panel, x, y, libtcod.green, libtcod.BKGND_SET)
##                #check targeted objects
##                for object in objects: #check if object is targeted
##                   if object.ai and (object.x == x and object.y == y):
##                       targets.append(object)

##    def lollipop_spell_listener(x,y):
##        tile = map[x][y]
##        if is_spell_blocked(x,y) or MAX_RANGE <= distance(player.x, player.y, x, y) or (x == mouse.cx and y == mouse.cy): #tile is blocked(and you dont have spell penetration) stop the line, or max range has been reached
##            libtcod.console_set_char_background(cursos_panel, x, y, color_pointer, libtcod.BKGND_SET)#set the last tile to red.
##            draw_circle_impact(x,y) #draw the impact area.
##            return False
##        if not(player.x == x and player.y == y):
##            libtcod.console_set_char_background() #color line tile red
##        return True

##    def circle_spell_listener(x,y):
##        tile = map[x][y]
##        if is_spell_blocked(x,y) or MAX_RANGE <= distance(player.x, player.y, x, y) or (x == mouse.cx and y == mouse.cy): #tile is blocked(and you dont have spell penetration) stop the line, or max range has been reached
##            draw_circle_impact(x,y) #draw the impact area.
##            return False
##        return True

    def draw_impact(x,y):
        global impact
        #draw rectangle
        dx1, dy1, dx2, dy2 = IMPACT_AREA

        x1 = x + dx1
        y1 = y + dy1
        x2 = x + dx2
        y2 = y + dy2

        impact = (x1, y1, x2, y2)


        for x in range(x1, x2):
            for y in range(y1, y2):
                libtcod.console_set_char_foreground(con, x, y, libtcod.green)
                for object in objects:
                   if object.ai and (object.x == x and object.y == y):
                    object.targeted(libtcod.green)


    def draw_lollipop(x,y):
        line_color = libtcod.red #might move this to constan
        libtcod.console_set_char_foreground(con, x, y, line_color)

        #check if line colides with objects.
        for object in objects:
            if object != player and (object.x == x and object.y == y): #check if line hits object
                if not(SPELL_PENETRATON) and object.ai: #check for spell pene
                    draw_impact(x,y)
                    return False

        #check if tile is blocked
        if map[x][y].blocked:
            draw_impact(x,y)
            return False

        #check if mouse line has reached mouse or if mouse is in max range
        if MAX_RANGE <= distance(player.x, player.y, x, y) or (x == mouse.cx and y == mouse.cy):
            draw_impact(x,y)
            return False

        return True

    def draw_line(x,y):
        line_color = libtcod.green #might move this to constan
        libtcod.console_set_char_foreground(con, x, y, line_color)

        #check if line colides with objects.
        for object in objects:
            if object != player and (object.x == x and object.y == y): #check if line hits object
                object.targeted(line_color) #target object
                if not(SPELL_PENETRATON) and object.ai: #check for spell pene
                    return False

        #check if tile is blocked
        if map[x][y].blocked:
            return False

        #check if mouse line has reached mouse or if mouse is in max range
        if MAX_RANGE <= distance(player.x, player.y, x, y) or (x == mouse.cx and y == mouse.cy):
            return False

        return True


##            if SPELL_TARGETING_TYPE == 'lollipop':
##
##                libtcod.line(player.x, player.y, mouse.cx, mouse.cy, lollipop_spell_listener)

##            elif SPELL_TARGETING_TYPE == "circle":
##
##                libtcod.line(player.x, player.y, mouse.cx, mouse.cy, circle_spell_listener)

    if SPELL_TARGETING_TYPE == 'line':
        iter_func = draw_line
    elif SPELL_TARGETING_TYPE == 'lollipop':
        iter_func = draw_lollipop
    elif SPELL_TARGETING_TYPE == 'chain':
        iter_func = draw_chain

    global key, mouse
    global fov_recompute
    global impact




    #remove inventory
    libtcod.line(player.x, player.y, mouse.cx, mouse.cy, iter_func) #draws first line
    render_all() #render line
    libtcod.console_flush()
    is_spell_cast = None #return if spell was cast or not


    while True:
        x = mouse.cx
        y = mouse.cy
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse) #update the mouse status

        if x != mouse.cx or y != mouse.cy: #if mouse moved. remove the line and targets

            #clear old line
            fov_recompute = True
            clear_marked()
            clear_targets()
            render_all()

            #draw newline
            libtcod.line(player.x, player.y, mouse.cx, mouse.cy, iter_func) #iterator that draws the line
            render_all()
            libtcod.console_flush()

        if mouse.lbutton_pressed:
            fov_recompute = True
            is_spell_cast = True
            clear_marked()

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            fov_recompute = True
            is_spell_cast = False
            clear_marked()



        if is_spell_cast != None:
            return is_spell_cast, impact






##            elif SPELL_TARGETING_TYPE == "chain":
##                libtcod.line(player.x, player.y, mouse.cx, mouse.cy, chain_spell_listener)







def handle_keys():
    global fov_recompute
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt: #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return "exit"  #exit game
    if game_state == 'playing':
        if key.vk == libtcod.KEY_UP:
            player_move_or_attack(0, -1)


        elif key.vk == libtcod.KEY_DOWN:
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT:
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT:
            player_move_or_attack(1, 0)

        else:
            #test for other keys
            key_char = chr(key.c)
            if key_char == "g":
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
            return "didnt-take-turn"

#######################################################
# Initialization & Main Loop
#######################################################


libtcod.console_set_custom_font("TiledFont.png", libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)
load_customfont()
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Gamer Quest", False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)


#create object representing the player
fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = Object(0, 0, player_tile, "player", libtcod.white, blocks=True, fighter=fighter_component)

#create a list of objects. starting with the player
objects = [player]

#generate map
make_map()

#create the fov map, acording to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
animation_playing = False
game_state = 'playing'
player_action = None

#empty list to store game messages and their colors
game_msgs = []

#test, welcoming message!
message('Welcome to gamer dungeon adventurer, stay as long as you like or stay FOREVER!', libtcod.red)

mouse = libtcod.Mouse()
key = libtcod.Key()

#set inventory
inventory = []

def main():
    global objects
    global game_state



    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        #libtcod.console_set_default_foreground(0, libtcod.white)
        render_all() #draw everything

        libtcod.console_flush()
        for object in objects: #clear all the objects
            object.clear()

        player_action = handle_keys()
        if game_state == "playing" and player_action != "didnt-take-turn":
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
        if player_action == "exit":
            break


if __name__ == '__main__':
    main()
