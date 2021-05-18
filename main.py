import pygame
from wuziqi import wuziqi


def main():
    gomoku = wuziqi()
    gomoku.draw_board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if gomoku.good_for_move(mouse_x=x, mouse_y=y):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                # pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                x, y = event.pos
                if gomoku.good_for_move(mouse_x=x, mouse_y=y):
                    gomoku.player_place_button(mouse_x=x, mouse_y=y)
            if event.type == pygame.QUIT:
                running = False

        gomoku.display_update()
        gomoku.clock_tick(frame_per_second=60)

    pygame.quit()


if __name__ == '__main__':
    main()
