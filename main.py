import pygame
from wuziqi import wuziqi


def main():
    frame_per_second = 60
    clock = pygame.time.Clock()
    gomoku = wuziqi()
    gomoku.draw_board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if gomoku.good_for_button(mouse_x=x, mouse_y=y):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                # pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                gomoku.player_place_button(mouse_x=x, mouse_y=y)
            if event.type == pygame.QUIT:
                running = False

        gomoku.display_update()
        clock.tick(frame_per_second)

    pygame.quit()


if __name__ == '__main__':
    main()
