# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import time
import math
import pygame
import pygame.gfxdraw
# import numpy as np
import mycolors as mc
import random


class board_xy:
    def __init__(self, nrow=15, ncol=15, board_width=800, board_height=800, x_margin=100, y_margin=100):
        self.nrow = nrow
        self.ncol = ncol
        self.board_width = board_width
        self.board_height = board_height
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.X = [[0 for i in range(self.ncol)] for j in range(self.nrow)]
        self.Y = [[0 for i in range(self.ncol)] for j in range(self.nrow)]
        self.x_interval = (self.board_width - 2 * self.x_margin) // (ncol - 1)
        self.y_interval = (self.board_height - 2 * self.y_margin) // (nrow - 1)

        x0 = x_margin
        y0 = y_margin

        for row in range(nrow):
            y = y0 + row * self.y_interval
            for col in range(ncol):
                x = x0 + col * self.x_interval
                self.X[row][col] = x
                self.Y[row][col] = y

    def get_xy(self, mouse_x=None, mouse_y=None, button_radius=16):
        for row in range(self.nrow):
            for col in range(self.ncol):
                x = self.X[row][col]
                y = self.Y[row][col]

                d = math.sqrt((mouse_x - x) * (mouse_x - x) + (mouse_y - y) * (mouse_y - y))
                #
                if d <= 0.5 * button_radius:
                    return x, y

        return -1, -1

    def get_row_col(self, x, y):
        col = (x - self.x_margin) // self.x_interval
        row = (y - self.y_margin) // self.y_interval
        return int(row), int(col)

    def row_col_to_xy(self, row, col):
        return (self.X[row][col], self.Y[row][col])


class Circle(pygame.sprite.Sprite):
    def __init__(self, color=mc.blue, width=32, height=32):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # set sprite attributes
        self.width = width
        self.height = height
        self.color = color
        self.radius = width // 2 - 2

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

        # draw circle
        xc = self.width // 2
        yc = self.height // 2
        r = self.radius
        pygame.draw.circle(self.image, self.color, (xc, yc), r)
        pygame.gfxdraw.aacircle(self.image, xc, yc, r, self.color)
        pygame.gfxdraw.filled_circle(self.image, xc, yc, r, self.color)

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y


class vline(pygame.sprite.Sprite):
    def __init__(self, color=mc.black, width=3, height=None, x=None, y=None):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.fill(color)


class hline(pygame.sprite.Sprite):
    def __init__(self, color=mc.black, width=None, height=3, x=None, y=None):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image.fill(color)


