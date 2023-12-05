#Pac-Man
import copy #for copying game objects
from board import boards #the actual pacman game board
import pygame #for access to video game variables
import math #doing calculations/drawing the curves on the grid
#the code isn't super optimized

pygame.init() #initialize pygame
#setting variables
WIDTH = 900#the width and height of the game
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])#display the game at the given size
timer = pygame.time.Clock()#the speed the game runs at
fps = 60#max speed
font = pygame.font.Font('freesansbold.ttf', 20)#font used for ingame text
level = copy.deepcopy(boards)#the board.py file
color = 'blue'#the color of the grid
PI = math.pi
player_images = [] #pacman images list
for i in range(1, 5):#load the images into a list and set their scale
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))
blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))#ghost images
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange (2).png'), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))#dark blue scared sprite
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))#floating eyes image
player_x = 450#pacmans starting position
player_y = 663
direction = 0#the direction we face at the start of the game
blinky_x = 56#starting position for all of the ghosts and their facing directions
blinky_y = 58
blinky_direction = 0
inky_x = 440
inky_y = 388
inky_direction = 2
pinky_x = 440
pinky_y = 408
pinky_direction = 2
clyde_x = 440
clyde_y = 438
clyde_direction = 2
counter = 0#this is used to cycle between pacmans sprites
flicker = False#the variable that controls the flickering of the large powerups
# R, L, U, D
turns_allowed = [False, False, False, False]#this is used to determine if pacman can turn in a given direction
direction_command = 0#the direction that we tell the game we want to move in
player_speed = 2#the speed that pacman moves at
score = 0#the score value
powerup = False#determines if we're in a powered up state where we can eat the ghosts
power_counter = 0#number of powerups eaten
eaten_ghost = [False, False, False, False]#this determines whether the ghosts have been eaten or not
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
#all the ghosts target the player by default
blinky_dead = False#track if the ghosts are dead
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False#this tracks if the ghosts are in the center box or not
inky_box = False
clyde_box = False
pinky_box = False
moving = False#determines if we're allowed to move
ghost_speeds = [2, 2, 2, 2]#the speed that the ghosts move at
startup_counter = 0# the counter at the start of the game that stops you from moving for a couple seconds
lives = 3#number of starting bonus lives you have
game_over = False#used to determine if we've won or lost the game
game_won = False


