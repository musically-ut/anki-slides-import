import unittest
import re
from io import StringIO

class ParseException(BaseException):
    def __init__(self, lineNumber, line):
        self.line = line
        self.lineNumber = lineNumber

        message = 'Parsing Error in line {0}:\n>>> {1}'.format(self.lineNumber, self.line)
        super(ParseException, self).__init__(message)


class Parser:
    slideNumberLine = re.compile(r'^(#.*)?Slide (?P<slideNum>\d+):')
    questionLine = re.compile(r'^\s+(?P<line>.*)$')

    def __init__(self, questionsBuffer):
        self.questionsBuffer = questionsBuffer
        slideQList = {}

        slideNum = None
        for idx, line in enumerate(self.questionsBuffer):
            lineNumber = idx + 1
            if len(line.strip()) == 0:
                continue

            if slideNum is not None:
                lineMatch = self.questionLine.match(line)
            else:
                lineMatch = None

            if lineMatch is not None:
                if slideNum not in slideQList:
                    slideQList[slideNum] = []

                slideQList[slideNum].append(lineMatch.group('line'))
            else:
                slideNumMatch = self.slideNumberLine.match(line)
                if slideNumMatch:
                    slideNum = int(slideNumMatch.group('slideNum'))
                else:
                    raise ParseException(lineNumber, line)

        self.slideQuestions = dict( (k, '\n'.join(v))
                                    for k, v in slideQList.items()
                                  )

    def getQuestions(self):
        """Gets a dictionary of questions."""
        return self.slideQuestions


singleSlide = u'''Slide 1:
    Question
'''

multipleSlides = u'''Slide 1:
        Question1
Slide 200:
    Question2
'''

emptySlide = u'''Slide 1:
Slide 2:
    Question
'''

multilineQuestion = u'''Slide 1:
    - Q1
    - Q2
'''

emptyLineQuestions = u'''

Slide 1:
    Question-1


Slide 2:
    Question-2

'''

multipleSlideMentions = u'''

Slide 1:
    Question-a

Slide 2:
    Question-b

Slide 1:
    Question-c
'''


class TestParser(unittest.TestCase):
    def testSingleSlide(self):
        p = Parser(StringIO(singleSlide))
        qs = p.getQuestions()

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[1], 'Question')

    def testMultipleSlides(self):
        p = Parser(StringIO(multipleSlides))
        qs = p.getQuestions()

        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[1], 'Question1')
        self.assertEqual(qs[200], 'Question2')

    def testEmptySlide(self):
        qs = Parser(StringIO(emptySlide)).getQuestions()

        # Empty slides are not recorded
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[2], 'Question')

    def testMultilineQuestion(self):
        qs = Parser(StringIO(multilineQuestion)).getQuestions()

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[1], '- Q1\n- Q2')

    def testEmptyLines(self):
        qs = Parser(StringIO(emptyLineQuestions)).getQuestions()

        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[1], 'Question-1')
        self.assertEqual(qs[2], 'Question-2')

    def testMultipleSlideMentions(self):
        qs = Parser(StringIO(multipleSlideMentions)).getQuestions()

        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[1], 'Question-a\nQuestion-c')
        self.assertEqual(qs[2], 'Question-b')
