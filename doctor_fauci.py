import pygame
from random import randint

FRAME_RATE = 30

ROWS = 16
COLUMNS = 8

WINDOW_INITIAL_WIDTH = 800
WINDOW_INITIAL_HEIGHT = 800

BOARD_TOP_LEFT_X = int(0.275 * WINDOW_INITIAL_WIDTH)
BOARD_TOP_LEFT_Y = int(0.01 * WINDOW_INITIAL_HEIGHT)

BOARD_WIDTH = WINDOW_INITIAL_WIDTH * 0.45
BOARD_HEIGHT = WINDOW_INITIAL_HEIGHT * 0.96

BLOCK_WIDTH = int(BOARD_WIDTH / COLUMNS)
BLOCK_HEIGHT = int(BOARD_HEIGHT / ROWS)

BOARD_TOP_MIDDLE_LEFT_X = BOARD_TOP_LEFT_X + 3 * BLOCK_WIDTH
BOARD_TOP_MIDDLE_RIGHT_X = BOARD_TOP_LEFT_X + 4 * BLOCK_WIDTH


BACKGROUND_COLOR = pygame.Color(255, 255, 255)
BOARD_COLOR = pygame.Color(0, 0, 0)
GRID_COLOR = pygame.Color(80, 80, 80)

VIR_RED = pygame.image.load('VirusRed.png')
VIR_RED = pygame.transform.scale(VIR_RED, (BLOCK_WIDTH, BLOCK_HEIGHT))

VIR_GREEN = pygame.image.load('VirusGreen.png')
VIR_GREEN = pygame.transform.scale(VIR_GREEN, (BLOCK_WIDTH, BLOCK_HEIGHT))

VIR_BLUE = pygame.image.load('VirusBlue.png')
VIR_BLUE = pygame.transform.scale(VIR_BLUE, (BLOCK_WIDTH, BLOCK_HEIGHT))

FAUCI = pygame.image.load('Fauci.png')


