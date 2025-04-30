import pygame

def drawFps(screen: pygame.Surface, font: pygame.Font, clock: pygame.time.Clock):
    fps   = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))
     