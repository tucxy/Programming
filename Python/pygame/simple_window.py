import pygame, sys

from pygame.locals import *

clock = pygame.time.Clock() #! initiates a Clock object
pygame.display.set_caption('Danny\'s Window') #! changes cpation of window to string

pygame.init() #! initiates pygame
WINDOW_SIZE = (400,400) #* sets pixel area inside window
screen = pygame.display.set_mode(WINDOW_SIZE,0,32) #! initiates window

while True: #! initiates game loop


    for event in pygame.event.get(): #* for each event in running game...
        if event.type == QUIT: #* If QUIT; X is pressed on window, is found then...
            print('Bye')
            pygame.quit() #! Stops pygame
            sys.exit() #! Stops program

    pygame.display.update() # not sure what this does rn
    clock.tick(60) #! Maintain 60 fps