class Game:
    def __init__(self):
        self.running = True
        self.loss = False
        self.level = 1
        self.state = BoardState(self.level)
        self.tick_count = 0

    def run(self) -> None:
        """Run the game."""
        pygame.init()
        pygame.display.set_caption('Dr. Fauci World')

        try:
            clock = pygame.time.Clock()
            self._create_surface((WINDOW_INITIAL_WIDTH, WINDOW_INITIAL_HEIGHT))
            self.state.add_viruses()

            while self.running:
                clock.tick(30)
                self.tick_count += 30

                if self.state.need_new_piece:
                    self.gravity()
                    if not self.lose():
                        self.get_new_piece()

                if self.running:
                    self.falling()
                    self.handle_events()
                    self.draw_frame()
                    self.execute_matches()
                    if self.level_complete():
                        self.level += 1
                        self.state = BoardState(self.level)
                        self.tick_count = 0
                        self.state.add_viruses()

            while self.loss:
                clock.tick(30)
                self.handle_loss()

        finally:
            pygame.quit()

    def handle_loss(self):
        end = False
        while not end:
            end = self.get_end_event()
            self.draw_loss_background()
            self.draw_text()
            pygame.display.flip()

    def draw_loss_background(self):
        self.surface.fill(pygame.Color(0, 0, 0))

    def draw_text(self):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 40)
        text = font.render('Game Over', True, pygame.Color(255, 255, 255))
        text_rect = text.get_rect()
        text_x = int(self.surface.get_width() / 2 - text_rect.width / 2)
        text_y = int(self.surface.get_height() / 2 - text_rect.height / 2)
        self.surface.blit(text, (text_x, text_y))

    def get_end_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.loss = False
                return True
            else:
                return False

    def lose(self):
        if (BOARD_TOP_MIDDLE_LEFT_X, BOARD_TOP_LEFT_Y) in self.state.locked_pieces or (BOARD_TOP_MIDDLE_RIGHT_X, BOARD_TOP_LEFT_Y) in self.state.locked_pieces:
            self.running = False
            self.loss = True
            return True
        else:
            return False

    def gravity(self):
        for i in range(15):
            if self.state.locked_pieces != {}:
                for coord, color in list(self.state.locked_pieces.items()):
                    if coord not in self.state.virus_pieces:
                        x, y = coord
                        if y < BOARD_TOP_LEFT_Y + 15 * BLOCK_HEIGHT:
                            if (x, y + BLOCK_HEIGHT) not in self.state.locked_pieces.keys():
                                self.state.locked_pieces.pop((x, y))
                                self.state.locked_pieces[x, y + BLOCK_HEIGHT] = color

    def execute_matches(self):
        horizontals = self.check_horizontal_matches()
        verticals = self.check_vertical_matches()
        all_matches = horizontals + verticals
        all_matches = list(set(all_matches))
        for coord in all_matches:
            self.state.locked_pieces.pop(coord)
            if coord in self.state.virus_pieces:
                self.state.virus_pieces.pop(coord)
                self.state.num_viruses -= 1

    def check_horizontal_matches(self):
        coords = [coord for coord in self.state.locked_pieces.keys()]
        matches = []
        for i in range(1, 17):
            row_list_coords = []
            row_list_colors = []
            for j in range(BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_X + 8 * BLOCK_WIDTH, BLOCK_WIDTH):
                if (j, BOARD_TOP_LEFT_Y + i * BLOCK_HEIGHT) in coords:
                    row_list_coords.append((j, BOARD_TOP_LEFT_Y + i*BLOCK_HEIGHT))
                    row_list_colors.append(self.state.locked_pieces[j, BOARD_TOP_LEFT_Y + i*BLOCK_HEIGHT])
                else:
                    row_list_coords.append((j, BOARD_TOP_LEFT_Y + i * BLOCK_HEIGHT))
                    row_list_colors.append(pygame.Color(0, 0, 0))

            for k in range(1, len(row_list_coords) - 1):
                if row_list_colors[k-1] != pygame.Color(0, 0, 0):
                    a = row_list_colors[k-1]
                    b = row_list_colors[k]
                    c = row_list_colors[k+1]
                    if a == b == c:
                        matches.append(row_list_coords[k-1])
                        matches.append(row_list_coords[k])
                        matches.append(row_list_coords[k+1])

        matches = list(set(matches))
        return matches

    def check_vertical_matches(self):
        coords = [coord for coord in self.state.locked_pieces.keys()]
        matches = []
        for i in range(0, 9):
            column_list_coords = []
            column_list_colors = []
            for j in range(BOARD_TOP_LEFT_Y, BOARD_TOP_LEFT_Y + 16 * BLOCK_HEIGHT, BLOCK_HEIGHT):
                if (BOARD_TOP_LEFT_X + i * BLOCK_WIDTH, j) in coords:
                    column_list_coords.append((BOARD_TOP_LEFT_X + i * BLOCK_WIDTH, j))
                    column_list_colors.append(self.state.locked_pieces[BOARD_TOP_LEFT_X + i * BLOCK_WIDTH, j])
                else:
                    column_list_coords.append((BOARD_TOP_LEFT_X + i * BLOCK_WIDTH, j))
                    column_list_colors.append(pygame.Color(0, 0, 0))

            for k in range(1, len(column_list_coords) - 1):
                if column_list_colors[k-1] != pygame.Color(0, 0, 0):
                    a = column_list_colors[k-1]
                    b = column_list_colors[k]
                    c = column_list_colors[k+1]
                    if a == b == c:
                        matches.append(column_list_coords[k - 1])
                        matches.append(column_list_coords[k])
                        matches.append(column_list_coords[k + 1])

        matches = list(set(matches))
        return matches

    def get_new_piece(self):
        self.state.current_piece = Piece()
        self.state.need_new_piece = False

    def falling(self):
        if self.tick_count % 300 == 0:
            if not self.state.current_piece.lower(self.state.locked_pieces):
                for i in range(2):
                    self.state.locked_pieces[
                        (self.state.current_piece.body[i].top_left_x, self.state.current_piece.body[i].top_left_y)] = \
                        self.state.current_piece.body[i].color
                self.state.need_new_piece = True
            else:
                for i in range(2):
                    self.state.current_piece.body[i].top_left_y += BLOCK_HEIGHT

    def draw_piece(self):
        for i in range(2):
            tlx, tly = self.state.current_piece.body[i].get_top_left()
            pygame.draw.rect(self.surface, self.state.current_piece.body[i].color,
                             (int(tlx), int(tly), BLOCK_WIDTH, BLOCK_HEIGHT))

    def handle_events(self) -> None:
        """Handle key and mouse clicks."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()

            if event.type == pygame.VIDEORESIZE:
                self._create_surface(event.size)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.state.current_piece.move_left(self.state.locked_pieces):
                        for i in range(2):
                            self.state.current_piece.body[i].top_left_x -= BLOCK_WIDTH

                if event.key == pygame.K_RIGHT:
                    if self.state.current_piece.move_right(self.state.locked_pieces):
                        for i in range(1, -1, -1):
                            self.state.current_piece.body[i].top_left_x += BLOCK_WIDTH

                if event.key == pygame.K_SPACE:
                    pass

    def draw_frame(self):
        self.surface.fill(BACKGROUND_COLOR)
        self.draw_fauci()
        self.draw_board()
        self.draw_previous_orbs()
        self.draw_viruses()
        self.draw_grid()
        self.draw_piece()
        pygame.display.flip()

    def draw_fauci(self):
        self.surface.blit(FAUCI, (-50, 200))

    def draw_viruses(self):
        for coord in self.state.virus_pieces:
            if self.state.virus_pieces[coord] == pygame.Color(255, 0, 0):
                self.surface.blit(VIR_RED, coord)
            elif self.state.virus_pieces[coord] == pygame.Color(0, 255, 0):
                self.surface.blit(VIR_GREEN, coord)
            elif self.state.virus_pieces[coord] == pygame.Color(0, 0, 255):
                self.surface.blit(VIR_BLUE, coord)

    def draw_board(self) -> None:
        """Draw the board."""
        pygame.draw.rect(self.surface, BOARD_COLOR,
                         (int(BOARD_TOP_LEFT_X),
                          int(BOARD_TOP_LEFT_Y),
                          int(BOARD_WIDTH),
                          int(BOARD_HEIGHT))
                         )

    def draw_grid(self) -> None:
        """Draw the grid onto the board."""
        for i in range(COLUMNS + 1):
            pygame.draw.line(self.surface, GRID_COLOR,
                             (int(BOARD_TOP_LEFT_X + i * BLOCK_WIDTH), int(BOARD_TOP_LEFT_Y)),
                             (int(BOARD_TOP_LEFT_X + i * BLOCK_WIDTH), int(BOARD_TOP_LEFT_Y + BOARD_HEIGHT))
                             )

        for j in range(ROWS + 1):
            pygame.draw.line(self.surface, GRID_COLOR,
                             (int(BOARD_TOP_LEFT_X), int(BOARD_TOP_LEFT_Y + j * BLOCK_HEIGHT)),
                             (int(BOARD_TOP_LEFT_X + BOARD_WIDTH), int(BOARD_TOP_LEFT_Y + j * BLOCK_HEIGHT))
                             )

    def draw_previous_orbs(self):
        for coord, color in self.state.locked_pieces.items():
            pygame.draw.rect(self.surface, color,
                             (int(coord[0]), int(coord[1]), BLOCK_WIDTH, BLOCK_HEIGHT))

    def _create_surface(self, size) -> None:
        """Create the surface."""
        self.surface = pygame.display.set_mode(size)

    def level_complete(self):
        """Checks if it's time to advance to next lvl"""
        if self.state.num_viruses == 0:
            return True
        return False

    def _quit_game(self):
        """Quit."""
        self.running = False


