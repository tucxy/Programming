import pygame, sys
from pygame.locals import *

#& environment objects/variables
clock = pygame.time.Clock() #! initiates a Clock object
pygame.display.set_caption('Danny\'s Window') #! changes cpation of window to string

pygame.init() #! initiates pygame
WINDOW_SIZE = (400,400) #* sets pixel area inside window
screen = pygame.display.set_mode(WINDOW_SIZE,0,32) #! initiates window

player = pygame.image.load('nyan_cat.png') #! initiates image object

#& Movement variables
moving_right = False #initiates boolean variable to be used for moving right
moving_left= False #initiates boolean variable to be used for moving left
#moving_up = False #initiates boolean variable to be used for moving up
#moving_down= False #initiates boolean variable to be used for moving down

#& Player physics variables
player_location = [50,50] #* player_location[0],player_location[1]
player_y_velocity = 0

#& Gameloop
while True: #! initiates game loop

    #& screen and rendering
    screen.fill((255,255,255)) #!fills screen with white color to ensure background surface [screen] is wiped after image [player] is continuously being put on top of it at various coordinates
    screen.blit(player, player_location) #!renders image object [player] onto the surface object [screen] at [player_location];

    #& Movement variables
    if moving_right==True:
        player_location[0] += 4 # recall + x is right
    if moving_left==True:
        player_location[0] -= 4 # recall - x is left
    '''important note on coordinate system:

       The top left corner of the screen is (0,0) and (a,b):= (a,-b) in \\RR^{2}; in other words we are in Quadrant IV'''
    
    if player_location[1] > WINDOW_SIZE[1]-player.get_height(): #* If the bottom of the [player] object touches the bottom of the screen... **or goes beyond the bottom of the screen...**
        player_y_velocity = -player_y_velocity  #* flips [player_y_velocity]; bouncing effect. Basically perfect bounce with no friction flips velocity (towards +\\infty)

    else: #*otherwise... if [player] is not touching the bottom...
        player_y_velocity += 0.2 #* accelerates [player_y_velocity] by 0.2 pixels -\\infty; players velocity changes (accelerates) by 0.2 pixels per loop towards -\\infty
    player_location[1] += player_y_velocity #! changes [player_position][1] by [player_y_velocity]; moves players y position according to instantaneous velocity

    #& Events
    for event in pygame.event.get(): #* for each event in running game...
        if event.type == QUIT: #* If QUIT; X is pressed on window, is found then...
            pygame.quit() #! Stops pygame
            sys.exit() #! Stops program
        
        if event.type == KEYDOWN: #* If a key is pressed down...
            if event.key== K_RIGHT: #* and If it's the right arrow key...
                moving_right=True
            if event.key== K_LEFT: #* and If it's the left arrow key...
                moving_left=True
        if event.type == KEYUP: #* If a key is released (comes up; not pressed)...
            if event.key== K_RIGHT: #* and If it's the right arrow key...
                moving_right=False
            if event.key== K_LEFT: #* and If it's the left arrow key...
                moving_left=False




    #& Updates
    pygame.display.update() #! updates the screen all at once with scripts run above it in the loop basically I think
    clock.tick(60) #! Maintain 60 fps