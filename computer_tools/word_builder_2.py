from pathlib import Path


PIXEL_DATA_PATH = Path.cwd() / 'pixels_data'


class Letter:
    def __init__(self, letter):
        self.letter = letter
        self.pixel_columns = []
        self._load_letter()

    def _load_letter(self):
        with open(PIXEL_DATA_PATH / f'{self.letter}.pixels') as file:
            for line in file:
                line = line.replace('\n', '')
                self.pixel_columns.append(line)


class Word:
    def __init__(self, word):
        self.word = word
        self.letters = []
        self._load_letters()
        self.pixel_word = None

    def _load_letters(self):
        for letter in self.word:
            self.letters.append(Letter(letter))

    def _last_col_is_empty(self, letter):
        for col in letter:
            if col.split(';')[-2] != "[0, 0, 0]":
                return False
        return True

    def _append_letter(self, letter):
        for i in range(len(self.pixel_word)):
            if not self._last_col_is_empty(letter):
                self.pixel_word[i] = self.pixel_word[i] + '[0, 0, 0];'
            self.pixel_word[i] = self.pixel_word[i] + letter[i]

        # for i in range(len(self.pixel_word)):
        #     self.pixel_word

    def _merge_all_letters(self):
        self.letters.reverse()
        self.pixel_word = self.letters.pop().pixel_columns
        while self.letters:
            self._append_letter(self.letters.pop().pixel_columns)
        # for letter in self.letters:
        #     print('LETTER', letter)
        #     self._append_letter(letter)

    def store_word(self):
        self._merge_all_letters()
        with open(PIXEL_DATA_PATH / f'{self.word}.pixels', 'w') as file:
            for row in self.pixel_word:
                file.write(row + '\n')


def main ():
    user_input = input('Please type in a word: ')
    word = Word(user_input)
    word.store_word()
 

if __name__ == '__main__':
    main()