class BoardState:
    def __init__(self, level):
        self.colors = [pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255)]
        self.current_piece = None
        self.need_new_piece = True
        self.lose = False
        self.need_event_move = True
        self.game_level = level
        self.total_viruses = 4 * self.game_level
        self.num_viruses = 4 * self.game_level
        self.locked_pieces = {}
        self.virus_pieces = {}

    def add_viruses(self):
        while len(list(self.locked_pieces)) != self.total_viruses:
            x = randint(0, 7)
            y = randint(8, 15)
            col = randint(0, 2)
            coord = BOARD_TOP_LEFT_X + x * BLOCK_WIDTH, BOARD_TOP_LEFT_Y + y * BLOCK_HEIGHT
            if coord not in self.locked_pieces:
                self.locked_pieces[coord] = self.colors[col]
                self.virus_pieces[coord] = self.colors[col]


class Piece:
    def __init__(self):
        self.body = self.create_body()

    def create_body(self):
        """Create orbs for the piece"""
        body = [Pill(BOARD_TOP_MIDDLE_LEFT_X, BOARD_TOP_LEFT_Y), Pill(BOARD_TOP_MIDDLE_RIGHT_X, BOARD_TOP_LEFT_Y)]
        return body

    def lower(self, locked_pos):
        can_lower = True
        for i in range(len(self.body)):
            if self.body[i].attempt_lower(locked_pos):
                pass
            else:
                can_lower = False

        return can_lower

    def move_left(self, locked_pos):
        can_left = True
        for i in range(len(self.body)):
            if self.body[i].attempt_left(locked_pos):
                pass
            else:
                can_left = False

        return can_left

    def move_right(self, locked_pos):
        can_right = True
        for i in range(1, -1, -1):
            if self.body[i].attempt_right(locked_pos):
                pass
            else:
                can_right = False

        return can_right


