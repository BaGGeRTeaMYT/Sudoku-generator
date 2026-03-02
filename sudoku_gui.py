import pygame
import sys
from sudoku_generator import SudokuGenerator

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
GRID_SIZE = 540
CELL_SIZE = GRID_SIZE // 9
MARGIN = (WINDOW_WIDTH - GRID_SIZE) // 2
TOP_MARGIN = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (200, 200, 255)
LIGHT_RED = (255, 200, 200)
LIGHT_GREEN = (200, 255, 200)

class SudokuGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sudoku Generator")
        self.font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 24)
        
        self.generator = SudokuGenerator()
        self.selected = None
        self.user_board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.error_cells = set()
        self.highlighted_cells = set()
        self.shift_pressed = False
        self.solved = False
        
        self.new_game()

    def new_game(self):
        puzzle = self.generator.generate_puzzle()
        self.original_board = [row[:] for row in puzzle]
        self.user_board = [row[:] for row in puzzle]
        self.error_cells = set()
        self.highlighted_cells = set()
        self.solved = False
        self.selected = None

    def update_highlights(self):
        self.highlighted_cells = set()
        if self.shift_pressed and self.selected:
            row, col = self.selected
            val = self.user_board[row][col]
            if val != 0:
                for r in range(9):
                    for c in range(9):
                        if self.user_board[r][c] == val:
                            self.highlighted_cells.add((r, c))

    def draw_grid(self):
        # Draw cells
        for i in range(9):
            for j in range(9):
                x = MARGIN + j * CELL_SIZE
                y = TOP_MARGIN + i * CELL_SIZE
                
                # Background color
                color = WHITE
                if (i, j) in self.error_cells:
                    color = LIGHT_RED
                elif (i, j) in self.highlighted_cells:
                    color = GRAY
                elif self.selected == (i, j):
                    color = LIGHT_BLUE
                
                pygame.draw.rect(self.screen, color, (x, y, CELL_SIZE, CELL_SIZE))
                
                # Draw value
                val = self.user_board[i][j]
                if val != 0:
                    color = BLACK if self.original_board[i][j] != 0 else BLUE
                    if self.solved and self.original_board[i][j] == 0:
                        color = GREEN
                        
                    text = self.font.render(str(val), True, color)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)

        # Draw lines
        for i in range(10):
            thickness = 4 if i % 3 == 0 else 1
            # Horizontal
            pygame.draw.line(self.screen, BLACK, 
                           (MARGIN, TOP_MARGIN + i * CELL_SIZE), 
                           (MARGIN + GRID_SIZE, TOP_MARGIN + i * CELL_SIZE), thickness)
            # Vertical
            pygame.draw.line(self.screen, BLACK, 
                           (MARGIN + i * CELL_SIZE, TOP_MARGIN), 
                           (MARGIN + i * CELL_SIZE, TOP_MARGIN + GRID_SIZE), thickness)

    def draw_buttons(self):
        button_y = TOP_MARGIN + GRID_SIZE + 30
        button_width = 120
        button_height = 40
        spacing = 30
        
        buttons = [
            ("New Game", self.new_game),
            ("Check", self.check_solution),
            ("Solve", self.solve_game)
        ]
        
        start_x = (WINDOW_WIDTH - (len(buttons) * button_width + (len(buttons) - 1) * spacing)) // 2
        
        self.button_rects = []
        for i, (text, action) in enumerate(buttons):
            x = start_x + i * (button_width + spacing)
            rect = pygame.Rect(x, button_y, button_width, button_height)
            self.button_rects.append((rect, action))
            
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            text_surf = self.small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def check_solution(self):
        self.error_cells = set()
        is_complete = True
        is_correct = True
        
        for i in range(9):
            for j in range(9):
                val = self.user_board[i][j]
                if val == 0:
                    is_complete = False
                elif val != self.generator.solution[i][j]:
                    self.error_cells.add((i, j))
                    is_correct = False
        
        if is_complete and is_correct:
            self.solved = True

    def solve_game(self):
        if self.generator.solution:
            self.user_board = [row[:] for row in self.generator.solution]
            self.solved = True
            self.error_cells = set()

    def handle_click(self, pos):
        x, y = pos
        
        # Check grid click
        if (MARGIN <= x < MARGIN + GRID_SIZE and
            TOP_MARGIN <= y < TOP_MARGIN + GRID_SIZE):
            col = (x - MARGIN) // CELL_SIZE
            row = (y - TOP_MARGIN) // CELL_SIZE
            self.selected = (row, col)
            self.update_highlights()
            return

        # Check button click
        for rect, action in self.button_rects:
            if rect.collidepoint(pos):
                action()
                return
        
        self.selected = None
        self.update_highlights()

    def set_selection(self, pos):
        self.selected = (max(0, min(pos[0], 8)), max(0, min(pos[1], 8)))
        self.update_highlights()

    def move_selection(self, dir):
        if self.selected:
            self.set_selection( (self.selected[0] + dir[0], self.selected[1] + dir[1]) )

    def handle_key(self, key):
        if self.selected and not self.solved:
            row, col = self.selected
            if self.original_board[row][col] == 0:
                if pygame.K_1 <= key <= pygame.K_9:
                    self.user_board[row][col] = key - pygame.K_0
                    self.update_highlights()
                    if not any(0 in row for row in self.user_board):
                        self.check_solution()
                elif pygame.K_KP1 <= key <= pygame.K_KP9:
                    self.user_board[row][col] = key - pygame.K_KP0
                    self.update_highlights()
                    if not any(0 in row for row in self.user_board):
                        self.check_solution()
                elif key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
                    self.user_board[row][col] = 0
                    self.update_highlights()
            if key == pygame.K_ESCAPE:
                self.selected = None

        if key == pygame.K_RIGHT or key == pygame.K_d:
            self.move_selection((0, 1))
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.move_selection((0, -1))
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.move_selection((1, 0))
        elif key == pygame.K_UP or key == pygame.K_w:
            self.move_selection((-1, 0))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift_pressed = True
                        self.update_highlights()
                    else:
                        self.handle_key(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.shift_pressed = False
                        self.update_highlights()

            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_buttons()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = SudokuGUI()
    app.run()