class wuziqi:
    def __init__(self, nrow=15, ncol=15, board_width=800, board_height=800, x_margin=100, y_margin=100):
        self.nrow = nrow
        self.ncol = ncol
        self.board_width = board_width
        self.board_height = board_height
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.end_game_flag = False

        pygame.init()
        window_size = (board_width, board_height)
        # window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.window = pygame.display.set_mode(window_size)
        self.rect = self.window.get_rect()
        pygame.display.set_caption(u"五子棋（Gomoku）")
        background_image = pygame.image.load("pine800x800.png")

        icon_image = pygame.image.load("wuziqi.png")
        pygame.display.set_icon(icon_image)
        # window.fill(mc.cyan)
        # fill the window with the pine texture background
        self.window.blit(background_image, self.rect)
        pygame.display.update()

        # 
        self.button_group = pygame.sprite.Group()

        self.XY = board_xy(nrow=self.nrow, ncol=self.ncol, board_width=self.board_width, board_height=self.board_height,
                           x_margin=self.x_margin, y_margin=self.y_margin)

        # board: 0-> empty, 1-> human, 2-> computer
        # self.board = np.zeros(shape=(nrow, ncol), dtype=np.int16)
        # stop using numpy ans switch to list for better performance
        self.board = [[0 for i in range(self.ncol)] for j in range(self.nrow)]

        # scores for different situations
        self.connected_five_points = 20000
        self.open_four_points = 20000
        self.closed_four_points = 2000
        self.open_three_points = 2000
        self.close_three_points = 20
        self.open_two_points = 2
        self.close_two_points = 1

        # catch for the minimax search algorithm
        # key: board code
        # value: board score 
        self.minimax_catch = {}
        self.computer_color = 2  # white color
        self.player_color = 1  # black color

    def print_board(self):
        for row in range(self.nrow):
            line = ""
            for col in range(self.ncol):
                line += str(self.board[row][col]) + " "
            print(line)
        print("")

    def get_xy(self, row, col):
        return self.XY.row_col_to_xy(row, col)

    def in_board(self, row, col):
        if (0 <= row < self.nrow) and (0 <= col < self.ncol):
            return True
        else:
            return False

    def count_five(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.in_board(row, col + 4) \
                        and self.board[row][col] == color_id \
                        and self.board[row][col + 1] == color_id \
                        and self.board[row][col + 2] == color_id \
                        and self.board[row][col + 3] == color_id \
                        and self.board[row][col + 4] == color_id:
                    count = count + 1
                if self.in_board(row + 4, col) \
                        and self.board[row][col] == color_id \
                        and self.board[row + 1][col] == color_id \
                        and self.board[row + 2][col] == color_id \
                        and self.board[row + 3][col] == color_id \
                        and self.board[row + 4][col] == color_id:
                    count = count + 1
                if self.in_board(row + 4, col + 4) \
                        and self.board[row][col] == color_id \
                        and self.board[row + 1][col + 1] == color_id \
                        and self.board[row + 2][col + 2] == color_id \
                        and self.board[row + 3][col + 3] == color_id \
                        and self.board[row + 4][col + 4] == color_id:
                    count = count + 1
                if self.in_board(row - 4, col + 4) \
                        and self.board[row][col] == color_id \
                        and self.board[row - 1][col + 1] == color_id \
                        and self.board[row - 2][col + 2] == color_id \
                        and self.board[row - 3][col + 3] == color_id \
                        and self.board[row - 4][col + 4] == color_id:
                    count = count + 1
        return count

    def count_open_four(self, color_id):  # color_id: 0 -> unoccupied, 1 -> black, 2 -> white
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                # check the horizontal direction, from left to right 
                # there are 5 more points to the right of the current point
                # the current (first) point is not occupied
                # the second point in the right is occupied with the  color_id
                # the third point in the right is occupied with the color_id
                # the fourth point in the right is occupied with the color_id
                # the fifth point in the right is occupied with the color_id
                # the sixth point in the right is not occupied
                if self.in_board(row, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row][col + 1] == color_id \
                        and self.board[row][col + 2] == color_id \
                        and self.board[row][col + 3] == color_id \
                        and self.board[row][col + 4] == color_id \
                        and self.board[row][col + 5] == 0:
                    count = count + 1
                # check the vertical direction, from top to bottom
                if self.in_board(row + 5, col) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col] == color_id \
                        and self.board[row + 2][col] == color_id \
                        and self.board[row + 3][col] == color_id \
                        and self.board[row + 4][col] == color_id \
                        and self.board[row + 5][col] == 0:
                    count = count + 1
                # check the diagonal direction 1, from upper left to lower right
                if self.in_board(row + 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col + 1] == color_id \
                        and self.board[row + 2][col + 2] == color_id \
                        and self.board[row + 3][col + 3] == color_id \
                        and self.board[row + 4][col + 4] == color_id \
                        and self.board[row + 5][col + 5] == 0:
                    count = count + 1
                # check the diagonal direction 2, from lower left to upper right
                if self.in_board(row - 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row - 1][col + 1] == color_id \
                        and self.board[row - 2][col + 2] == color_id \
                        and self.board[row - 3][col + 3] == color_id \
                        and self.board[row - 4][col + 4] == color_id \
                        and self.board[row - 5][col + 5] == 0:
                    count = count + 1
        return count

    def count_closed_four(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                # horizontal direction
                if (self.in_board(row, col + 4) \
                    and self.board[row][col] == 0 \
                    and self.board[row][col + 1] == color_id \
                    and self.board[row][col + 2] == color_id \
                    and self.board[row][col + 3] == color_id \
                    and self.board[row][col + 4] == color_id) \
                        or (self.in_board(row, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == color_id \
                            and self.board[row][col + 4] == 0):
                    count = count + 1
                # vertical direction 
                elif (self.in_board(row + 4, col) \
                      and self.board[row][col] == 0 \
                      and self.board[row + 1][col] == color_id \
                      and self.board[row + 2][col] == color_id \
                      and self.board[row + 3][col] == color_id \
                      and self.board[row + 4][col] == color_id) \
                        or (self.in_board(row + 4, col) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == color_id \
                            and self.board[row + 4][col] == 0):
                    count = count + 1
                # diagonal direction 1, to lower right
                elif (self.in_board(row + 4, col + 4) \
                      and self.board[row][col] == 0 \
                      and self.board[row + 1][col + 1] == color_id \
                      and self.board[row + 2][col + 2] == color_id \
                      and self.board[row + 3][col + 3] == color_id \
                      and self.board[row + 4][col + 4] == color_id) \
                        or (self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == color_id \
                            and self.board[row + 4][col + 4] == 0):
                    count = count + 1
                # diagonal direction 1, to upper right
                elif (self.in_board(row - 4, col + 4) \
                      and self.board[row][col] == 0 \
                      and self.board[row - 1][col + 1] == color_id \
                      and self.board[row - 2][col + 2] == color_id \
                      and self.board[row - 3][col + 3] == color_id \
                      and self.board[row - 4][col + 4] == color_id) \
                        or (self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == color_id \
                            and self.board[row - 4][col + 4] == 0):
                    count = count + 1
        return count

    def count_open_three(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                # check the horizontal direction, from left to right 
                # there are 5 more points to the right of the current point
                # the current (first) point is not occupied
                # the second point in the right is not occupied
                # the third point in the right is occupied with the color_id
                # the fourth point in the right is occupied with the color_id
                # the fifth point in the right is occupied with the color_id
                # the sixth point in the right is not occupied
                if (self.in_board(row, col + 5) \
                    and self.board[row][col] == 0 \
                    and self.board[row][col + 1] == 0 \
                    and self.board[row][col + 2] == color_id \
                    and self.board[row][col + 3] == color_id \
                    and self.board[row][col + 4] == color_id \
                    and self.board[row][col + 5] == 0) \
                        or (self.in_board(row, col + 5) \
                            and self.board[row][col] == 0 \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == color_id \
                            and self.board[row][col + 4] == 0 \
                            and self.board[row][col + 5] == 0):
                    count = count + 1
                # check the vertical direction, from top to bottom
                if (self.in_board(row + 5, col) \
                    and self.board[row][col] == 0 \
                    and self.board[row + 1][col] == 0 \
                    and self.board[row + 2][col] == color_id \
                    and self.board[row + 3][col] == color_id \
                    and self.board[row + 4][col] == color_id \
                    and self.board[row + 5][col] == 0) \
                        or (self.in_board(row + 5, col) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == color_id \
                            and self.board[row + 4][col] == 0 \
                            and self.board[row + 5][col] == 0):
                    count = count + 1
                # check the diagonal direction 1, from upper left to lower right
                if (self.in_board(row + 5, col + 5) \
                    and self.board[row][col] == 0 \
                    and self.board[row + 1][col + 1] == 0 \
                    and self.board[row + 2][col + 2] == color_id \
                    and self.board[row + 3][col + 3] == color_id \
                    and self.board[row + 4][col + 4] == color_id \
                    and self.board[row + 5][col + 5] == 0) \
                        or (self.in_board(row + 5, col + 5) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == color_id \
                            and self.board[row + 4][col + 4] == 0 \
                            and self.board[row + 5][col + 5] == 0):
                    count = count + 1
                # check the diagonal direction 2, from lower left to uper right
                if (self.in_board(row - 5, col + 5) \
                    and self.board[row][col] == 0 \
                    and self.board[row - 1][col + 1] == 0 \
                    and self.board[row - 2][col + 2] == color_id \
                    and self.board[row - 3][col + 3] == color_id \
                    and self.board[row - 4][col + 4] == color_id \
                    and self.board[row - 5][col + 5] == 0) \
                        or (self.in_board(row - 5, col + 5) \
                            and self.board[row][col] == 0 \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == color_id \
                            and self.board[row - 4][col + 4] == 0 \
                            and self.board[row - 5][col + 5] == 0):
                    count = count + 1
        return count

    def count_closed_three(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                # horizontal direction
                if (self.in_board(row, col + 4) \
                    and self.board[row][col] == 0 \
                    and self.board[row][col + 1] == 0 \
                    and self.board[row][col + 2] == color_id \
                    and self.board[row][col + 3] == color_id \
                    and self.board[row][col + 4] == color_id) \
                        or (self.in_board(row, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == 0 \
                            and self.board[row][col + 4] == 0):
                    count = count + 1
                # vertical direction 
                elif (self.in_board(row + 4, col) \
                      and self.board[row][col] == 0 \
                      and self.board[row + 1][col] == 0 \
                      and self.board[row + 2][col] == color_id \
                      and self.board[row + 3][col] == color_id \
                      and self.board[row + 4][col] == color_id) \
                        or (self.in_board(row + 4, col) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == 0 \
                            and self.board[row + 4][col] == 0):
                    count = count + 1
                # diagonal direction 1, to lower right
                elif (self.in_board(row + 4, col + 4) \
                      and self.board[row][col] == 0 \
                      and self.board[row + 1][col + 1] == 0 \
                      and self.board[row + 2][col + 2] == color_id \
                      and self.board[row + 3][col + 3] == color_id \
                      and self.board[row + 4][col + 4] == color_id) \
                        or (self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == 0 \
                            and self.board[row + 4][col + 4] == 0):
                    count = count + 1
                # diagonal direction 1, to upper right
                elif (self.in_board(row - 4, col + 4) \
                      and self.board[row][col] == 0 \
                      and self.board[row - 1][col + 1] == 0 \
                      and self.board[row - 2][col + 2] == color_id \
                      and self.board[row - 3][col + 3] == color_id \
                      and self.board[row - 4][col + 4] == color_id) \
                        or (self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == 0 \
                            and self.board[row - 4][col + 4] == 0):
                    count = count + 1
        return count

    def count_open_two(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.in_board(row, col + 7) \
                        and self.board[row][col] == 0 \
                        and self.board[row][col + 1] == 0 \
                        and self.board[row][col + 2] == 0 \
                        and self.board[row][col + 3] == color_id \
                        and self.board[row][col + 4] == color_id \
                        and self.board[row][col + 5] == 0 \
                        and self.board[row][col + 6] == 0 \
                        and self.board[row][col + 7] == 0:
                    count = count + 1
                if self.in_board(row + 7, col) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col] == 0 \
                        and self.board[row + 2][col] == 0 \
                        and self.board[row + 3][col] == color_id \
                        and self.board[row + 4][col] == color_id \
                        and self.board[row + 5][col] == 0 \
                        and self.board[row + 6][col] == 0 \
                        and self.board[row + 7][col] == 0:
                    count = count + 1

                if self.in_board(row + 7, col + 7) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col + 1] == 0 \
                        and self.board[row + 2][col + 2] == 0 \
                        and self.board[row + 3][col + 3] == color_id \
                        and self.board[row + 4][col + 4] == color_id \
                        and self.board[row + 5][col + 5] == 0 \
                        and self.board[row + 6][col + 6] == 0 \
                        and self.board[row + 7][col + 7] == 0:
                    count = count + 1

                if self.in_board(row - 7, col + 7) \
                        and self.board[row][col] == 0 \
                        and self.board[row - 1][col + 1] == 0 \
                        and self.board[row - 2][col + 2] == 0 \
                        and self.board[row - 3][col + 3] == color_id \
                        and self.board[row - 4][col + 4] == color_id \
                        and self.board[row - 5][col + 5] == 0 \
                        and self.board[row - 6][col + 6] == 0 \
                        and self.board[row - 7][col + 7] == 0:
                    count = count + 1
        return count

    def count_closed_two(self, color_id):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                if (self.in_board(row, col + 4) \
                    and self.board[row][col] == 0 \
                    and self.board[row][col + 1] == 0 \
                    and self.board[row][col + 2] == 0 \
                    and self.board[row][col + 3] == color_id \
                    and self.board[row][col + 4] == color_id) \
                        or (self.in_board(row, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row][col + 1] == 0 \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == color_id \
                            and self.board[row][col + 4] == 0) \
                        or (self.in_board(row, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == 0 \
                            and self.board[row][col + 4] == 0) \
                        or (self.in_board(row, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == 0 \
                            and self.board[row][col + 3] == 0 \
                            and self.board[row][col + 4] == 0):
                    count = count + 1

        for row in range(self.nrow):
            for col in range(self.ncol):
                if (self.in_board(row + 4, col) \
                    and self.board[row][col] == 0 \
                    and self.board[row + 1][col] == 0 \
                    and self.board[row + 2][col] == 0 \
                    and self.board[row + 3][col] == color_id \
                    and self.board[row + 4][col] == color_id) \
                        or (self.in_board(row + 4, col) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col] == 0 \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == color_id \
                            and self.board[row + 4][col] == 0) \
                        or (self.in_board(row + 4, col) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == 0 \
                            and self.board[row + 4][col] == 0) \
                        or (self.in_board(row + 4, col) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == 0 \
                            and self.board[row + 3][col] == 0 \
                            and self.board[row + 4][col] == 0):
                    count = count + 1
        for row in range(self.nrow):
            for col in range(self.ncol):
                if (self.in_board(row + 4, col + 4) \
                    and self.board[row][col] == 0 \
                    and self.board[row + 1][col + 1] == 0 \
                    and self.board[row + 2][col + 2] == 0 \
                    and self.board[row + 3][col + 3] == color_id \
                    and self.board[row + 4][col + 4] == color_id) \
                        or (self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col + 1] == 0 \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == color_id \
                            and self.board[row + 4][col + 4] == 0) \
                        or (self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == 0 \
                            and self.board[row + 4][col + 4] == 0) \
                        or (self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == 0 \
                            and self.board[row + 3][col + 3] == 0 \
                            and self.board[row + 4][col + 4] == 0):
                    count = count + 1

        for row in range(self.nrow):
            for col in range(self.ncol):
                if (self.in_board(row - 4, col + 4) \
                    and self.board[row][col] == 0 \
                    and self.board[row - 1][col + 1] == 0 \
                    and self.board[row - 2][col + 2] == 0 \
                    and self.board[row - 3][col + 3] == color_id \
                    and self.board[row - 4][col + 4] == color_id) \
                        or (self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row - 1][col + 1] == 0 \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == color_id \
                            and self.board[row - 4][col + 4] == 0) \
                        or (self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == 0 \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == 0 \
                            and self.board[row - 4][col + 4] == 0) \
                        or (self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == 0 \
                            and self.board[row - 3][col + 3] == 0 \
                            and self.board[row - 4][col + 4] == 0):
                    count = count + 1
        return count

    def winning_position(self, color_id):
        for row in range(self.nrow):
            for col in range(self.ncol):
                for offset in range(0, 5):
                    others = list(filter(lambda x: x != offset, [0, 1, 2, 3, 4]))
                    if self.in_board(row, col + 4) \
                            and self.board[row][col + offset] == 0 \
                            and self.board[row][col + others[0]] == color_id \
                            and self.board[row][col + others[1]] == color_id \
                            and self.board[row][col + others[2]] == color_id \
                            and self.board[row][col + others[3]] == color_id:
                        return row, col + offset
                    if self.in_board(row + 4, col) \
                            and self.board[row + offset][col] == 0 \
                            and self.board[row + others[0]][col] == color_id \
                            and self.board[row + others[1]][col] == color_id \
                            and self.board[row + others[2]][col] == color_id \
                            and self.board[row + others[3]][col] == color_id:
                        return row + offset, col
                    if self.in_board(row + 4, col + 4) \
                            and self.board[row + offset][col + offset] == 0 \
                            and self.board[row + others[0]][col + others[0]] == color_id \
                            and self.board[row + others[1]][col + others[1]] == color_id \
                            and self.board[row + others[2]][col + others[2]] == color_id \
                            and self.board[row + others[3]][col + others[3]] == color_id:
                        return row + offset, col + offset
                    if self.in_board(row - 4, col + 4) \
                            and self.board[row - offset][col + offset] == 0 \
                            and self.board[row - others[0]][col + others[0]] == color_id \
                            and self.board[row - others[1]][col + others[1]] == color_id \
                            and self.board[row - others[2]][col + others[2]] == color_id \
                            and self.board[row - others[3]][col + others[3]] == color_id:
                        return row - offset, col + offset
        return (-1, -1)  # no winning position

    def terminal_state(self):
        for row in range(self.nrow):
            for col in range(self.ncol):
                for color_id in [1, 2]:
                    if self.in_board(row, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row][col + 1] == color_id \
                            and self.board[row][col + 2] == color_id \
                            and self.board[row][col + 3] == color_id \
                            and self.board[row][col + 4] == color_id:
                        return color_id
                    if self.in_board(row + 4, col) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col] == color_id \
                            and self.board[row + 2][col] == color_id \
                            and self.board[row + 3][col] == color_id \
                            and self.board[row + 4][col] == color_id:
                        return color_id
                    if self.in_board(row + 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row + 1][col + 1] == color_id \
                            and self.board[row + 2][col + 2] == color_id \
                            and self.board[row + 3][col + 3] == color_id \
                            and self.board[row + 4][col + 4] == color_id:
                        return color_id
                    if self.in_board(row - 4, col + 4) \
                            and self.board[row][col] == color_id \
                            and self.board[row - 1][col + 1] == color_id \
                            and self.board[row - 2][col + 2] == color_id \
                            and self.board[row - 3][col + 3] == color_id \
                            and self.board[row - 4][col + 4] == color_id:
                        return color_id
        return -1

    def nearby_moves(self):
        nearby_row_col = []
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.board[row][col] > 0:
                    row_max = min(row + 1, self.nrow)
                    col_max = min(col + 1, self.ncol)
                    row_min = max(row - 1, 0)
                    col_min = max(col - 1, 0)

                    for r in range(row_min, row_max + 1):
                        for c in range(col_min, col_max + 1):
                            if self.board[r][c] == 0 and (r, c) not in nearby_row_col:
                                nearby_row_col.append((r, c))
        return nearby_row_col

    def board_string_code(self):
        string_code = ""
        for row in range(self.nrow):
            for col in range(self.ncol):
                string_code += str(self.board[row][col])
        return string_code

    def evaluate_board_score(self):
        computer_connected_five = self.count_five(self.computer_color)
        player_connected_five = self.count_five(self.player_color)

        computer_open_four = self.count_open_four(self.computer_color)
        player_open_four = self.count_open_four(self.player_color)
        computer_open_three = self.count_open_three(self.computer_color)
        player_open_three = self.count_open_three(self.player_color)
        computer_open_two = self.count_open_two(self.computer_color)
        player_open_two = self.count_open_two(self.player_color)

        computer_closed_four = self.count_closed_four(self.computer_color) - computer_open_four
        player_closed_four = self.count_closed_four(self.player_color) - player_open_four
        computer_closed_three = self.count_closed_three(self.computer_color) - computer_open_three
        player_closed_three = self.count_closed_three(self.player_color) - player_open_three
        computer_closed_two = self.count_closed_two(self.computer_color) - computer_open_two
        player_closed_two = self.count_closed_two(self.player_color) - player_open_two

        computer_score = self.open_two_points * computer_open_two + self.close_two_points * computer_closed_two \
                         + self.open_three_points * computer_open_three + self.close_three_points * computer_closed_three \
                         + self.open_four_points * computer_open_four + self.closed_four_points * computer_closed_four \
                         + self.connected_five_points * computer_connected_five

        player_score = self.open_two_points * player_open_two + self.close_two_points * player_closed_two \
                       + self.open_three_points * player_open_three + self.close_three_points * player_closed_three \
                       + self.open_four_points * player_open_four + self.closed_four_points * player_closed_four \
                       + self.connected_five_points * player_connected_five

        return computer_score - 10*player_score

    def minimax(self, current_depth, target_depth, maximize_player_flag, alpha, beta, possible_moves, computer_color):
        # recursion function exit condition
        if current_depth == target_depth or self.terminal_state() == -1:
            board_code = self.board_string_code()
            if board_code in self.minimax_catch.keys():
                return self.minimax_catch[board_code]
            else:
                score = self.evaluate_board_score()
                self.minimax_catch[board_code] = score
                #self.print_board()
                #print("score: ", score)
                return score

        # determine current color to be maximized
        # current_depth = stone_count + 1
        # Since the player places the first stone, then current_color = computer when current_depth %  2==0
        if current_depth % 2 == 0:
            current_color = self.computer_color
        else:
            current_color = self.player_color
        print("current_depth", current_depth, "current_color", current_color)
        # maximize player score
        if maximize_player_flag:
            best_score = float("-inf")  # negative infinity
            for (row, col) in possible_moves:  # key: (row, col)
                self.board[row][col] = current_color
                new_board_code = self.board_string_code()
                # if the current situation is already evaluated before
                # assign the score to new_score
                if new_board_code in self.minimax_catch.keys():
                    new_score = self.minimax_catch[new_board_code]
                # current situation is not evaluated before, then
                # evaluate it
                else:
                    new_moves = self.nearby_moves()
                    new_score = self.minimax(current_depth + 1, target_depth, False, alpha, beta, new_moves,
                                             computer_color)
                    self.minimax_catch[new_board_code] = new_score
                # recover the board
                self.board[row][col] = 0

                # update best score
                best_score = max(best_score, new_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        # maximize computer score
        else:
            best_score = float("inf")  # positive infinity
            for (row, col) in possible_moves:
                self.board[row][col] = current_color
                new_board_code = self.board_string_code()
                if new_board_code in self.minimax_catch.keys():
                    new_score = self.minimax_catch[new_board_code]
                else:
                    new_moves = self.nearby_moves()
                    new_score = self.minimax(current_depth + 1, target_depth, True, alpha, beta, new_moves,
                                             computer_color)
                self.board[row][col] = 0
                best_score = min(best_score, new_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score

    def count_stone(self):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.board[row][col] != 0:
                    count += 1
        return count

    def find_open_four(self, color_id):
        for row in range(self.nrow):
            for col in range(self.ncol):
                # horizontal direction
                if self.in_board(row, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row][col + 1] == 0 \
                        and self.board[row][col + 2] == color_id \
                        and self.board[row][col + 3] == color_id \
                        and self.board[row][col + 4] == color_id \
                        and self.board[row][col + 5] == 0:
                    return row, col + 1
                if self.in_board(row, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row][col + 1] == color_id \
                        and self.board[row][col + 2] == color_id \
                        and self.board[row][col + 3] == color_id \
                        and self.board[row][col + 4] == 0 \
                        and self.board[row][col + 5] == 0:
                    return row, col + 4
                # vertical direction
                if self.in_board(row + 5, col) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col] == 0 \
                        and self.board[row + 2][col] == color_id \
                        and self.board[row + 3][col] == color_id \
                        and self.board[row + 4][col] == color_id \
                        and self.board[row + 5][col] == 0:
                    return row + 1, col
                if self.in_board(row + 5, col) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col] == color_id \
                        and self.board[row + 2][col] == color_id \
                        and self.board[row + 3][col] == color_id \
                        and self.board[row + 4][col] == 0 \
                        and self.board[row + 5][col] == 0:
                    return row + 4, col
                # diagonal direction to lower right
                if self.in_board(row + 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col + 1] == 0 \
                        and self.board[row + 2][col + 2] == color_id \
                        and self.board[row + 3][col + 3] == color_id \
                        and self.board[row + 4][col + 4] == color_id \
                        and self.board[row + 5][col + 5] == 0:
                    return row + 1, col + 1
                if self.in_board(row + 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row + 1][col + 1] == color_id \
                        and self.board[row + 2][col + 2] == color_id \
                        and self.board[row + 3][col + 3] == color_id \
                        and self.board[row + 4][col + 4] == 0 \
                        and self.board[row + 5][col + 5] == 0:
                    return row + 4, col + 4
                # diagonal direction to upper right
                if self.in_board(row - 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row - 1][col + 1] == 0 \
                        and self.board[row - 2][col + 2] == color_id \
                        and self.board[row - 3][col + 3] == color_id \
                        and self.board[row - 4][col + 4] == color_id \
                        and self.board[row - 5][col + 5] == 0:
                    return row - 1, col + 1
                if self.in_board(row - 5, col + 5) \
                        and self.board[row][col] == 0 \
                        and self.board[row - 1][col + 1] == color_id \
                        and self.board[row - 2][col + 2] == color_id \
                        and self.board[row - 3][col + 3] == color_id \
                        and self.board[row - 4][col + 4] == 0 \
                        and self.board[row - 5][col + 5] == 0:
                    return row - 4, col + 4
        return -1, -1

    def get_move(self):
        stone_count = self.count_stone()
        if stone_count == 0:
            return [int(self.nrow / 2), int(self.ncol / 2)]
        current_depth = stone_count + 1
        target_depth = current_depth + 3
        computer_win_row, computer_win_col = self.winning_position(self.computer_color)
        player_win_row, player_win_col = self.winning_position(self.player_color)
        if (computer_win_row, computer_win_col) != (-1, -1):
            return computer_win_row, computer_win_col
        if (player_win_row, player_win_col) != (-1, -1):
            return player_win_row, player_win_col
        open_four_row, open_four_col = self.find_open_four(self.computer_color)
        if (open_four_row, open_four_col) != (-1, -1):
            return open_four_row, open_four_col

        score = float("-inf")  # negative infinity
        best_list = []
        best_low = float("-inf")

        possible_moves = self.nearby_moves()
        # self.show_possible_moves(possible_moves)

        print("possible moves")
        print(possible_moves)
        #a= input("enter")
        alpha = float("-inf")
        beta = float("inf")
        for (row, col) in possible_moves:
            print("row, col", (row, col))

            self.board[row][col] = self.computer_color
            move_score = self.minimax(current_depth, target_depth, False, alpha, beta, possible_moves,
                                      self.computer_color)
            print("score", move_score)
            # a = input("press enter")
            self.board[row][col] = 0  # recover the board
            if move_score > score:
                score = move_score
                position = (row, col)

            if move_score > best_low:
                if len(best_list) == 0:
                    best_list.append([(row, col), move_score])
                else:
                    for n in range(len(best_list)):
                        if move_score > best_list[n][1]:
                            best_list.insert(n, [(row, col), move_score])
                            break
                    # only keep the top four positions
                    if len(best_list) > 4:
                        best_list = best_list[0:4]
                best_low = best_list[-1][1]  # index 0: (row, col), index 1: score
        # clear the catch for the minimax search
        self.minimax_catch = {}

        # choose the first candidate in the best_list
        chosen_idx = 0  # random.randint(0, 3)
        print("best_list", best_list)
        position = best_list[chosen_idx][0]

        #self.print_board()
        return position[0], position[1] # row, col

    def show_possible_moves(self, possible_moves):
        for row, col in possible_moves:
            x, y = self.get_xy(row, col)
            new_circle = Circle(color=mc.blue, width=32, height=32)
            new_circle.set_position(x - new_circle.width // 2, y - new_circle.height // 2)
            self.button_group.add(new_circle)
        pygame.display.update()

    def player_place_button(self, mouse_x=None, mouse_y=None):
        if self.end_game_flag == True:
            return
        x, y = self.XY.get_xy(mouse_x=mouse_x, mouse_y=mouse_y, button_radius=16)
        r, c = self.XY.get_row_col(x, y)
        if x == -1 and y == -1 and self.board[r][c] == 0:
            return

        new_circle = Circle(color=mc.black, width=32, height=32)
        new_circle.set_position(x - new_circle.width // 2, y - new_circle.height // 2)
        self.button_group.add(new_circle)
        pygame.display.update()
        self.board[r][c] = self.player_color
        if self.terminal_state() == self.player_color:
            pygame.display.set_caption(u"五子棋（Gomoku）: player win!")
            self.end_game_flag = True
            return

        print("------------------------------")
        # print("number of five: %d" % (self.count_five(1)))
        # print("number of open four: %d" % (self.count_open_four(1)))
        # print("number of four: %d" % (self.count_closed_four(1)))
        # print("number of open three: %d" % (self.count_open_three(1)))
        # print("number of three: %d" % (self.count_closed_three(1)))
        # print("number of open two: %d" % (self.count_open_two(1)))
        # print("number of two: %d" % (self.count_closed_two(1)))
        print("current score: %f" % (self.evaluate_board_score()))
        move_row, move_col = self.get_move()
        print("computer move: %d %d" %(move_row, move_col))
        # computer
        self.board[move_row][move_col] = self.computer_color
        move_x, move_y = self.get_xy(move_row, move_col)
        new_circle = Circle(color=mc.white, width=32, height=32)
        new_circle.set_position(move_x - new_circle.width // 2, move_y - new_circle.height // 2)
        self.button_group.add(new_circle)

        if self.terminal_state() == self.computer_color:
            pygame.display.set_caption(u"五子棋（Gomoku）: computer win!")
            self.end_game_flag = True

    def good_for_button(self, mouse_x=None, mouse_y=None):
        x, y = self.XY.get_xy(mouse_x=mouse_x, mouse_y=mouse_y, button_radius=16)
        r, c = self.XY.get_row_col(x, y)
        if (x == -1 and y == -1) or self.board[r][c] == 1:
            return False
        else:
            return True

    def draw_board(self, x_margin=100, y_margin=100, nrow=15, ncol=15):
        x0, y0, x1, y1 = self.window.get_rect()
        width0 = x1 - 2 * x_margin
        height0 = y1 - 2 * y_margin
        x_interval = width0 // (ncol - 1)
        y_interval = height0 // (nrow - 1)

        width = x_interval * (ncol - 1)
        height = y_interval * (ncol - 1) + 3

        # print(x_interval, y_interval, width, height)
        board_group = pygame.sprite.Group()

        for row in range(0, nrow):
            x = x_margin
            y = y_margin + row * y_interval
            a_hline = hline(width=width, x=x, y=y - 1)
            board_group.add(a_hline)

        for col in range(0, ncol):
            x = x_margin + col * x_interval
            y = y_margin
            a_vline = vline(height=height, x=x - 1, y=y - 1)
            board_group.add(a_vline)

        board_group.draw(self.window)
        pygame.display.update()

    def display_update(self):
        self.button_group.draw(self.window)
        pygame.display.update()