class Orb(object):
    def __init__(self, x, y):
        self.colors = [pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255)]
        self.color = self.create_body()
        self.top_left_x = x
        self.top_left_y = y

    def create_body(self):
        color_num = randint(0, 2)
        color = self.colors[color_num]
        return color

    def get_top_left(self) -> (float, float):
        """Get the top left coordinate of the faller."""
        self.top_left = (self.top_left_x, self.top_left_y)
        return self.top_left


class Pill(Orb):
    def attempt_lower(self, locked_pos):
        if self.top_left_y <= BOARD_TOP_LEFT_Y + (ROWS - 2) * BLOCK_HEIGHT:
            prev_pos = list(locked_pos.keys())
            if (self.top_left_x, self.top_left_y + BLOCK_HEIGHT) not in prev_pos:
                return True
            else:
                return False

        return False

    def attempt_left(self, locked_pos):
        if BOARD_TOP_LEFT_X < self.top_left_x <= BOARD_TOP_LEFT_X + ((COLUMNS - 1) * BLOCK_WIDTH):
            prev_pos = list(locked_pos.keys())
            if (self.top_left_x - BLOCK_WIDTH, self.top_left_y) not in prev_pos:
                return True
            else:
                return False
        return False

    def attempt_right(self, locked_pos):
        if BOARD_TOP_LEFT_X <= self.top_left_x < BOARD_TOP_LEFT_X + ((COLUMNS - 1) * BLOCK_WIDTH):
            prev_pos = list(locked_pos.keys())
            if (self.top_left_x + BLOCK_WIDTH, self.top_left_y) not in prev_pos:
                return True
            else:
                return False
        return False

    def pill_image(self):
        if self.color == 'whatever color':
            # BLIT IMAGE HERE
            pass
        elif self.color == 'asdf':
            pass
        elif self.color == 'asdf':
            pass


class Virus(Orb):
    def virus_image(self):
        if self.color == 'whatever color':
            # BLIT IMAGE HERE
            pass
        elif self.color == 'asdf':
            pass
        elif self.color == 'asdf':
            pass


def main():
    Game().run()


if __name__ == '__main__':
    main()
