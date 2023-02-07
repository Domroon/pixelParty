from pathlib import Path

PIXEL_DATA_PATH = Path.cwd() / 'pixels_data'

EMPTY_PIXEL = "[0, 0, 0];"


def load_pixels_letters(word):
    pixels_strings = []
    for letter in word:
        with open(PIXEL_DATA_PATH / f'{letter}.pixels') as file:
            letter = []
            for line in file:
                line = line.replace('\n', '')
                letter.append(line)
            pixels_strings.append(letter)

    return pixels_strings


def last_column_is_empty(letter_strings):
    is_empty = True
    for line in letter_strings:
        row_pixels = line.split(';')
        if row_pixels[-2] != '[0, 0, 0]':
            is_empty = False
    return is_empty


def append_letter(word, letter):
    last_letter = word[-1]

    # add next letter to last letter
    for i in range(len(last_letter)):
        last_letter[i] = last_letter[i] + letter[i]

def append_empty_column(word):
    last_letter = word[-1]

    # add empt column to last letter
    for i in range(len(last_letter)):
        last_letter[i] = last_letter[i] + '[0, 0, 0]'


def merge_pixels_strings(pixels_letters):
    # lade ersten buchstaben in eine liste (new_pixels)
    pixels_letters.reverse()
    word = pixels_letters.pop()

    # füge an jede zeile des buchstabens (liste-new_pixels) ein leeren pixel an,
    # wenn die letzte spalte nicht leer ist
    for letter in pixels_letters:
        if last_column_is_empty(letter):
            print('Last column is empty')
            # append every row from the next letter to every row from the current letter
            append_letter(word, pixels_letters.pop())
        else:
            print('Last column is NOT empty')
            # append a empty pixel to every row of the current letter
            append_empty_column(word)
            # then append every row from the next letter to every row from the current letter
            append_letter(word, pixels_letters.pop())
    print('WORD')
    for letter in word:
        print('letter', letter)

    # füge dann jede zeile des nächsten buchstabens an jede zeile der liste (new_pixels) an

    # füge an jede zeile des buchstabens (liste-new_pixels) ein leeren pixel an 
    # füge dann jede zeile des nächsten buchstabens an jede zeile der liste (new_pixels) an

    # gib die new_pixels liste zurück


def main():
    word = input('Please enter a word: ')
    pixels_letters = load_pixels_letters(word)
    print(pixels_letters)

    merge_pixels_strings(pixels_letters)

    # make a new file with the word name.pixels and store it in the folder pixels_data


if __name__ == '__main__':
    main()