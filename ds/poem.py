import regex as re


class Poem(dict):
    def get_rhymes(self, lines=None, split=False):
        # this needs improvement: not every character will be a rhyme
        patt = r'，。\]'
        end = '' if split else '$'

        return [last_char
                for line in (lines or self['paragraphs'])
                # add $ to force end of line
                for last_char in re.findall(f'([^{patt}])[{patt}]+{end}', line)
                ]