class Ghost:#the class that holds the data for the ghosts
    #self refers to the instance of the class so we can access the variables inside of it
    #_init initializes the variables of the object the moment its created
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        #this defines what a ghost is, every frame we set each ghost to the ghost class with their respective variables
        #these variables are updated every frame
        #x/y coords, who the ghost target, their speed and appearance, their direction, whether their dead or in the box, and a unique id for each ghost
        self.x_pos = x_coord#we set each variable to the coresponding variable thats passed into the function
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22#this is the center of the ghost, similar to how we got the center of the player
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()#the ghost will use the same collision check the player uses
        self.rect = self.draw()

    #General Rundown(called every frame in the ghost class which each ghost calles every frame
    #We show different sprited based on if the ghost is scared/dead/neither
    #We return ghost_rect which is the hitbox of the ghost that is used for collisions
    #We also set the sprite of the ghost accordin to the ghosts id and theirs a powerup active or if their eaten
    def draw(self):#this controls which sprite the ghost display in the game
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            #if theres no powerup active and the ghost isnt dead
            #Or if the ghost was just eaten and came back to life while a powerup was active
            screen.blit(self.img, (self.x_pos, self.y_pos))#the ghost will use their normal sprite by default
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            #if a powerup is active and the ghost is alive and not dead
            #the ghost will use there scared sprite
            screen.blit(spooked_img, (self.x_pos, self.y_pos))#if a powerup is active and the ghost is still alive
            #show the scared sprite
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))#otherwise show the dead sprite with the floating eyes
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))#hitbox of the ghosts
        #were defining the side of the rectangle with 2 sets of tuples, you give 2 numbers for where you start
        #in this case the center of the ghost
        #and you give 2 vars for how tall and wide you want the rectange to be
        #We dont want the hitbox to be seen so we just use rect.rect and not draw.rect
        return ghost_rect

    #General Rundown(Called every frame for every ghost)
    #ghost handle collisions similar to pacman (around line 364)
    #the main difference with this movement code for the ghost is that it lets the ghosts move through the white ghost door
    #that the player isn't allowed to move through
    #here we set the direction the cooresponding ghost turn boolean true if they're facing the empty tile
    #this is different from the players logic where there we checked the space behind the player
    #this function returns the turns and in_box variable so the ghost knows every frame what directions it can turn in
    #and if its in the center box
    def check_collisions(self):#ghost collisions are similar to how the player handles collisions
        # R, L, U, D
        num1 = ((HEIGHT - 50) // 32) #the height of the tile that scales off the screen size(about 26)
        num2 = (WIDTH // 30) #the width of the tile that scales off the screen size(about 30)
        num3 = 15 #the offset used to check for tiles around the ghost
        #the ghosts have similar dimentions to pacman
        # meaning we can reuse the same values to check ghost collisions with the board
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:#if the ghost is on the grid
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:#if the white ghost door is above the ghost
                self.turns[2] = True #allow the ghost to move up
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                #if the only stuff to the left of us is empty space or pellets, we can turn left
                #if the only stuff to the left of us is the white ghost door and were in the center box
                # or dead as ghost
                self.turns[1] = True#the ghost can turn left, repeat this logic for all the other directions
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:#similar to player collision
                # if the ghost is moving up/down
                if 12 <= self.center_x % num2 <= 18:
                    #and is close to the center of a tile
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                        #OR a white ghost door that we're in Or if we're dead
                            self.in_box or self.dead)):
                        self.turns[3] = True#we can turn up to face the tile, this logic repeats for every direction
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:#if the ghosts is in the side portals
            self.turns[0] = True
            self.turns[1] = True
            #this just checks if the ghost is in the center box
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True#sets box variable to true if we're in the box
        else:
            self.in_box = False
        return self.turns, self.in_box

    #General Rundown (called every frame)
    # This is the logic that determines how the ghosts will move
    #.target is a coordinate pair which is the player by default
    #Similar to the player move script we return the x,y and direction variable and update the ghosts position every frame
    def move_ghost(self):
        # r, l, u, d
        # ghost is going to turn to chase down player
        if self.direction == 0:#if the ghost is moving right
            if self.target[0] > self.x_pos and self.turns[0]:#if my target(player) is to my right
                #and I am allowed to move right
                self.x_pos += self.speed#keep moving right
            elif not self.turns[0]:#if the ghost was moving right and we hit a tile and are no longer allow to turn right
                if self.target[1] > self.y_pos and self.turns[3]:#We Start checking for more possible directions to move
                    #starting with down
                    #if my target is below me and i can move down
                    self.direction = 3#turn down
                    self.y_pos += self.speed#move down
                elif self.target[1] < self.y_pos and self.turns[2]:#target is above me and I can move up
                    self.direction = 2#turn up
                    self.y_pos -= self.speed#move up
                elif self.target[0] < self.x_pos and self.turns[1]:#same thing but for the left direction
                    self.direction = 1
                    self.x_pos -= self.speed
                    #we've checked if any turns are logical to pursue pac-man
                elif self.turns[3]:#if we can't move in any of the previous directions
                    # basically if the target is in a weird direction ex. up and to the right
                    # start cycling though different directions starting with down, then up, left, and finally right
                    # until theres a direction the ghost can move
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:# ghost can go right but the target isnt to the right anymore
                if self.target[1] > self.y_pos and self.turns[3]:#if the target is not to my right but i can keep going right
                    #keep going right and check for a different direction to move in starting with down
                    #if the target is below the ghost
                    #this will allow the ghost to change directions towards the target even if they don't hit a wall
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
                    #this logic was just for moving in 1 direction, this is copy pasted for each other direction
        elif self.direction == 1:#this logic gets repeated for all for direction
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed##
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:#if the ghost move offscreen, return them onscreen
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos - 30
        return self.x_pos, self.y_pos, self.direction

#General rundown (ran every frame)
#Every frame we draw the score and lives to the screen using pygame's draw function
#we define the shape, size and color of whatever UI we want to draw
#we can draw the game win/lose screen using this function as well
def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 720))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)#this was for debugging
    for i in range(lives):#draw a extra life ui for each each extra life we have
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (350 + i * 40, 715))
    if game_over:#if we lose draw the game over screen
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:#draw a win screen if we win
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))


    #General rundown(called every frame)
    #we check pacmans position in the board array and see if it overlaps where a 1 or a pellet is
    #if he's over a pellet we change the value to a 0 making the tile an empty space, we then increase the score
    #same logic for the big pellets but you also get a powerup and more points
    #the score, powerup, power_counter, and the eaten_ghost vars all get updated every frame
    #this function returns those variables
