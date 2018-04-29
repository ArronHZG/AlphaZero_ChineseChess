# from code.environment.chessman import Pawn, Cannon, Rook, Knight, Elephant, Mandarin, King
from enum import Enum, auto
import numpy as np

Fen_2_Idx = {
    'p': 0,
    'P': 0,
    'c': 1,
    'C': 1,
    'r': 2,
    'R': 2,
    'k': 3,
    'K': 3,
    'e': 4,
    'E': 4,
    'm': 5,
    'M': 5,
    's': 6,
    'S': 6
}


class Color(Enum):
    Black = auto()
    Red = auto()


class Winner(Enum):
    red = auto()
    black = auto()
    draw = auto()


def flip_move(x):
    new = ''
    new = ''.join([new, str(8 - int(x[0]))])
    new = ''.join([new, str(9 - int(x[1]))])
    new = ''.join([new, str(8 - int(x[2]))])
    new = ''.join([new, str(9 - int(x[3]))])
    return new


def flip_action_labels(labels):
    return [flip_move(x) for x in labels]


def create_action_labels():
    labels_array = []  # [col_src,row_src,col_dst,row_dst]
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  # row
    letters = ['0', '1', '2', '3', '4', '5', '6', '7', '8']  # col

    for n1 in range(10):
        for l1 in range(9):
            destinations = [(n1, t) for t in range(9)] + \
                           [(t, l1) for t in range(10)] + \
                           [(n1 + a, l1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]
            for (n2, l2) in destinations:
                if (n1, l1) != (n2, l2) and n2 in range(10) and l2 in range(9):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)

    # for red mandarin
    labels_array.append('3041')
    labels_array.append('5041')
    labels_array.append('3241')
    labels_array.append('5241')
    labels_array.append('4130')
    labels_array.append('4150')
    labels_array.append('4132')
    labels_array.append('4152')
    # for black mandarin
    labels_array.append('3948')
    labels_array.append('5948')
    labels_array.append('3748')
    labels_array.append('5748')
    labels_array.append('4839')
    labels_array.append('4859')
    labels_array.append('4837')
    labels_array.append('4857')

    # for red elephant
    labels_array.append('2002')
    labels_array.append('2042')
    labels_array.append('6042')
    labels_array.append('6082')
    labels_array.append('2402')
    labels_array.append('2442')
    labels_array.append('6442')
    labels_array.append('6482')
    labels_array.append('0220')
    labels_array.append('4220')
    labels_array.append('4260')
    labels_array.append('8260')
    labels_array.append('0224')
    labels_array.append('4224')
    labels_array.append('4264')
    labels_array.append('8264')
    # for black elephant
    labels_array.append('2907')
    labels_array.append('2947')
    labels_array.append('6947')
    labels_array.append('6987')
    labels_array.append('2507')
    labels_array.append('2547')
    labels_array.append('6547')
    labels_array.append('6587')
    labels_array.append('0729')
    labels_array.append('4729')
    labels_array.append('4769')
    labels_array.append('8769')
    labels_array.append('0725')
    labels_array.append('4725')
    labels_array.append('4765')
    labels_array.append('8765')

    return labels_array


ActionLabelsRed = create_action_labels()
ActionLabelsBlack = flip_action_labels(ActionLabelsRed)

unflipped_index = [ActionLabelsRed.index(x) for x in ActionLabelsBlack]


def flip_policy(pol):
    global unflipped_index
    return np.asarray([pol[ind] for ind in unflipped_index])


if __name__ == '__main__':
    print(ActionLabelsRed.__len__())
