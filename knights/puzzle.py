from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
statement0 = And(AKnight, AKnave)
knowledge0 = And(
    Or(And(AKnight, statement0), And(AKnave, Not(statement0))),
    # 表示A不可能同时是Knight和Knave
    Biconditional(AKnave, Not(AKnight))
    #Implication(AKnave, Not(AKnight)),
    #Implication(AKnight, Not(AKnave))
    # TODO
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
statement1 = And(AKnave, BKnave)
knowledge1 = And(
    # 更简介的表述：Biconditional(AKnave, Not(statement1))
    Or(And(AKnight, statement1), And(AKnave, Not(statement1))),
    Biconditional(AKnave, Not(AKnight)),
    Biconditional(BKnave, Not(BKnight))
    # TODO
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."

# 更简洁的表述：Biconditional(AKnave, BKnave)
statement2A = Or(And(AKnight, BKnight), And(AKnave, BKnave))
statement2B = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    Or(And(AKnight, statement2A), And(AKnave, Not(statement2A))),
    Or(And(BKnight, statement2B), And(BKnave, Not(statement2B))),
    Biconditional(AKnave, Not(AKnight)),
    Biconditional(BKnave, Not(BKnight))
    # TODO
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
statement3A = Or(AKnave, AKnight)
statement3B1 = Biconditional(statement3A, AKnave)
statement3B2 = CKnave
statement3C = AKnight
knowledge3 = And(
    Biconditional(AKnave, Not(AKnight)),
    Biconditional(BKnave, Not(BKnight)),
    Biconditional(CKnave, Not(CKnight)),

    Biconditional(AKnave, Not(statement3A)),
    Biconditional(BKnave, Not(statement3B1)),
    Biconditional(BKnave, Not(statement3B2)),
    Biconditional(CKnave, Not(statement3C)),
    # TODO
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