def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:#if pacmans position is on the grid, we can't check outside of the grid
        #a 1 is a small pellet from the board.py file
        #change it to a 0 or an empty space, this will make it appear as if pacman ate the pellet
        #increase score
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:#gain more points for the large pellets
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True#activate the powerup that lets pac-man eat ghosts
            power_count = 0#the number of powerups we've eaten
            eaten_ghosts = [False, False, False, False]#tracks which ghosts we've eaten
            # this makes sure the ghost stay dead as floating eyes and not frightened
            #after we collect powerups back to back
    return scor, power, power_count, eaten_ghosts


#General Rundown: (this function is called every frame)
#the level variable is the board array of arrays from board.py (around line 14)
#num1 and 2 are the height and width of the tile
#they scale to the size of the game screen.
#We loop through every row and every column in every row in the board array and check what number it is
#based on what that number is we draw a tile in the game based on where the number in the array is
#this makes the array function as a map for the game
#to find where the sprite should be drawn on the x axis we use
#j * num2, j is the column the number was in, we move it over on the x axis a set amount
#the 0.5*num2 centers the tile
#this is repeated for the y coordinate the number at the end
#this tells us where the image should be drawn on the screen
#the number at the end of the draw function determines the scale of the tile
#the collision for the player and the board is different for the player and the ghosts

def draw_board():#drawing the grid (num1 and 2 are roughly 26 and 31)
    #the -50 for the height adds a bit of empty space around the tile
    #the //32 and // 30 determines how tall and wide each piece should be
    num1 = ((HEIGHT - 50) // 32) #the size of the tiles, the size of the tiles scales to the window size
    num2 = (WIDTH // 30)#the board is slightly taller than it is wider, the "//" is so the result is an integer for the draw command
    #j is what column we're in and acts as the x coordinate, i is the row and y coord,
    #num2 will move the object 32 spaces across board from start pos, 0.5 centers the object, last digit is the size of the object
    for i in range(len(level)):#go through every row in the array
        for j in range(len(level[i])):#go through every column in the row in the array
            if level[i][j] == 1: #if the number is a 1, do this: the mini pellets that pac-man eats
                #based on where the number appeared in the array and what the number is
                #draw a image                        #this is the center of the circle
                                                    #we're putting the x value as wherever this number appears in the board array
                                                    #times 30 to position it and scale it to the screen size, the 0.5 puts the image in the center
                                                    #the 4 determines how big the image is
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)#this puts the object in the center of the tile
            if level[i][j] == 2 and not flicker:#the big pellets that let pac-man eat the ghosts, its only drawn if flicker = false
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:#3-9 are the different lines used to make the walls of the grid
                #this draws a line from the top of the tile to the bottom of the tile, j * num2 is the center of the tile, i*num1 is the top of the tile
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)#i*num1 +num1 is the bottom of the tile, 3 is the thickness of the line
            if level[i][j] == 4:#by swapping num1 for num2 you rotate the line
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:#5-8 formula for making an arc, it draws part of a circle with a defined start and end point
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:#the special white door that only ghosts can move through, the same as number 4
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)


#General rundown: (This is called every frame)
#the direction variable determines what direction pac-man is facing
#screen.blit draws images to the screen, we draw 1 of pacmans 4 sprites to the screen at his x and y postition
#counter is a variable that constantly changes every frame (line 560)
#this causes pacman to cycle through a different images every frame
#depending on where we're facing we have to either rotate or flip the image
def draw_player():#display pacman and rotate his sprite based on which direction we're moving
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:#           how fast we cycle through pac-mans sprites
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


