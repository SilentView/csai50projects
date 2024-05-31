import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains.keys():
            to_del = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    to_del.add(word)
            self.domains[var] -= to_del

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        x_to_del = set()
        for x_word in self.domains[x]:
            if self.crossword.overlaps[x, y] is None:
                continue
            else:
                i, j = self.crossword.overlaps[x, y]
                has_satisfying_y = False
                for y_word in self.domains[y]:
                    if x_word[i] == y_word[j]:
                        has_satisfying_y = True
                        break
                if not has_satisfying_y:
                    x_to_del.add(x_word)
                    revised = True
        self.domains[x] -= x_to_del
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for x in self.domains.keys():
                for y in self.domains.keys():
                    if x != y:
                        arcs.append((x, y))
        # check every existing arc(e.g., x against y), if any x's domain modified,
        # should remember to check binary consistence of neighbor(y excluded) against x,
        # or this may be left out
        while len(arcs) > 0:
            x, y = arcs[0]
            arcs = arcs[1:]     # modify list like a queue, dequeue
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.domains)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if every value is distinct
        # 用set查重！
        if len(assignment) != len(set(assignment.values())):
            return False

        # check if the length is correct:
        for var in assignment:
            if var.length != len(assignment[var]):
                return False

        # check if there is any conflict
        for var in assignment:
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                i, j = self.crossword.overlaps[var, neighbor]
                if neighbor not in assignment:
                    continue
                elif assignment[var][i] != assignment[neighbor][j]:
                    return False

        return True

    def rule_out_count(self, var, value):
        """
        return the number of choices ruled out if
        var chooses "value" as its value
        """
        rule_out_num = 0
        for neighbor in self.crossword.neighbors(var):
            i, j = self.crossword.overlaps[var, neighbor]
            for neighbor_value in self.domains[neighbor]:
                if value[i] != neighbor_value[j]:
                    rule_out_num += 1
        return rule_out_num

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = list(self.domains[var])

        def rule_out_num(value):
            return self.rule_out_count(var, value)
        values = sorted(values, key=rule_out_num)
        return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        def select(var):
            """
            return the magnitude(int) of the var's domain
            plus a normalized factor representing its degree
            0 < this factor < 1
            """
            degree = len(self.crossword.neighbors(var))
            factor = 1 / (degree + 1)
            return len(self.domains[var]) + factor
        unassigned_var = list(set(self.domains.keys()) - assignment.keys())
        unassigned_var = sorted(unassigned_var, key=select)
        return unassigned_var[0]

    def revise_trial(self, x, y, domains):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # 该函数只修改传进来的domains，因为inference中对domains的修改应当是可逆的
        revised = False
        x_to_del = set()
        for x_word in self.domains[x]:
            if self.crossword.overlaps[x, y] is None:
                continue
            else:
                i, j = self.crossword.overlaps[x, y]
                has_satisfying_y = False
                for y_word in self.domains[y]:
                    if x_word[i] == y_word[j]:
                        has_satisfying_y = True
                        break
                if not has_satisfying_y:
                    x_to_del.add(x_word)
                    revised = True
        domains[x] -= x_to_del
        return revised

    def inference(self, assignment, var):
        """
        return a dict recording the inferences about the assignment
        note that the before adding {var = value} to assignment, arc consistency
        is met, so the arc_que can first enqueue var's neighbors against var
        """
        m_assignment = copy.deepcopy(assignment)
        m_domains = copy.deepcopy(self.domains)
        arc_queue = []
        inferred_dict = {}
        for neighbor in self.crossword.neighbors(var):
            arc_queue.append((neighbor, var))
        # check every existing arc(e.g., x against y), if any x's domain modified,
        # should remember to check arc consistency of neighbor(y excluded) against x,
        # or this may be left out
        while len(arc_queue) > 0:
            x, y = arc_queue[0]
            arc_queue = arc_queue[1:]     # modify list like a queue, dequeue
            if self.revise_trial(x, y, m_domains):
                if len(self.domains[x]) == 0:
                    raise Exception("by inference, not a feasible assignment")
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arc_queue.append((neighbor, x))
        for variable in self.domains:
            if len(self.domains[variable]) == 1 and variable not in assignment:
                inferred_dict[variable] = self.domains[variable].pop()
        return inferred_dict

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if not self.consistent(assignment):
                del assignment[var]
                continue
            try:
                # consistence will be checked during inference()
                inference_dict = self.inference(assignment, var)
            except Exception:
                del assignment[var]
                continue
            else:
                assignment.update(inference_dict)
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                # if result is None, trace back to former assignment
                for variable in set(inference_dict.keys()) | {var}:
                    del assignment[variable]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
