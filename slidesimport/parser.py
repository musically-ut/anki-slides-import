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
    questionWithoutSlideLine = re.compile(r'^\s+Q:\s*(?P<line>.*)$')
    answerWithoutSlideLine = re.compile(r'^\s+A:\s*(?P<line>.*)$')

    def __init__(self, questionsBuffer):
        self.questionsBuffer = questionsBuffer
        slideQList = {}
        slideQWSList = {}
        slideAWSList = {}

        slideNum = None
        for idx, line in enumerate(self.questionsBuffer):
            lineNumber = idx + 1
            if len(line.strip()) == 0:
                continue

            if slideNum is not None:
                lineMatch = self.questionLine.match(line)
                questionWithoutSlideLineMatch = self.questionWithoutSlideLine.match(line)
                answerWithoutSlideLineMatch = self.answerWithoutSlideLine.match(line)
            else:
                lineMatch = None
                questionWithoutSlideLineMatch = None
                answerWithoutSlideLineMatch = None

            if lineMatch is not None:
                if slideNum not in slideQList:
                    slideQList[slideNum] = []
                    slideQWSList[slideNum] = []
                    slideAWSList[slideNum] = []

                slideQList[slideNum].append(lineMatch.group('line'))

                if questionWithoutSlideLineMatch is not None:
                    slideQWSList[slideNum].append(questionWithoutSlideLineMatch.group('line'))

                if answerWithoutSlideLineMatch is not None:
                    slideAWSList[slideNum].append(answerWithoutSlideLineMatch.group('line'))
            else:
                slideNumMatch = self.slideNumberLine.match(line)
                if slideNumMatch:
                    slideNum = int(slideNumMatch.group('slideNum'))
                else:
                    raise ParseException(lineNumber, line)

        self.slideQuestions = dict( (k, '\n'.join(v))
                                    for k, v in slideQList.items()
                                  )

        self.slideQuestionsWithoutSlides = dict( (k, '\n'.join(v))
                                                 for k, v in slideQWSList.items()
                                               )
        
        self.slideAnswersWithoutSlides = dict( (k, '\n'.join(v))
                                                 for k, v in slideAWSList.items()
                                               )


    def getQuestions(self):
        """Gets a dictionary of questions."""
        return self.slideQuestions
        # return self.slideQuestionsAndAnswers
    
    def getQAndAParsing(self):
        """Gets dictionaries of various question and answer parsings."""
        return self.slideQuestions, self.slideQuestionsWithoutSlides, self.slideAnswersWithoutSlides


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

singleSlideQ = u'''Slide 1:
    Q: Question
'''

singleSlideA = u'''Slide 1:
    A: Answer
'''

singleSlideQAndA = u'''Slide 1:
    Q: Question
    A: Answer
'''

multipleSlideQAndA = u'''Slide 1:
    Q: Question-1
    A: Answer-1
Slide 2:
    Q: Question-2
    A: Answer-2
'''

multiLineQAndA = u'''Slide 1:
    Q: Question-1
    Q: Question-2
    A: Answer-1
    A: Answer-2
'''

emptyLineQAndA = u'''Slide 1:

    Q: Question-1

    A: Answer-1

Slide 2:

    Q: Question-2

    A: Answer-2

'''

multipleSlideMentionsQAndA = u'''

Slide 1:
    Q: Question-a
    A: Answer-a

Slide 2:
    Q: Question-b
    A: Answer-b

Slide 1:
    Q: Question-c
    A: Answer-c
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
    
    def testSingleSlideQ(self):
        p = Parser(StringIO(singleSlideQ))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(qs[1], 'Q: Question')
        self.assertEqual(q[1], 'Question')
        self.assertEqual(a[1], '')
    
    def testSingleSlideA(self):
        p = Parser(StringIO(singleSlideA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(qs[1], 'A: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(a[1], 'Answer')

    def testSingleSlideQAndA(self):
        p = Parser(StringIO(singleSlideQAndA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(qs[1], 'Q: Question\nA: Answer')
        self.assertEqual(q[1], 'Question')
        self.assertEqual(a[1], 'Answer')

    def testMultipleSlideQAndA(self):
        p = Parser(StringIO(multipleSlideQAndA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(qs[1], 'Q: Question-1\nA: Answer-1')
        self.assertEqual(qs[2], 'Q: Question-2\nA: Answer-2')
        self.assertEqual(q[1], 'Question-1')
        self.assertEqual(a[1], 'Answer-1')
        self.assertEqual(q[2], 'Question-2')
        self.assertEqual(a[2], 'Answer-2')

    def testMultiLineeQAndA(self):
        p = Parser(StringIO(multiLineQAndA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(qs[1], 'Q: Question-1\nQ: Question-2\nA: Answer-1\nA: Answer-2')
        self.assertEqual(q[1], 'Question-1\nQuestion-2')
        self.assertEqual(a[1], 'Answer-1\nAnswer-2')
    
    def testEmptyLineQAndA(self):
        p = Parser(StringIO(emptyLineQAndA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(qs[1], 'Q: Question-1\nA: Answer-1')
        self.assertEqual(qs[2], 'Q: Question-2\nA: Answer-2')
        self.assertEqual(q[1], 'Question-1')
        self.assertEqual(a[1], 'Answer-1')
        self.assertEqual(q[2], 'Question-2')
        self.assertEqual(a[2], 'Answer-2')

    def testMultipleSlideMentionsQAndA(self):
        p = Parser(StringIO(multipleSlideMentionsQAndA))
        qs, q, a = p.getQAndAParsing()

        self.assertEqual(len(qs), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(qs[1], 'Q: Question-a\nA: Answer-a\nQ: Question-c\nA: Answer-c')
        self.assertEqual(qs[2], 'Q: Question-b\nA: Answer-b')
        self.assertEqual(q[1], 'Question-a\nQuestion-c')
        self.assertEqual(a[1], 'Answer-a\nAnswer-c')
        self.assertEqual(q[2], 'Question-b')
        self.assertEqual(a[2], 'Answer-b')