#General Rundown: (called every frame)
#Center x and y are the center point coordinates of the player
#num 3 lets us check a set distance away from the player from their center
#this is to make sure collisions are done the moment an object touches pacman himself and not just his center
#the "centerx // 30 < 29:" is to check if pacman is in the board
#the board is 30 tiles wide so if we're ouside that we're going to one of the side portals
#by default we make it so pacman isn't allowed to turn in any direction
#"turns = [False, False, False, False]" makes it so we aren't allowed to turn
#meaning pacman can only turn left and right and therefore don't need to check for a direction in that instance
#for right collisions we check if our direction = 0
#then we check for our position in the level, which is an array of arrays
#"level[centery // num1][(centerx - num3) // num2] < 3:"centery//num1 is the board row we're in that we can detect based on our center y pos
#same goes for centerx but with the columns instead, the -num3 is the offset number we're using to check the tile behind the player
#basically where pacman is on the screen can be correlated to a positon in the array
#we can check the numbers in and around pacman to see if he's facing a wall,pellet,etc...
#using that we can tell the game whether or not he can turn in that direction
#this works with the move_player function to decide if pacman can move foreward or not
# the "< 3" is checking the board array and seeing if the coordinate in question is a 0,1 or 2, if it is we set turns[1] = true
# turns[1] is a left turn, were saying that we can turn left because we're moving right and the space behind us is either empty or a type of pellet
#this logic is used for every direction to determine if we can turn or not
#this function returns turns, this tells the game what direction the player can turn in
def check_position(centerx, centery):#center x and center y are the center coords of the player
    turns = [False, False, False, False]#by default make it so you can't turn
    num1 = (HEIGHT - 50) // 32#these vars are used to determine pacmans position relative to the board array
    num2 = (WIDTH // 30)
    num3 = 15 #offset value we use to check tiles away from pacman
    # check collisions based on center x and center y of player +/- offset number
    if centerx // 30 < 29:#if we're on the grid and not moving out of it
        if direction == 0:#if we're moving right and the tile behind the player is okay to pass through
            # 0-3 are powerups and empty space
            if level[centery // num1][(centerx - num3) // num2] < 3:#is the space to the left of me not a wall
                turns[1] = True#I can turn left
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:#moving up and down
            #were checking here if our x pos allows a turn up or down
            if 12 <= centerx % num2 <= 18:#if pacman is about in the center of a tile
                #each tile is 30 wide so this checks if were at most 6 pixels away from the center of a tile
                #this gives pacman another way to be allowed to turn that isn't based on his direction
                #this also makes sure pacman is close to the center of a tile before he can turn
                #its close to the same logic as the previous if statements
                if level[(centery + num3) // num1][centerx // num2] < 3:#if the space below me isnt a wall
                    turns[3] = True#im allowed to turn down
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:#same logic as before but for left/right
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    #num 3 is sometimes swaped out for num1/2 to check a full tile instead
                    #this helps make the window you have turn bigger
                    #this is to make sure the tile is clear and we aren't moving through a wall but close to the wall
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:#if we're moving out of the grid
        turns[0] = True
        turns[1] = True

    return turns


#General rundown: (runs every frame)
#the player will move in the direction their facing if their allowed to turn in that same direction
#this function returns 2 values that are set to the players x and y coordinate every frame
def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:#if were currently facing right and we're allowed to turn right
        play_x += player_speed#increase our x value by the players speed
    elif direction == 1 and turns_allowed[1]:#repeat for left, up, and down
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


#general Rundown(updated every frame)
#this is called every frame to update the targets of the ghost (the target being the players position)
#The ghosts will always try to pursue a target
#when the player gets a powerup the ghosts will change target from the player coords to a different set of coords
#these are unique to each ghost
#this returns the target coordinate for the 4 ghosts to follow
def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 450:#this controls how the ghosts will run away if a powerup is active
        #we grab the players x coordinate and make a new variable that is far away from the player for the ghosts to run to
        runaway_x = 900
    else:
        runaway_x = 0
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0
    return_target = (380, 400)#this is where the center box is
    if powerup:#if the powerup is active and the ghosts are still alive
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)#the ghost will Change to this new target with is different for each ghost
            #the red ghost will run away from the player
        elif not blinky.dead and eaten_ghost[0]:#if the ghost was eaten
            if 340 < blink_x < 560 and 340 < blink_y < 500:#if were in the center box and were not dead, get out of the box
                blink_target = (400, 100)#if in box, move out of the box
            else:
                blink_target = (player_x, player_y)#if out of the box, target player
        else:#the ghost is dead
            blink_target = return_target#return to the box, repeat for the other ghosts
        if not inky.dead and not eaten_ghost[1]:
            # the blue ghost will run away from the player but only on the x axis
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            # the pink ghost will run away from the player but only in thy y axis
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead and not eaten_ghost[3]:
            #the orange ghost will try to run to the middle of the board
            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:#if the powerup isn't active, repeat the previous code without the runaway targeting
        if not blinky.dead:#if the ghost is alive
            if 340 < blink_x < 560 and 340 < blink_y < 500:#if the ghost is in the center box
                blink_target = (400, 100)#get out of the box
            else:
                blink_target = (player_x, player_y)#not in center box, go chase player
        else:#the ghost is dead
            blink_target = return_target#return to the centerbox, repeat for other ghosts
        if not inky.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target
        if not pinky.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target
        if not clyde.dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]


run = True
while run: #this is the game loop that will run every frame while run = true
    timer.tick(fps)
    if counter < 19:#this controls the speed pacman animates at and how fast the large powerups flicker
        counter += 1
        if counter > 3:#flicker 3 times a second
            flicker = False
    else:
        counter = 0#to make sure the counter doesn't increase indefinatly
        flicker = True
    if powerup and power_counter < 600:#if we are powered up and its been less than 6 seconds
        #this game runs up to 60 frames per second
        power_counter += 1#increment the power counter by 1 every frame, this will act as a timer so we can track
        #how long the powerup has been active for
    elif powerup and power_counter >= 600:#once we've reached 6 seconds with the powerup
        #deactivate the powerup and return the ghosts to their normal state
        power_counter = 0#reset timer to 0
        powerup = False#deactive the powerup
        eaten_ghost = [False, False, False, False]#make all the ghosts normal again
    if startup_counter < 180 and not game_over and not game_won:#at the start of the game, pac-man can't move for a couple seconds
        #this simulates that
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black') #make the background of the screen black
    draw_board()#draw the game grid onto the screen
    center_x = player_x + 23#the center of pacman
    center_y = player_y + 24
    if powerup:#when we get a powerup slow down the ghosts
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]#the ghosts regular speed
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if blinky_dead:
        ghost_speeds[0] = 4#when the ghosts become eyeballs and is heading back to the center box
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4

    game_won = True#code runs from top to bottom, every frame we set game won to true
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:#then we loop through the board to see if theres a 1 or a 2
            #1 and 2 correspond to the different pellets the player, if there is a 1 or 2 then set game won to false
            #once theres no more pellets game won wont be set to false anymore and will stay set to true meaning we win
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)#players hitbox
    draw_player()
    #define what the ghost are as gameobjects with set values
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead,
                   blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead,
                 inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead,
                  pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead,
                  clyde_box, 3)
    draw_misc()
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)#this lets the ghost target stuff

    turns_allowed = check_position(center_x, center_y)#pac-mans center
    if moving: #if pacman is allowed to move then move
        player_x, player_y = move_player(player_x, player_y)#move the player and ghosts every frame
        blinky_x, blinky_y, blinky_direction = blinky.move_ghost()
        pinky_x, pinky_y, pinky_direction = pinky.move_ghost()
        inky_x, inky_y, inky_direction = inky.move_ghost()
        clyde_x, clyde_y, clyde_direction = clyde.move_ghost()
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    # check ghost collisions with the player
    if not powerup: #if pac-man doesn't have a powerup and touches a ghost
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
                (player_circle.colliderect(inky.rect) and not inky.dead) or \
                (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
                (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0:#if you still have bonus lives lose a life and reset the game and all vars
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 408
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
            else:#if you have no lives left lose the game
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 408
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 408
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 408
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 408
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
        #if we have a powerup active, blinky isnt dead, and we collide with blinky, kill blinky
        #repeat for the other ghosts
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100#you get more points the more ghosts you eat
        #2^current number of ghost that are eaten * 100
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
        inky_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100
#this runs through all the edge cases and makes sure the proper response happens when we eat ghosts

    for event in pygame.event.get():#check if a pygame event is triggered
        if event.type == pygame.QUIT:#if we exit the game, stop running it
            run = False
        if event.type == pygame.KEYDOWN:#when we press a keyboard button
            if event.key == pygame.K_RIGHT:#the right arrow key
                direction_command = 0#rotate pacman accordingly
                # direction_command is what we use to tell the game that we want to change directions
                #the game itself will check to see if it can change directions
                #if theres a wall or ghost in the way then the direction cant be changed
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):#if we press space and the game ended
                #reset the game completly
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 408
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)#reset the board, this is why we have to import copy
                game_over = False
                game_won = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:#this is for in case we press
                # multiple keys down at once, we will keep going in the direction we were going or the direction still being held down
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:#if we tell the game that we want to turn right
        #and we're allowed to turn right
        direction = 0#turn pacman right, repeat for the other directions
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:#if the player moves too far off the board
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if blinky.in_box and blinky_dead:#if the ghosts in their floating eyes form return to the box
        # bring them back to life
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False

    pygame.display.flip()
pygame.quit()