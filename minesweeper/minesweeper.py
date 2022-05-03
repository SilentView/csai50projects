import itertools
import random

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # do not modify a set while iterating over it
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        else:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbors(self, cell):
        """
        return a set of all the neighbor cells of a certain cell
        """
        neighbors = set()
        for i in range(3):
            for j in range(3):
                m = cell[0] - 1 + i
                n = cell[1] - 1 + j
                if 0 <= m <= self.height-1 and 0 <= n <= self.width-1:
                    neighbors.add((m, n))
        return neighbors

    def conclude(self):
        """
        check if any sentence itself can lead to a certain result,
        if so, mark accordingly. return the number of these sentences
        this function only loops once.
        """
        conclusion_cnt = 0
        mines = set()
        safes = set()
        # 不能在循环过程中就去mark，因为下面这个，因为mark会改动safes指向的内存
        """
        for safe in safes:
            self.mark_safe(safe)
        """
        # 经典的Set changed size during iteration
        # self.mark_mine()会改变knowledge的cells，而safes、mines
        # 实质上都是cells的引用
        for knowledge in self.knowledge:
            mines |= knowledge.known_mines()
            safes |= knowledge.known_safes()
        if len(mines) != 0:
            conclusion_cnt += len(mines)
            for mine in mines:
                self.mark_mine(mine)
        if len(safes) != 0:
            conclusion_cnt += len(safes)
            for safe in safes:
                self.mark_safe(safe)
        return conclusion_cnt


    def infer(self):
        """
        enumerate any double combination of sentences, if one < another,
        add a new sentence cells1 - cells2 = count1 - count2
        return the number of this kind of combinations
        only enumerate once
        """
        inference_cnt = 0
        new_knowledge = []
        for i in range(len(self.knowledge)):
            for j in range(i+1, len(self.knowledge)):
                if self.knowledge[i].cells < self.knowledge[j].cells:
                    new_sentence = Sentence(self.knowledge[j].cells - self.knowledge[i].cells,
                                            self.knowledge[j].count - self.knowledge[i].count)
                    is_redundant = False
                    for sentence in self.knowledge:
                        if sentence == new_sentence:
                            is_redundant = True
                            break
                    if is_redundant:
                        continue

                    inference_cnt += 1
                    new_knowledge.append(new_sentence)
                elif self.knowledge[j].cells < self.knowledge[i].cells:
                    new_sentence = Sentence(self.knowledge[i].cells - self.knowledge[j].cells,
                                            self.knowledge[i].count - self.knowledge[j].count)
                    is_redundant = False
                    for sentence in self.knowledge:
                        if sentence == new_sentence:
                            is_redundant = True
                            break
                    if is_redundant:
                        continue

                    inference_cnt += 1
                    new_knowledge.append(new_sentence)
        self.knowledge += new_knowledge
        return inference_cnt

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the cell as a move that has been made
        self.moves_made.add(cell)
        # mark the cell as safe
        self.mark_safe(cell)
        # add basic new sentence
        self.knowledge.append(Sentence(self.get_neighbors(cell), count))
        # we will loop to call conclude() and infer(), until we can't get anything new.
        # this is because everytime we modify or add some sentences, new possible changes may be made to other sentences
        while True:
            new_change_cnt = 0
            new_change_cnt += self.conclude()
            new_change_cnt += self.infer()
            if new_change_cnt == 0:
                break


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_cells = self.safes - self.moves_made
        try:
            return safe_cells.pop()
        except KeyError:
            return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        board = set()
        for i in range(self.height):
            for j in range(self.width):
                board.add((i, j))
        possible_moves = board - self.moves_made - self.mines
        try:
            return possible_moves.pop()
        except KeyError:
            return None
