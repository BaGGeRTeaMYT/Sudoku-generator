import random
import copy

class SudokuGenerator:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None

    def generate_base_board(self):
        """Generate a base valid Sudoku board using a simple pattern"""
        # A simple way to generate a valid base board is to shift rows
        # Row 0: 1 2 3 4 5 6 7 8 9
        # Row 1: 4 5 6 7 8 9 1 2 3 (shifted by 3)
        # Row 2: 7 8 9 1 2 3 4 5 6 (shifted by 3)
        # Row 3: 2 3 4 5 6 7 8 9 1 (shifted by 1 relative to row 0, or just follow pattern)
        
        # Pattern: shift by 3 for each row in a block, shift by 1 for each block
        # Indices:
        # 0 1 2 3 4 5 6 7 8
        # 3 4 5 6 7 8 0 1 2
        # 6 7 8 0 1 2 3 4 5
        # 1 2 3 4 5 6 7 8 9
        # ...
        
        base_row = list(range(1, 10))
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        
        for i in range(9):
            # Calculate shift
            # i=0 -> 0
            # i=1 -> 3
            # i=2 -> 6
            # i=3 -> 1
            # i=4 -> 4
            # i=5 -> 7
            # i=6 -> 2
            # i=7 -> 5
            # i=8 -> 8
            shift = (i % 3) * 3 + (i // 3)
            for j in range(9):
                self.board[i][j] = base_row[(j + shift) % 9]
        
        self.solution = copy.deepcopy(self.board)

    def transpose(self):
        """Transpose the board"""
        self.board = list(map(list, zip(*self.board)))

    def swap_rows_small(self):
        """Swap two rows within the same 3x9 block"""
        block = random.randint(0, 2)
        row1 = block * 3 + random.randint(0, 2)
        row2 = block * 3 + random.randint(0, 2)
        while row1 == row2:
            row2 = block * 3 + random.randint(0, 2)
        self.board[row1], self.board[row2] = self.board[row2], self.board[row1]

    def swap_cols_small(self):
        """Swap two columns within the same 3x9 block"""
        self.transpose()
        self.swap_rows_small()
        self.transpose()

    def swap_rows_area(self):
        """Swap two 3x9 blocks of rows"""
        area1 = random.randint(0, 2)
        area2 = random.randint(0, 2)
        while area1 == area2:
            area2 = random.randint(0, 2)
        
        for i in range(3):
            r1 = area1 * 3 + i
            r2 = area2 * 3 + i
            self.board[r1], self.board[r2] = self.board[r2], self.board[r1]

    def swap_cols_area(self):
        """Swap two 3x9 blocks of columns"""
        self.transpose()
        self.swap_rows_area()
        self.transpose()

    def shuffle_board(self, steps=20):
        """Apply random transformations to the board"""
        transformations = [
            self.transpose,
            self.swap_rows_small,
            self.swap_cols_small,
            self.swap_rows_area,
            self.swap_cols_area
        ]
        
        for _ in range(steps):
            func = random.choice(transformations)
            func()
            
        self.solution = copy.deepcopy(self.board)

    def solve_count(self, board, count=0):
        """
        Count solutions for the board. 
        Returns number of solutions found (stops if > 1).
        """
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, i, j, num):
                            board[i][j] = num
                            count = self.solve_count(board, count)
                            if count > 1:
                                return count
                            board[i][j] = 0
                    return count
        return count + 1

    def is_valid(self, board, row, col, num):
        """Check if placing num at board[row][col] is valid"""
        # Check row
        for j in range(9):
            if board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Check 3x3 box
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False
        
        return True

    def remove_numbers_unique(self, attempts=5):
        """
        Remove numbers while maintaining a unique solution.
        attempts: Not strictly used as a limit in the described algorithm, 
                  but useful if we want to limit how many cells we try to remove.
                  Here we implement the algorithm: try to remove ALL cells in random order.
        """
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for row, col in positions:
            backup = self.board[row][col]
            if backup == 0:
                continue
                
            self.board[row][col] = 0
            
            # Check if unique solution exists
            # We need to pass a copy because solve_count modifies the board
            board_copy = copy.deepcopy(self.board)
            solutions = self.solve_count(board_copy)
            
            if solutions != 1:
                self.board[row][col] = backup
                # If we found > 1 solution, we put it back and remove from list of available cells
                # (The loop naturally moves to the next position, effectively removing this one from consideration)

    def generate_puzzle(self):
        """Generate a Sudoku puzzle with unique solution"""
        # 1. Create base board
        self.generate_base_board()
        
        # 2. Shuffle board
        self.shuffle_board()
        
        # 3. Remove numbers
        self.remove_numbers_unique()
        
        return self.board

    def print_board(self, board):
        """Print the Sudoku board in a readable format"""
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("- - - - - - - - - - - -")
            
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print(" | ", end="")
                
                val = board[i][j]
                display = "." if val == 0 else str(val)
                
                if j == 8:
                    print(display)
                else:
                    print(display + " ", end="")

def main():
    generator = SudokuGenerator()
    puzzle = generator.generate_puzzle()
    
    print("Generated Sudoku Puzzle with Unique Solution:")
    generator.print_board(puzzle)

if __name__ == "__main__":
    main()
