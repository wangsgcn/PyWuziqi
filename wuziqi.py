# Developer Shugong Wang (wangsgcn@gmail.com)

import pygame
import mycolors as mc
import random
from ui import board_xy, circle, vline, hline


class wuziqi:
    def __init__(self, nrow=15, ncol=15, board_width=800, board_height=800, x_margin=100, y_margin=100):
        self.nrow = nrow
        self.ncol = ncol
        self.board_width = board_width
        self.board_height = board_height
        self.x_interval = (board_width-2*x_margin)//(ncol-1)
        self.y_interval = (board_width-2*y_margin)//(nrow-1)
        self.x_margin = (board_width-self.x_interval*(ncol-1))//2
        self.y_margin = (board_height-self.y_interval*(nrow-1))//2
        self.end_game_flag = False
        self.clock = pygame.time.Clock()
        self.ready_for_human_move_flag = True
        self.opp_color = {1:2, 2:1} # dictionary for opponent color id


        pygame.init()
        window_size = (board_width, board_height)
        # window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.window = pygame.display.set_mode(window_size)
        self.rect = self.window.get_rect()
        pygame.display.set_caption(u"五子棋（Gomoku）")
        background_image = pygame.image.load("pine800x800.png")

        icon_image = pygame.image.load("wuziqi.png")
        pygame.display.set_icon(icon_image)

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
        self.connected_5_pts = 20000
        self.open_4_pts = 20000
        self.double_3_pts = 10000
        self.closed_4_pts = 2000
        self.open_3_pts =  2000
        self.closed_3_pts = 20
        self.open_2_pts = 2
        self.closed_2_pts = 1
        self.player_penalty = 10.0
        # catch for the minimax search algorithm
        # key: board code
        # value: board score 
        self.minimax_records = {}
        self.computer_color = 2  # white color
        self.player_color = 1  # black color

    def clock_tick(self, frame_per_second=60):
        self.clock.tick(frame_per_second)

    def print_board(self):
        line="    "
        for col in range(self.ncol):
            line += "%3d" %(col)
        print(line)
        line="     "
        for col in range(self.ncol):
            line += "---"
        print(line)
        for row in range(self.nrow):
            line = "%02d | " %row
            for col in range(self.ncol):
                line +=  " " + str(self.board[row][col]) + " "
            print(line)
        # print("")

    def get_xy(self, row, col):
        return self.XY.row_col_to_xy(row, col)

    def in_board(self, row, col):
        if (0 <= row < self.nrow) and (0 <= col < self.ncol):
            return True
        else:
            return False

    def count_five(self, color_id):
        a = color_id
        count = 0
        #  a a a a a
        #  -          (-) represent the current point to check
        for r in range(self.nrow):
            for c in range(self.ncol):
                if self.board[r][c] != a:
                    continue
                # horizontal direction
                if self.inside([(r,c+4)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)],[a,a,a,a,a]):
                    count += 1
                # vertical direction
                if self.inside([(r+4,c)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [a,a,a,a,a]):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-4,c+4)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [a,a,a,a,a]):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+4,c+4)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [a,a,a,a,a]):
                    count +=1
        return count

    def count_open_four(self, color_id):
        a = color_id
        count = 0
        # 0 a a a a 0
        for r in range(self.nrow):
            for c in range(self.ncol):
                # if the current point is already taken by either computer or player, no need to check
                if self.board[r][c] != 0:
                    continue
                # horizontal direction
                if self.inside([(r,c+4)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)],[0,a,a,a,a,0]):
                    count += 1
                # vertical direction
                if self.inside([(r+4,c)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [0,a,a,a,a,0]):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-4,c+4)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [0,a,a,a,a,0]):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+4,c+4)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [0,a,a,a,a,0]):
                    count += 1
        return count

    def count_closed_four(self, color_id):
        a = color_id             # current color to check
        b = self.opp_color[a]    # opponent color
        count = 0
        #0 a a a a b
        #b a a a a 0
        for r in range(self.nrow):
            for c in range(self.ncol):
                # if the current point is taken by color a, then continue. The algorithm only checks 0 or b for possible closed four.
                if self.board[r][c]==a:
                    continue
                # horizontal direction
                if self.inside([(r,c+5)]) and (self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [0,a,a,a,a,b])\
                                            or self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [b,a,a,a,a,0])):
                    count += 1
                # vertical direction
                if self.inside([(r+5,c)]) and (self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [0,a,a,a,a,b]) \
                                            or self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [b,a,a,a,a,0])):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-5,c+5)]) and (self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [0,a,a,a,a,b]) \
                                              or self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [b,a,a,a,a,0])):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+5,c+5)]) and (self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)],[0,a,a,a,a,b]) \
                                              or self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)],[b,a,a,a,a,0])):
                    count += 1
        return count

    def count_open_three(self, color_id):
        count = 0
        a = color_id # current cor to check
        for r in range(self.nrow):
            for c in range(self.ncol):
                # 0 * * * 0 (r, c), (r, c+4)
                if self.inside([(r,c+4)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)], [0,a,a,a,0]):
                    count += 1
                # column, (r, c) -> (r+4, c)
                if self.inside([(r+4,c)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [0,a,a,a,0]):
                    count += 1
                # upper right diagonal (r, c) -> (r-4,c+4)
                if self.inside([(r-4,c+4)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [0,a,a,a,0]):
                    count += 1
                # lower right diagonal (r, c) => (r+4, c+4)
                if self.inside([(r+4,c+4)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [0,a,a,a,0]):
                    count += 1
        return count

    def count_closed_three(self, color_id):
        a = color_id
        b = self.opp_color[a]
        count = 0
        # b a a a 0 0
        # 0 0 a a a b
        # -           (-) current point
        for r in range(self.nrow):
            for c in range(self.ncol):
                if self.board[r][c] == a:
                    continue
                # horizontal direction
                if self.inside([(r,c+4)]) and (self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)], [b,a,a,a,0,0])\
                                            or self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)], [0,0,a,a,a,b])):
                    count += 1
                # vertical direction
                if self.inside([(r+4,c)]) and (self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [b,a,a,a,0,0])\
                                            or self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [0,0,a,a,a,b])):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-4,c+4)]) and (self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [b,a,a,a,0,0])\
                                             or self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [0,0,a,a,a,b])):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+4,c+4)]) and (self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [b,a,a,a,0,0])\
                                              or self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [0,0,a,a,a,b])):
                    count += 1
        return count

    def count_closed_two(self, color_id):
        a = color_id
        b = self.opp_color[a]
        count = 0
        # closed cases
        # b a a 0 0 0
        # 0 0 0 a a b
        # -             current point to check
        for r in range(self.nrow):
            for c in range(self.ncol):
                if self.board[r][c] == a:
                    continue
                # horizontal direction
                if self.inside([(r,c+5)]) and (self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [b,a,a,0,0,0])\
                                            or self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [0,0,0,a,a,b])):
                    count += 1
                # vertical direction
                if self.inside([(r+5,c)]) and (self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [b,a,a,0,0,0])\
                                            or self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [0,0,0,a,a,b])):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-5,c+5)]) and (self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [b,a,a,0,0,0])\
                                              or self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [0,0,0,a,a,b])):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+5,c+5)]) and (self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)], [b,a,a,0,0,0])\
                                              or self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)], [0,0,0,a,a,b])):
                    count += 1
        return count

    def count_open_two(self, color_id):
        # only two situations of open two are considered for computational efficiency
        a = color_id
        count = 0
        for r in range(self.nrow):
            for c in range(self.ncol):
                # 0 0 a a 0
                # 0 a a 0 0
                if self.board[r][c] != 0:
                    continue
                # horizontal direction
                if self.inside([(r,c+4)]) and (self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)], [0,0,a,a,0]) \
                                           or  self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)], [0,a,a,0,0])):
                    count += 1
                # vertical direction
                if self.inside([(r+4,c)]) and (self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [0,0,a,a,0]) \
                                           or  self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [0,a,a,0,0])):
                    count += 1
                # upper right diagonal direction
                if self.inside([(r-4,c+4)]) and (self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [0,0,a,a,0]) \
                                             or self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [0,a,a,0,0])):
                    count += 1
                # lower right diagonal direction
                if self.inside([(r+4,c+4)]) and (self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [0,0,a,a,0]) \
                                              or self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [0,a,a,0,0])):
                    count += 1
        return count

    def winning_position(self, color_id):
        a = color_id
        for r in range(self.nrow):
            for c in range(self.ncol):
                for offset in range(0, 5):
                    others = list(filter(lambda x: x != offset, [0, 1, 2, 3, 4]))
                    o0, o1, o2, o3 = others[0], others[1], others[2], others[3]
                    # horizontal direction
                    if self.inside([(r,c+4)]) and self.check([(r,c+offset),(r,c+o0),(r,c+o1),(r,r+o2),(r,c+o3)], [0,a,a,a,a]):
                        return r, c+offset
                    # vertical direction
                    if self.inside([(r+4,c)]) and self.check([(r+offset,c),(r+o0,c),(r+o1,c),(r+o2,c),(r+o3,c)], [0,a,a,a,a]):
                        return r+offset, c
                    # upper right diagonal direction
                    if self.inside([(r-4,c+4)]) and self.check([(r-offset,c+offset),(r-o0,c+o0),(r-o1,c+o1),(r-o2,c+o2),(r-o3,c+o3)], [0,a,a,a,a]):
                        return r-offset, c+offset
                    # lower right diagonal direction
                    if self.inside([(r+4,c+4)]) and self.check([(r+offset,c+offset),(r+o0,c+o0),(r+o1,c+o1),(r+o2,c+o2),(r+o3,c+o3)], [0,a,a,a,a]):
                        return r+offset, c+offset
        return  -1, -1 # no winining position

    def game_over(self):
        for r in range(self.nrow):
            for c in range(self.ncol):
                for x in [self.computer_color, self.player_color]:
                    # horizontal direction
                    if self.inside([(r,c+4)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4)],[x,x,x,x,x]):
                        return x
                    # vertical direction
                    if self.inside([(r+4,r)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c)], [x,x,x,x,x]):
                        return x
                    # upper right direction
                    if self.inside([(r-4,c+4)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4)], [x,x,x,x,x]):
                        return x
                    # lower right direction
                    if self.inside([(r+4,c+4)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4)], [x,x,x,x,x]):
                        return x
        return -1 # game is not over yet.


    def nearby_moves(self, buffer_size=1):
        nearby_row_col = []
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.board[row][col] > 0:
                    row_max = min(row + buffer_size+1, self.nrow)
                    col_max = min(col + buffer_size+1, self.ncol)
                    row_min = max(row - buffer_size, 0)
                    col_min = max(col - buffer_size, 0)

                    for r in range(row_min, row_max):
                        for c in range(col_min, col_max):
                            if self.board[r][c] == 0 and (r, c) not in nearby_row_col:
                                nearby_row_col.append((r, c))
        return nearby_row_col

    def nearby_moves2(self):
        nearby_row_col = [[False for i in range(self.ncol)] for j in range(self.nrow)]
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.board[row][col] > 0:
                    row_max = min(row + 1, self.nrow)
                    col_max = min(col + 1, self.ncol)
                    row_min = max(row - 1, 0)
                    col_min = max(col - 1, 0)

                    for r in range(row_min, row_max + 1):
                        for c in range(col_min, col_max + 1):
                            nearby_row_col[r][c] = True

        return nearby_row_col

    def board_string_code(self):
        string_code = ""
        for row in range(self.nrow):
            for col in range(self.ncol):
                string_code += str(self.board[row][col])
        return string_code

    def evaluate_board_score(self, maximize_computer):
        self.print_board()
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

        print("computer_connected_five =", computer_connected_five)
        print("player_connected_five   =", player_connected_five)
        print("computer_open_four      =", computer_open_four)
        print("player_open_four        =", player_open_four)
        print("computer_open_three     =", computer_open_three)
        print("player_open_three       =", player_open_three)
        print("computer_open_two       =", computer_open_two)
        print("player_open_two         =", player_open_two)
        print("computer_closed_four    =", computer_closed_four)
        print("player_closed_four      =", player_closed_four)
        print("computer_closed_three   =", computer_closed_three)
        print("player_closed_three     =", player_closed_three)
        print("computer_closed_two     =", computer_closed_two)
        print("player_closed_two       =", player_closed_two)
        #computer_score = self.open_2_pts * computer_open_two + self.closed_2_pts * computer_closed_two \
        #                 + self.open_3_pts * computer_open_three + self.closed_3_pts * computer_closed_three \
        #                 + self.open_4_pts * computer_open_four + self.closed_4_pts * computer_closed_four \
        #                 + self.connected_5_pts * computer_connected_five

        #player_score = self.open_2_pts * player_open_two + self.closed_2_pts * player_closed_two \
        #               + (self.open_3_pts * player_open_three + self.closed_3_pts * player_closed_three \
        #                  + self.open_4_pts * player_open_four + self.closed_4_pts * player_closed_four \
        #                  + self.connected_5_pts * player_connected_five) * 10

        if maximize_computer:
            computer_score = 2*computer_open_two + 1*computer_closed_two +  200*computer_open_three + 20*computer_closed_three +  2000*computer_open_four +  200*computer_closed_four + 2000*computer_connected_five
            player_score   = 2*player_open_two   + 1*player_closed_two   + 2000*player_open_three   + 20*player_closed_three   + 20000*player_open_four   + 2000*player_closed_four  + 20000*player_connected_five
            return computer_score + player_score
        else:
            player_score   = 2*player_open_two + 1*player_closed_two +  200*player_open_three + 20*player_closed_three +  2000*player_open_four +  200*player_closed_four + 2000*player_connected_five
            computer_score = 2*computer_open_two   + 1*computer_closed_two   + 2000*computer_open_three   + 20*computer_closed_three   + 20000*computer_open_four   + 2000*computer_closed_four  + 20000*computer_connected_five
            return -1*(computer_score+player_score)

    def evaluate_board_score2(self):
        #self.print_board()
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

        score = 6000 * (computer_connected_five - player_connected_five)
        + 4800 * (computer_open_four - player_open_four)
        + 500 * (computer_closed_four - player_closed_four)
        + 500 * (computer_open_three - player_open_three)
        + 200 * (computer_closed_three - player_closed_three)
        + 50 * (computer_open_two - player_open_two)
        + 10 * (computer_closed_two - player_closed_two)

        print("evaluate2 ", score, computer_open_two, player_open_two)
        return score

    def get_move_greedy(self):
        # check the wining positions
        computer_win_row, computer_win_col = self.winning_position(self.computer_color)
        player_win_row, player_win_col = self.winning_position(self.player_color)
        if (computer_win_row, computer_win_col) != (-1, -1):
            return computer_win_row, computer_win_col
        if (player_win_row, player_win_col) != (-1, -1):
            return player_win_row, player_win_col
        open_four_row, open_four_col = self.find_open_four(self.computer_color)
        if (open_four_row, open_four_col) != (-1, -1):
            return open_four_row, open_four_col

        # greedy algorithm
        best_score = float("-inf")
        best_row, best_col = -1, -1
        possible_moves = self.nearby_moves(buffer_size=2)
        for (row, col) in possible_moves:
            score = self.evaluate_board_greedy(row,col)
            if best_score < score:
                best_score = score
                best_row, best_col = row, col
        return best_row, best_col

    def evaluate_board_greedy(self, row, col):
        # evaluate computer offense
        self.board[row][col] = self.computer_color
        computer_connected_five = self.count_five(self.computer_color)
        computer_open_four      = self.count_open_four(self.computer_color)
        computer_closed_four    = self.count_closed_four(self.computer_color)
        computer_open_three     = self.count_open_three(self.computer_color)
        computer_closed_three   = self.count_closed_three(self.computer_color)
        computer_open_two       = self.count_open_two(self.computer_color)
        computer_closed_two     = self.count_closed_two(self.computer_color)
        computer_double_three   = self.count_double_three(self.computer_color)
        if computer_double_three > 0:
            print("computer double three: row=%d, col=%d"%(row,col))
        self.board[row][col] = 0

        offend_score   = self.open_2_pts * computer_open_two + self.closed_2_pts * computer_closed_two \
                         + self.open_3_pts * computer_open_three + self.closed_3_pts * computer_closed_three \
                         + self.open_4_pts * computer_open_four + self.closed_4_pts * computer_closed_four \
                         + self.connected_5_pts * computer_connected_five + self.double_3_pts * computer_double_three

        # evaluate computer defense
        self.board[row][col] = self.player_color
        player_connected_five  = self.count_five(self.player_color)
        player_open_four       = self.count_open_four(self.player_color)
        player_closed_four     = self.count_closed_four(self.player_color)
        player_open_three      = self.count_open_three(self.player_color)
        player_closed_three    = self.count_closed_three(self.player_color)
        player_open_two        = self.count_open_two(self.player_color)
        player_closed_two      = self.count_closed_two(self.player_color)
        player_double_three    = self.count_double_three(self.player_color)

        if player_double_three > 0:
            print("player double three: row=%d, col=%d"%(row,col))
        self.board[row][col] = 0
        defend_score = self.open_2_pts * player_open_two + self.closed_2_pts * player_closed_two \
                       + (self.open_3_pts * player_open_three + self.closed_3_pts * player_closed_three \
                       + self.open_4_pts * player_open_four + self.closed_4_pts * player_closed_four \
                       + self.connected_5_pts * player_connected_five + self.double_3_pts * player_double_three)*2

        return offend_score + defend_score

    def get_move_wiki(self):
        computer_win_row, computer_win_col = self.winning_position(self.computer_color)
        player_win_row, player_win_col = self.winning_position(self.player_color)
        if (computer_win_row, computer_win_col) != (-1, -1):
            return computer_win_row, computer_win_col
        if (player_win_row, player_win_col) != (-1, -1):
            return player_win_row, player_win_col
        open_four_row, open_four_col = self.find_open_four(self.computer_color)
        if (open_four_row, open_four_col) != (-1, -1):
            return open_four_row, open_four_col

        depth = 0
        score = float("-inf")
        possible_moves = self.nearby_moves()
        best_row, best_col = possible_moves[0]
        debug_info = []
        for move_row, move_col in possible_moves:
            print("try (%d, %d)" %(move_row, move_col))
            self.board[move_row][move_col] = self.computer_color
            move_score = self.minimax_wiki(depth, True)
            debug_info.append({"position":(move_row, move_col), "score": move_score})
            if move_score > score:
                score = move_score
                best_row, best_col = move_row, move_col
            self.board[move_row][move_col] = 0 # restore current position
            self.minimax_records = {}  # clear catch
        print("get_move_wiki:")
        print(debug_info)
        return best_row, best_col

    def minimax_wiki(self, depth, maximize_computer_flag):
        if depth==0 or self.game_over() != -1:
            board_code = self.board_string_code()
            if board_code in self.minimax_records.keys():
                return self.minimax_records[board_code]
            else:
                score = self.evaluate_board_score(maximize_computer_flag)
                self.minimax_records[board_code] = score
                print("score: ", score)
                return score

        possible_moves = self.nearby_moves()
        if maximize_computer_flag:     # True, maximize computer
            score = float("-inf")
            debug_info = []
            for (move_row, move_col) in possible_moves:
                self.board[move_row][move_col] = self.player_color
                board_code = self.board_string_code()
                if board_code in self.minimax_records.keys():
                    move_score = self.minimax_records[board_code]
                else:
                    move_score = self.minimax_wiki(depth-1, False)
                self.board[move_row][move_col] = 0
                debug_info.append([(move_row, move_col), move_score])
                score = max(score, move_score)
            print("maximize computer: ")
            print(debug_info)
            print("max score: ", score)
            return score
        else:                         # False, maximize player by minimizing the score
            score = float("inf")
            debug_info = []
            for (move_row, move_col) in possible_moves:
                self.board[move_row][move_col] = self.computer_color
                board_code = self.board_string_code()
                if board_code in self.minimax_records.keys():
                    move_score = self.minimax_records[board_code]
                else:
                    move_score = self.minimax_wiki(depth-1, True)
                self.board[move_row][move_col] = 0
                debug_info.append([(move_row, move_col), move_score])
                score = min(score, move_score)
            print("minimize computer: ")
            print(debug_info)
            print("min score: ", score)
            return score

    def minimax2(self, current_depth, target_depth, maximize_player_flag, alpha, beta, possible_moves):
        # recursion function exit condition
        print("******")
        print("current_depth = ", current_depth)
        print("target_depth = ", target_depth)
        print("maximize_player_flag = ", maximize_player_flag)
        print("game_over = ", self.game_over())
        self.print_possible_moves(possible_moves)
        if current_depth == target_depth or self.game_over() != -1:
            board_code = self.board_string_code()
            if board_code in self.minimax_records.keys():
                return self.minimax_records[board_code]
            else:
                score = self.evaluate_board_score()
                self.minimax_records[board_code] = score
                print("score: ", score)
                return score


        print("current_depth", current_depth)
        # maximize player score
        if maximize_player_flag:
            print("maximize player")
            best_score = float("-inf")  # negative infinity
            for row in range(self.nrow):
                for col in range(self.ncol):
                    if possible_moves[row][col] == True and self.board[row][col] == 0:
                        print("minimize player by trying (%d, %d) for computer" %(row, col))
                        self.board[row][col] = self.computer_color
                        new_board_code = self.board_string_code()
                        if new_board_code in self.minimax_records.keys():
                            new_score = self.minimax_records[new_board_code]
                        else:
                            new_moves = self.nearby_moves2()
                            new_score = self.minimax2(current_depth + 1, target_depth, False, alpha, beta, new_moves)
                            self.minimax_records[new_board_code] = new_score
                        self.board[row][col] = 0
                        best_score = max(best_score, new_score)
                        #alpha = max(alpha, best_score)
                        #if beta <= alpha:
                        #    break
            return best_score
        else:
            best_score = float("inf")
            for row in range(self.nrow):
                for col in range(self.ncol):
                    if possible_moves[row][col] == True and self.board[row][col] == 0:
                        print("maximize computer by trying (%d, %d) for player" %(row, col))
                        self.board[row][col] = self.player_color
                        new_board_code = self.board_string_code()
                        if new_board_code in self.minimax_records.keys():
                            new_score = self.minimax_records[new_board_code]
                        else:
                            new_moves = self.nearby_moves2()
                            new_score = self.minimax2(current_depth + 1, target_depth, True, alpha, beta, new_moves)
                            self.minimax_records[new_board_code] = new_score
                        self.board[row][col] = 0
                        best_score = min(best_score, new_score)
                        #beta = min(beta, best_score)
                        #if beta <= alpha:
                        #    break
            return best_score

    def count_stone(self):
        count = 0
        for row in range(self.nrow):
            for col in range(self.ncol):
                if self.board[row][col] != 0:
                    count += 1
        return count

    def find_open_four(self, color_id):
        a = color_id
        # 0 A a a a 0
        # -           - current point, A, return point
        # 0 a a a A 0
        # -           - current point, A, return point
        for r in range(self.nrow):
            for c in range(self.ncol):
                # horizontal direction
                if self.inside([(r,c+5)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [0,0,a,a,a,0]):
                    return r, c+1
                if self.inside([(r,c+5)]) and self.check([(r,c),(r,c+1),(r,c+2),(r,c+3),(r,c+4),(r,c+5)], [0,a,a,a,0,0]):
                    return r, c+4
                # vertical direction
                if self.inside([(r+5,c)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [0,0,a,a,a,0]):
                    return r+1, c
                if self.inside([(r+5,c)]) and self.check([(r,c),(r+1,c),(r+2,c),(r+3,c),(r+4,c),(r+5,c)], [0,a,a,a,0,0]):
                    return r+4, c
                # upper right direction
                if self.inside([(r-5,c+5)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [0,0,a,a,a,0]):
                    return r-1, c+1
                if self.inside([(r-5,c+5)]) and self.check([(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3),(r-4,c+4),(r-5,c+5)], [0,a,a,a,0,0]):
                    return r-4, c+4
                # lower right direction
                if self.inside([(r+5,c+5)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)], [0,0,a,a,a,0]):
                    return r+1, c+1
                if self.inside([(r+5,c+5)]) and self.check([(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3),(r+4,c+4),(r+5,c+5)], [0,a,a,a,0,0]):
                    return r+4, c+4
        return -1, -1  # no open four

    def count_double_three(self, color_id):
        a = color_id
        count = 0
        for r in range(self.nrow):
            for c in range(self.ncol):
                # the algorithm requires that the current position is taken by color "a".
                if self.board[r][c] != a:
                    continue
                # (1)
                # ? 0 ? ? ? (r-3,c)
                # ? * ? ? ?
                # ? * ? ? ?
                # 0 x * * 0 (r,c-1) (r,c) (r,c+3)
                # ? 0 ? ? ? (r+1)
                if self.inside([(r-3,c),(r+1,c),(r,c-1),(r,c+3)]) \
                    and self.check([(r,c-1),(r,c),(r,c+1),(r,c+2),(r,c+3)], [0,a,a,a,0])\
                    and self.check([(r+1,c),(r,c),(r-1,c),(r-2,c),(r-3,c)], [0,a,a,a,0]):
                    print("1")
                    count += 1
                # (2)
                # ? ? ? ? 0 (r-3,c+3)
                # ? ? ? * ?
                # 0 ? * ? ? (r-1,c-1)
                # ? x ? ? ? (r,c)
                # 0 ? * ? ? (r+1,c-1)
                # ? ? ? * ?
                # ? ? ? ? 0 (r+3,c+3)
                if self.inside([(r-3,c+3),(r-1,c-1),(r+1,c-1),(r+3,c+3)]) \
                    and self.check([(r-1,c-1),(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3)], [0,a,a,a,0]) \
                    and self.check([(r+1,c-1),(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3)], [0,a,a,a,0]):
                    print("2")
                    count += 1
                # (3)
                # ? 0 ? ? ?   (r-1,c)
                # 0 x * * 0   (r,c-1), (r,c), (r,c+3)
                # ? * ? ? ?
                # ? * ? ? ?
                # ? 0 ? ? ?   (r+3, c)
                if self.inside([(r-1,c),(r,c-1),(r,c+3),(r+3,c)]) \
                    and self.check([(r,c-1),(r,c),(r,c+1),(r,c+2),(r,c+3)], [0,a,a,a,0]) \
                    and self.check([(r-1,c),(r,c),(r+1,c),(r+2,c),(r+3,c)], [0,a,a,a,0]):
                    print("3")
                    count += 1

                # (4)
                #  ? ? 0 ? 0 ? ?   (r-1,c-1), (r-1,c+1)
                #  ? ? ? x ? ? ?   (r,c)
                #  ? ? * ? * ? ?
                #  ? * ? ? ? * ?
                #  0 ? ? ? ? ? 0   (r+3,c-3), (r+3,c+3)
                if self.inside([(r-1,c-1),(r-1,c+1),(r+3,c-3),(r+3,c+3)]) \
                    and self.check([(r-1,c-1),(r,c),(r+1,c+1),(r+2,c+2),(r+3,c+3)], [0,a,a,a,0])\
                    and self.check([(r-1,c+1),(r,c),(r+1,c-1),(r+2,c-2),(r+3,c-3)], [0,a,a,a,0]):
                    print("4, r=%d, c=%d" %(r,c))
                    count += 1

                # (5)
                # ? ? ? 0 ?  (r-1,c)
                # 0 * * x 0  (r,c-3),(r,c),(r,c+1)
                # ? ? ? * ?
                # ? ? ? * ?
                # ? ? ? 0 ?  (r+3,c)
                if self.inside([(r-1,c),(r,c-3),(r,c+1),(r+3,c)]) \
                    and self.check([(r,c+1),(r,c),(r,c-1),(r,c-2),(r,c-3)], [0,a,a,a,0])\
                    and self.check([(r-1,c),(r,c),(r+1,c),(r+2,c),(r+3,c)], [0,a,a,a,0]):
                    print("5")
                    count += 1

                #(6)
                # 0 ? ? ? ?    (r-3, c-3)
                # ? * ? ? ?
                # ? ? * ? 0
                # ? ? ? x ?    (r, c)
                # ? ? * ? 0    (r+1, c+1)
                # ? * ? ? ?
                # 0 ? ? ? ?    (r+3, c-3)
                if self.inside([(r-3,c-3),(r+1,c+1),(r+3,c-3)]) \
                    and self.check([(r-1,c+1),(r,c),(r+1,c-1),(r+2,c-2),(r+3,c-3)],[0,a,a,a,0])\
                    and self.check([(r+1,c+1),(r,c),(r-1,c-1),(r-2,c-2),(r-3,c-3)],[0,a,a,a,0]):
                    print("6")
                    count += 1

                # (7)
                # ? ? ? 0 ? (r-3, c)
                # ? ? ? * ?
                # ? ? ? * ?
                # 0 * * x 0 (r, c-3), (r,c), (r, c+1)
                # ? ? ? 0 ? (r+1, c)
                if self.inside([(r-3,c),(r,c-3),(r,c+1),(r+1,c)]) \
                    and self.check([(r,c+1),(r,c),(r,c-1),(r,c-2),(r,c-3)],[0,a,a,a,0]) \
                    and self.check([(r+1,c),(r,c),(r-1,c),(r-2,c),(r-3,c)],[0,a,a,a,0]):
                    print("7")
                    count += 1

                # (8)
                # 0 ? ? ? ? ? 0 (r-3, c-3), (r-3, c+3)
                # ? * ? ? ? * ?
                # ? ? * ? * ? ?
                # ? ? ? x ? ? ?  (r, c)
                # ? ? 0 ? 0 ? ? (r+1, c-1), (r+1, c+1)
                if self.inside([(r-3,c-3),(r-3,c+3),(r+1,c-1),(r+1,c+1)]) \
                    and self.check([(r+1,c-1),(r,c),(r-1,c+1),(r-2,c+2),(r-3,c+3)], [0,a,a,a,0]) \
                    and self.check([(r+1,c+1),(r,c),(r-1,c-1),(r-2,c-2),(r-3,c-3)], [0,a,a,a,0]):
                    print("8")
                    count += 1

                # (9)
                # ? ? 0 ? ?   (r-2, c)
                # ? ? * ? ?
                # 0 * x * 0   (r, c-2), (r, c), (r, c+2)
                # ? ? * ? ?
                # ? ? 0 ? ?   (r+2, c)
                if self.inside([(r-2, c), (r+2, c), (r, c-2), (r, c+2)]) \
                        and self.check([(r-2,c), (r-1,c), (r,c), (r+1,c), (r+2,c)], [0,a,a,a,0]) \
                        and self.check([(r,c-2), (r,c-1), (r,c), (r,c+1), (r,c+2)], [0,a,a,a,0]):
                    print("9")
                    count += 1

                # (10)
                # 0 ? ? ? 0    (r-2, c-2), (r-2, c+2)
                # ? * ? * ?
                # ? ? x ? ?    (r, c)
                # ? * ? * ?
                # 0 ? ? ? 0    (r+2, c-2), (r+2, c+2)
                if self.inside([(r-2, c-2), (r-2, c+2), (r+2, c-2), (r+2, c+2)]) \
                    and self.check([(r-2,c-2), (r-1,c-1), (r,c), (r+1,c+1), (r+2,c+2)], [0,a,a,a,0]) \
                    and self.check([(r+2,c-2), (r+1,c-1), (r,c), (r-1,c+1), (r-2,c+2)], [0,a,a,a,0]):
                    print("10")
                    count += 1

                # (11)
                # ? ? ? ? 0 ?   (r-1, c+1)
                # ? 0 * x * 0   (r, c-2), (r,c), (r, c+2)
                # ? ? * ? ? ?
                # ? * ? ? ? ?
                # 0 ? ? ? ? ?   (r+3,c-3)
                if self.inside([(r-1,c+1), (r,c+2), (r+3,c-3)]) \
                    and self.check([(r+3,c-3),(r+2,c-2),(r+1,c-1),(r,c),(r-1,c+1)], [0,a,a,a,0]) \
                    and self.check([(r,c-2),(r,c-1),(r,c),(r,c+1),(r,c+2)], [0,a,a,a,0]):
                    print("11")
                    count += 1

                # (12)
                # ? 0 ? ? ? ?    (r-2,c-2)
                # ? ? * ? ? ?
                # 0 * * x 0 ?    (r, c-3) (r,c) (r, c+1)
                # ? ? ? ? * ?
                # ? ? ? ? ? 0    (r+2, c+2)
                if self.inside([(r-2,c-2), (r+2,c+2), (r,c-3)]) \
                    and self.check([(r,c-3), (r,c-2), (r,c-1), (r,c), (r,c+1)], [0, a, a, a, 0]) \
                    and self.check([(r-2,c-2), (r-1,c-1), (r,c), (r+1,c+1), (r+2,c+2)], [0, a, a, a, 0]):
                    print("12")
                    count += 1
                # (13)
                # 0 ? ? ? ?     (r-3, c-3)
                # ? * ? 0 ?     (r-2,c)
                # ? ? * * ?
                # ? ? ? x ?     (r, c)
                # ? ? ? * 0     (r+1, c+1)
                # ? ? ? 0 ?     (r+2, c)
                #    and self.check([(), (), (), (), ()], [0, a, a, a, 0])
                if self.inside([(r-3,c-3), (r+1,c+1), (r+2,c)]) \
                    and self.check([(r-3,c-3), (r-2,c-2), (r-1,c-1), (r,c), (r+1,c+1)], [0, a, a, a, 0])\
                    and self.check([(r-2,c), (r-1,c), (r,c), (r+1,c), (r+2,c)], [0, a, a, a, 0]):
                    print("13")
                    count += 1

                # (14)
                # ? ? 0 ? ?    (r-3, c)
                # ? ? * ? 0    (r-2,c+2)
                # ? ? * * ?
                # ? ? x ? ?    (r, c)
                # ? * 0 ? ?
                # 0 ? ? ? ?    (r+2, c-2)
                if self.inside([(r-3,c), (r-2,c+2), (r+2,c-2)]) \
                    and self.check([(r+2,c-2), (r+1,c-1), (r,c), (r-1,c+1), (r-2,c+2)], [0, a, a, a, 0])\
                    and self.check([(r-3,c), (r-2,c), (r-1,c), (r,c), (r+1,c)], [0, a, a, a, 0]):
                    print("14")
                    count += 1
                # (15)
                # ? ? ? ? ? 0  (r-3,c+3)
                # ? ? ? ? * ?
                # ? ? ? * ? ?
                # 0 * x * 0 ?   (r, c-2) (r,c)
                # ? 0 ? ? ? ?   (r+1, c-1)
                if self.inside([(r+1,c-1), (r,c-2), (r-3,c+3)]) \
                    and self.check([(r+1,c-1), (r,c), (r-1,c+1), (r-2,c+2), (r-3,c+3)], [0, a, a, a, 0]) \
                    and self.check([(r,c-2), (r,c-1), (r,c), (r,c+1), (r,c+2)], [0, a, a, a, 0]):
                    prin("15")
                    count += 1
                # (16)
                # 0 ? ? ? ? ?    (r-2,c-2)
                # ? * ? ? ? ?
                # ? 0 x * * 0    (r,c), (r, c+3)
                # ? ? ? * ? ?
                # ? ? ? ? 0 ?    (r+2,c+2)
                if self.inside([(r-2,c-2), (r,c+3), (r+2,c+2)]) \
                    and self.check([(r-2,c-2), (r-1,c-1), (r,c), (r+1,c+1), (r+2,c+2)], [0, a, a, a, 0]) \
                    and self.check([(r,c-1), (r,c), (r,c+1), (r,c+2), (r,c+3)], [0, a, a, a, 0]):
                    print("16")
                    count += 1

                # (17)
                # ? 0 ? ? ? (r-2,c)
                # 0 * ? ? ?  (r-1,c-1)
                # ? x ? ? ? (r,c)
                # ? * * ? ?
                # ? 0 ? * ?
                # ? ? ? ? 0 (r+3,c+3)
                if self.inside([(r-2,c), (r-1,c-1), (r+3,c+3)])\
                    and self.check([(r-2,c), (r-1,c), (r,c), (r+1,c), (r+2,c)], [0, a, a, a, 0])\
                    and self.check([(r-1,c-1), (r,c), (r+1,c+1), (r+2,c+2), (r+3,c+3)], [0, a, a, a, 0]):
                    print("17")
                    count += 1
                # (18)
                # ? ? ? ? 0 ?    (r-2, c+2)
                # ? ? 0 * ? ?
                # ? ? x ? ? ?    (r, c)
                # ? * * ? ? ?
                # 0 ? * ? ? ?    (r+2, c-2)
                # ? ? 0 ? ? ?    (r+3,c)
                if self.inside([(r-2,c+2), (r+2,c-2), (r+3,c)]) \
                    and self.check([(r+2,c-2), (r+1,c-1), (r,c), (r-1,c+1), (r-2,c+2)], [0, a, a, a, 0]) \
                    and self.check([(r-1,c), (r,c), (r+1,c), (r+2,c), (r+3,c)], [0, a, a, a, 0]):
                    print("18")
                    count += 1
        return count

    def check(self, stone_row_col_list, pattern):
        result = True
        for k in range(len(stone_row_col_list)):
            row, col = stone_row_col_list[k]
            result = result and (self.board[row][col] == pattern[k])
        return result

    def inside(self, stones):
        for row, col in stones:
            if not ((0 <= row < self.nrow) and (0 <= col < self.ncol)):
                return False
        return True


    def print_possible_moves(self, possible_moves):
        print("possible moves: ")
        for row in range(self.nrow):
            for col in range(self.ncol):
                if possible_moves[row][col]==True:
                    print("(%d, %d)" %(row, col), end=" ")
        print("")

    def get_move2(self):
        #stone_count = self.count_stone()
        #if stone_count == 0:
        #    return [int(self.nrow / 2), int(self.ncol / 2)]
        #current_depth = stone_count + 1
        #target_depth = current_depth + 1
        current_depth = 1
        target_depth  = 2
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
        move_list = []
        position = []
        possible_moves = self.nearby_moves2()
        # print("possible_moves", possible_moves)
        alpha0 = float("-inf")
        beta0 = float("inf")
        for row in range(self.nrow):
            for col in range(self.ncol):
                if possible_moves[row][col] == True and self.board[row][col] == 0:
                    self.board[row][col] = self.computer_color
                    print("get_move2")
                    self.print_board()
                    new_moves = self.nearby_moves2()
                    move_score = self.minimax2(current_depth, target_depth, False, alpha0, beta0, new_moves)
                    self.board[row][col] = 0
                    print("get_move2, row=%d col=%d score=%f" % (row, col, move_score))
                    if move_score > score:
                        score = move_score
                        position = [row, col]
                    if move_score > best_low:
                        if len(best_list) == 0:
                            best_list.append({"position": (row, col), "score": move_score})
                        else:
                            for n in range(len(best_list)):
                                if move_score >= best_list[n]["score"]:
                                    best_list.insert(n, {"position": (row, col), "score": move_score})
                                    break
                            # if len(best_list)>4:
                            #    best_list = best_list[0:4]
                        best_low = best_list[0]["score"]
        self.minimax_records = {}
        print("best_list", best_list)
        chosen = random.randint(0, len(best_list) - 1)
        return best_list[chosen]["position"]

    def show_possible_moves(self, possible_moves):
        for row, col in possible_moves:
            x, y = self.get_xy(row, col)
            new_circle = circle(color=mc.blue, width=32, height=32)
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

        new_circle = circle(color=mc.black, width=32, height=32)
        new_circle.set_position(x - new_circle.width // 2, y - new_circle.height // 2)
        self.button_group.add(new_circle)
        #pygame.display.update()
        #self.clock_tick()
        self.display_update()

        self.board[r][c] = self.player_color
        if self.game_over() == self.player_color:
            pygame.display.set_caption(u"五子棋（Gomoku）: player win!")
            self.end_game_flag = True
            return

        # set flag
        self.ready_for_human_move_flag = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAIT)
        # computer move
        #move_row, move_col = self.get_move_wiki()
        move_row, move_col = self.get_move_greedy()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW )
        self.ready_for_human_move_flag = True
        # print("computer move: %d %d" %(move_row, move_col))
        # computer
        self.board[move_row][move_col] = self.computer_color
        move_x, move_y = self.get_xy(move_row, move_col)
        new_circle = circle(color=mc.white, width=32, height=32)
        new_circle.set_position(move_x - new_circle.width // 2, move_y - new_circle.height // 2)
        self.button_group.add(new_circle)
        pygame.display.update()

        if self.game_over() == self.computer_color:
            pygame.display.set_caption(u"五子棋（Gomoku）: computer win!")
            self.end_game_flag = True

    def ready_for_human_move(self):
        return self.ready_for_human_move_flag

    def good_for_move(self, mouse_x=None, mouse_y=None):
        x, y = self.XY.get_xy(mouse_x=mouse_x, mouse_y=mouse_y, button_radius=16)
        r, c = self.XY.get_row_col(x, y)
        if (x == -1 and y == -1) or self.board[r][c] == 1 or self.board[r][c] == 2:
            return False
        else:
            return True

    #def draw_board(self, x_margin=100, y_margin=100, nrow=15, ncol=15):
    def draw_board(self, x_margin=100, y_margin=100, nrow=15, ncol=15):
        x0, y0, x1, y1 = self.window.get_rect()
        width  = self.x_interval * (ncol - 1)
        height = self.y_interval * (ncol - 1) + 3

        # print(x_interval, y_interval, width, height)
        board_group = pygame.sprite.Group()
        pygame.font.init()
        myfont = pygame.font.SysFont('Helvetica', 20)

        for row in range(0, nrow):
            x = self.x_margin
            y = self.y_margin + row * self.y_interval
            new_hline = hline(width=width, x=x, y=y - 1)
            board_group.add(new_hline)
            # draw label
            label = myfont.render("%2d"%row, False, (0, 0, 255))
            self.window.blit(label, (x-30, y-10))
            self.window.blit(label, (x+width+10, y-10))

        for col in range(0, ncol):
            x = self.x_margin + col * self.x_interval
            y = self.y_margin
            new_vline = vline(height=height, x=x - 1, y=y - 1)
            board_group.add(new_vline)
            # draw label
            label = myfont.render("%2d"%col, False, (0, 0, 255))
            self.window.blit(label, (x-10, y-30))
            self.window.blit(label, (x-10, y+height+10))

        board_group.draw(self.window)
        pygame.display.update()

    def display_update(self):
        self.button_group.draw(self.window)
        pygame.display.update()
