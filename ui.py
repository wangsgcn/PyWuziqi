import math
import mycolors as mc
import pygame
import pygame.gfxdraw

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

class circle(pygame.sprite.Sprite):
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

class board_xy:
    def __init__(self, nrow=15, ncol=15, board_width=800, board_height=800, x_margin=100, y_margin=100):
        self.nrow = nrow
        self.ncol = ncol
        self.board_width = board_width
        self.board_height = board_height
        self.X = [[0 for i in range(self.ncol)] for j in range(self.nrow)]
        self.Y = [[0 for i in range(self.ncol)] for j in range(self.nrow)]
        self.x_interval = (board_width  - 2 * x_margin) // (ncol - 1)
        self.y_interval = (board_height - 2 * y_margin) // (nrow - 1)
        self.x_margin = (self.board_width  - self.x_interval * (ncol-1)) // 2
        self.y_margin = (self.board_height - self.y_interval * (nrow-1)) // 2
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
        return self.X[row][col], self.Y[row][col]
