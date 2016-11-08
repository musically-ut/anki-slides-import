import unittest
import re
from io import StringIO
from collections import namedtuple
import cgi

NotesParsing = namedtuple('NotesParsing',
                          ['fullNotes',
                           'questionsWithoutSlides',
                           'questionsFollowedBySlides',
                           'slidesFollowedByQuestions',
                           'answersWithoutSlides',
                           'answersFollowedBySlides',
                           'slidesFollowedByAnswers'])

NotesAndCropsParsing = namedtuple('NotesParsing',
                                  ['fullNotes',
                                   'questionsWithoutSlides',
                                   'questionsFollowedBySlides',
                                   'questionsFollowedBySlidesCrops',
                                   'slidesFollowedByQuestions',
                                   'slidesFollowedByQuestionsCrops',
                                   'answersWithoutSlides',
                                   'answersFollowedBySlides',
                                   'answersFollowedBySlidesCrops',
                                   'slidesFollowedByAnswers',
                                   'slidesFollowedByAnswersCrops'])

class ParseException(BaseException):
    def __init__(self, lineNumber, line):
        self.line = line
        self.lineNumber = lineNumber

        message = 'Parsing Error in line {0}:\n>>> {1}'.format(self.lineNumber, self.line)
        super(ParseException, self).__init__(message)


class Parser:
    slideNumberLine = re.compile(r'^(#.*)?Slide (?P<slideNum>\d+):')
    fullNotes = re.compile(r'^\s+(?P<line>.*)$')
    questionWithoutSlideLine = re.compile(r'^\s+Q:\s*(?P<line>.*)$')
    questionFollowedBySlideLine = re.compile(r'^\s+Q_S\s*(?:\[(?P<crop>.*?)\].*?)?\s*:\s*(?P<line>.*)$')
    slideFollowedByQuestionLine = re.compile(r'^\s+S_Q\s*(?:\[(?P<crop>.*?)\].*?)?\s*:\s*(?P<line>.*)$')
    answerWithoutSlideLine = re.compile(r'^\s+A:\s*(?P<line>.*)$')
    answerFollowedBySlideLine = re.compile(r'^\s+A_S\s*(?:\[(?P<crop>.*?)\].*?)?\s*:\s*(?P<line>.*)$')
    slideFollowedByAnswerLine = re.compile(r'^\s+S_A\s*(?:\[(?P<crop>.*?)\].*?)?\s*:\s*(?P<line>.*)$')

    def __init__(self, questionsBuffer):
        self.questionsBuffer = questionsBuffer
        slideQList = {}
        slideQWSList = {}
        slideQFBSList = {}
        slideQFBSCropList = {}
        slideSFBQList = {}
        slideSFBQCropList = {}
        slideAWSList = {}
        slideAFBSList = {}
        slideAFBSCropList = {}
        slideSFBAList = {}
        slideSFBACropList = {}

        slideNum = None
        for idx, line in enumerate(self.questionsBuffer):
            lineNumber = idx + 1
            if len(line.strip()) == 0:
                continue

            if slideNum is not None:
                lineMatch = self.fullNotes.match(line)
                questionWithoutSlideLineMatch = self.questionWithoutSlideLine.match(line)
                questionFollowedBySlideLineMatch = self.questionFollowedBySlideLine.match(line)
                slideFollowedByQuestionLineMatch = self.slideFollowedByQuestionLine.match(line)
                answerWithoutSlideLineMatch = self.answerWithoutSlideLine.match(line)
                answerFollowedBySlideLineMatch = self.answerFollowedBySlideLine.match(line)
                slideFollowedByAnswerLineMatch = self.slideFollowedByAnswerLine.match(line)
            else:
                lineMatch = None
                questionWithoutSlideLineMatch = None
                questionFollowedBySlideLineMatch = None
                slideFollowedByQuestionLineMatch = None
                answerWithoutSlideLineMatch = None
                answerFollowedBySlideLineMatch = None
                slideFollowedByAnswerLineMatch = None

            if lineMatch is not None:
                if slideNum not in slideQList:
                    slideQList[slideNum] = []
                    slideQWSList[slideNum] = []
                    slideQFBSList[slideNum] = []
                    slideQFBSCropList[slideNum] = []
                    slideSFBQList[slideNum] = []
                    slideSFBQCropList[slideNum] = []
                    slideAWSList[slideNum] = []
                    slideAFBSList[slideNum] = []
                    slideAFBSCropList[slideNum] = []
                    slideSFBAList[slideNum] = []
                    slideSFBACropList[slideNum] = []

                slideQList[slideNum].append(cgi.escape(lineMatch.group('line')))

                questionFollowedBySlideCropParsing = []
                slideFollowedByQuestionCropParsing = []
                answerFollowedBySlideCropParsing = []
                slideFollowedByAnswerCropParsing = []

                if questionWithoutSlideLineMatch is not None:
                    slideQWSList[slideNum].append(cgi.escape(questionWithoutSlideLineMatch.group('line')))

                if questionFollowedBySlideLineMatch is not None:
                    slideQFBSList[slideNum].append(cgi.escape(questionFollowedBySlideLineMatch.group('line')))

                    questionFollowedBySlideCropString = questionFollowedBySlideLineMatch.group('crop')
                    if questionFollowedBySlideCropString is not None:
                        questionFollowedBySlideCropParsing = self.parseCrop(questionFollowedBySlideCropString)

                if slideFollowedByQuestionLineMatch is not None:
                    slideSFBQList[slideNum].append(cgi.escape(slideFollowedByQuestionLineMatch.group('line')))

                    slideFollowedByQuestionCropString = slideFollowedByQuestionLineMatch.group('crop')
                    if slideFollowedByQuestionCropString is not None:
                        slideFollowedByQuestionCropParsing = self.parseCrop(slideFollowedByQuestionCropString)

                if answerWithoutSlideLineMatch is not None:
                    slideAWSList[slideNum].append(cgi.escape(answerWithoutSlideLineMatch.group('line')))

                if answerFollowedBySlideLineMatch is not None:
                    slideAFBSList[slideNum].append(cgi.escape(answerFollowedBySlideLineMatch.group('line')))

                    answerFollowedBySlideCropString = answerFollowedBySlideLineMatch.group('crop')
                    if answerFollowedBySlideCropString is not None:
                        answerFollowedBySlideCropParsing = self.parseCrop(answerFollowedBySlideCropString)

                if slideFollowedByAnswerLineMatch is not None:
                    slideSFBAList[slideNum].append(cgi.escape(slideFollowedByAnswerLineMatch.group('line')))

                    slideFollowedByAnswerCropString = slideFollowedByAnswerLineMatch.group('crop')
                    if slideFollowedByAnswerCropString is not None:
                        slideFollowedByAnswerCropParsing = self.parseCrop(slideFollowedByAnswerCropString)

                # For now, just to get this working, unlike with the notes/questions/answers lists,
                # we are not appending to the crop values list for the slide,
                # but just assigning it to whatever the last input crop values were.
                # It might be best to do things this way anyway, because in the current incarnation
                # of system, we're only able to use one slide, so having multiple
                # crop values is pointless.
                if slideQFBSCropList[slideNum] == []:
                    slideQFBSCropList[slideNum] = questionFollowedBySlideCropParsing
                if slideSFBQCropList[slideNum] == []:
                    slideSFBQCropList[slideNum] = slideFollowedByQuestionCropParsing
                if slideAFBSCropList[slideNum] == []:
                    slideAFBSCropList[slideNum] = answerFollowedBySlideCropParsing
                if slideSFBACropList[slideNum] == []:
                    slideSFBACropList[slideNum] = slideFollowedByAnswerCropParsing

            else:
                slideNumMatch = self.slideNumberLine.match(line)
                if slideNumMatch:
                    slideNum = int(slideNumMatch.group('slideNum'))
                else:
                    raise ParseException(lineNumber, line)

        self.fullNotes = self.dictOfListsToDict(slideQList)
        self.slideQuestionsWithoutSlides = self.dictOfListsToDict(slideQWSList)
        self.slideQuestionsFollowedBySlides = self.dictOfListsToDict(slideQFBSList)
        self.slideQuestionsFollowedBySlidesCrops = dict(slideQFBSCropList)
        self.slideSlidesFollowedByQuestions = self.dictOfListsToDict(slideSFBQList)
        self.slideSlidesFollowedByQuestionsCrops = dict(slideSFBQCropList)
        self.slideAnswersWithoutSlides = self.dictOfListsToDict(slideAWSList)
        self.slideAnswersFollowedBySlides = self.dictOfListsToDict(slideAFBSList)
        self.slideAnswersFollowedBySlidesCrops = dict(slideAFBSCropList)
        self.slideSlidesFollowedByAnswers = self.dictOfListsToDict(slideSFBAList)
        self.slideSlidesFollowedByAnswersCrops = dict(slideSFBACropList)

    def dictOfListsToDict(self, x):
        """Converts a dict of lists of strings to a dict of strings separated by HTML line breaks."""
        return {k: '<br><br>'.join(v) for k, v in x.items()}

    def parseCrop(self, cropString):
        """Parses a slide crop string to a list of crop percentage numbers formatted as [[wmin, wmax], [hmin, hmax]]."""

        cropStringNumParser = re.compile(r'^\s*(?P<wmin>\d.*)[-|:](?P<wmax>\d.*),\s*(?P<hmin>\d.*)[-|:](?P<hmax>\d.*)\s*')
        cropStringNumParsing = cropStringNumParser.match(cropString)
        cropStringAlphaParser = re.compile(r'^\s*(?P<code>[a-zA-Z].*)\s*')
        cropStringAlphaParsing = cropStringAlphaParser.match(cropString)

        # First check if we're dealing with numerical values
        if cropStringNumParsing is None:
            # If not, check if we're dealing with alphabetic codes, e.g. 'tl' for 'top-left', etc.
            if cropStringAlphaParsing is None:
                # If we can't parse the string, return crop percentage values that encapsulate the entire slide image.
                cropNumList = [[0,100], [0,100]]
            else:
                code = cropStringAlphaParsing.group('code').lower()

                # 'All' of the slide, or the 'whole' of the slide
                if code == 'a' or code == 'w':
                    cropNumList = [[0, 100], [0, 100]]
                # 'Top' or 'top half' of the slide
                elif code == 't' or code == 'th':
                    cropNumList = [[0, 100], [0, 50]]
                # 'vertical middle half' of the slide
                elif code == 'vmh':
                    cropNumList = [[0, 100], [25, 75]]
                # 'Bottom' or 'bottom half' of the slide
                elif code == 'b' or code == 'bh':
                    cropNumList = [[0, 100], [50, 100]]
                # 'Left' or 'left half' of the slide
                elif code == 'l' or code == 'lh':
                    cropNumList = [[0, 50], [0, 100]]
                # 'middle half' or 'horizontal middle half' of the slide
                elif code == 'mh' or code == 'hmh':
                    cropNumList = [[25, 75], [0, 100]]
                # 'Right' or 'right half' of the slide
                elif code == 'r' or code == 'rh':
                    cropNumList = [[50, 100], [0, 100]]
                # 'middle' or 'centre' or 'middle quarter' or 'centre quarter' of the slide
                elif code == 'm' or code == 'c' or code == 'mq' or code == 'cq':
                    cropNumList = [[25, 75], [25, 75]]
                # 'Top-left' or 'top-left quarter' of the slide
                elif code == 'tl' or code == 'tlq':
                    cropNumList = [[0, 50], [0, 50]]
                # 'Top-right' or 'top-right quarter' of the slide
                elif code == 'tr' or code == 'trq':
                    cropNumList = [[50, 100], [0, 50]]
                # 'Bottom-left' or 'bottom-left quarter' of the slide
                elif code == 'bl' or code == 'blq':
                    cropNumList = [[0, 50], [50, 100]]
                # 'Bottom-right' or 'bottom-right quarter' of the slide
                elif code == 'br' or code == 'brq':
                    cropNumList = [[50, 100], [50, 100]]
                # 'Top third' of the slide
                elif code == 'tt':
                    cropNumList = [[0, 100], [0, 33]]
                # 'Vertical middle third' of the slide
                elif code == 'vmt':
                    cropNumList = [[0, 100], [33, 66]]
                # 'Bottom third' of the slide
                elif code == 'bt':
                    cropNumList = [[0, 100], [66, 100]]
                # 'Left third' of the slide
                elif code == 'lt':
                    cropNumList = [[0, 33], [0, 100]]
                # 'middle third' or 'horizontal middle third' of the slide
                elif code == 'mt' or code == 'hmt':
                    cropNumList = [[33, 66], [0, 100]]
                # 'right third' of the slide
                elif code == 'rt':
                    cropNumList = [[66, 100], [0, 100]]
                # Fall back to default values
                else:
                    cropNumList = [[0,100], [0,100]]

        else:
            wmin = int(cropStringNumParsing.group('wmin'))
            wmax = int(cropStringNumParsing.group('wmax'))
            hmin = int(cropStringNumParsing.group('hmin'))
            hmax = int(cropStringNumParsing.group('hmax'))

            # Some error checking
            if wmax <= wmin:
                wmin = 0
                wmax = 100
            if hmax <= hmin:
                hmin = 0
                hmax = 100

            cropNumList = [[wmin, wmax], [hmin, hmax]]

        return cropNumList

    def getQuestions(self):
        """Gets a dictionary of questions. (left here for backwards compatibility)"""
        return self.fullNotes

    def getNotesParsing(self):
        """Gets dictionaries of various question and answer parsings."""

        notesParsing = NotesParsing(self.fullNotes,
                                    self.slideQuestionsWithoutSlides,
                                    self.slideQuestionsFollowedBySlides,
                                    self.slideSlidesFollowedByQuestions,
                                    self.slideAnswersWithoutSlides,
                                    self.slideAnswersFollowedBySlides,
                                    self.slideSlidesFollowedByAnswers)

        return notesParsing

    def getNotesAndCropsParsing(self):
        """Gets dictionaries of various question and answer parsings, as well as slide crop values."""

        notesAndCropsParsing = NotesAndCropsParsing(self.fullNotes,
                                                    self.slideQuestionsWithoutSlides,
                                                    self.slideQuestionsFollowedBySlides,
                                                    self.slideQuestionsFollowedBySlidesCrops,
                                                    self.slideSlidesFollowedByQuestions,
                                                    self.slideSlidesFollowedByQuestionsCrops,
                                                    self.slideAnswersWithoutSlides,
                                                    self.slideAnswersFollowedBySlides,
                                                    self.slideAnswersFollowedBySlidesCrops,
                                                    self.slideSlidesFollowedByAnswers,
                                                    self.slideSlidesFollowedByAnswersCrops)

        return notesAndCropsParsing


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

singleSlideQ_S = u'''Slide 1:
    Q_S: Question
'''

singleSlideS_Q = u'''Slide 1:
    S_Q: Question
'''

singleSlideA = u'''Slide 1:
    A: Answer
'''

singleSlideA_S = u'''Slide 1:
    A_S: Answer
'''

singleSlideS_A = u'''Slide 1:
    S_A: Answer
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

singleSlideQ_SCrop = u'''Slide 1:
    Q_S[0:50,50:100]: Question
'''

singleSlideS_QCrop = u'''Slide 1:
    S_Q[25-50,50-75]: Question
'''

singleSlideA_SCrop = u'''Slide 1:
    A_S[10-40,10:100]: Answer
'''

singleSlideS_ACrop = u'''Slide 1:
    S_A[0:100,0-10]: Answer
'''

singleSlideQ_SCropBadValues = u'''Slide 1:
    Q_S[50:0,100:10]: Question
'''

singleSlideA_SCropBadValues = u'''Slide 1:
    A_S[0:0,100:100]: Answer
'''

singleSlideQ_SAndA_SNumericalCrop = u'''Slide 1:
    Q_S[0-25, 25-50]: Question
    A_S[50-75, 75-100]: Answer
'''

singleSlideS_QAndS_AAlphabeticalCrop = u'''Slide 1:
    S_Q[t]: Question
    S_A[b]: Answer
'''

class TestParser(unittest.TestCase):
    def testSingleSlide(self):
        p = Parser(StringIO(singleSlide))
        n = p.getQuestions()

        self.assertEqual(len(n), 1)
        self.assertEqual(n[1], 'Question')

    def testMultipleSlides(self):
        p = Parser(StringIO(multipleSlides))
        n = p.getQuestions()

        self.assertEqual(len(n), 2)
        self.assertEqual(n[1], 'Question1')
        self.assertEqual(n[200], 'Question2')

    def testEmptySlide(self):
        n = Parser(StringIO(emptySlide)).getQuestions()

        # Empty slides are not recorded
        self.assertEqual(len(n), 1)
        self.assertEqual(n[2], 'Question')

    def testMultilineQuestion(self):
        n = Parser(StringIO(multilineQuestion)).getQuestions()

        self.assertEqual(len(n), 1)
        self.assertEqual(n[1], '- Q1<br><br>- Q2')

    def testEmptyLines(self):
        n = Parser(StringIO(emptyLineQuestions)).getQuestions()

        self.assertEqual(len(n), 2)
        self.assertEqual(n[1], 'Question-1')
        self.assertEqual(n[2], 'Question-2')

    def testMultipleSlideMentions(self):
        n = Parser(StringIO(multipleSlideMentions)).getQuestions()

        self.assertEqual(len(n), 2)
        self.assertEqual(n[1], 'Question-a<br><br>Question-c')
        self.assertEqual(n[2], 'Question-b')

    def testSingleSlideQ(self):
        p = Parser(StringIO(singleSlideQ))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'Q: Question')
        self.assertEqual(q[1], 'Question')
        self.assertEqual(q_s[1], '')
        self.assertEqual(s_q[1], '')
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(s_a[1], '')

    def testSingleSlideQ_S(self):
        p = Parser(StringIO(singleSlideQ_S))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'Q_S: Question')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], 'Question')
        self.assertEqual(s_q[1], '')
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(s_a[1], '')

    def testSingleSlideS_Q(self):
        p = Parser(StringIO(singleSlideS_Q))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'S_Q: Question')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(s_q[1], 'Question')
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(s_a[1], '')

    def testSingleSlideA(self):
        p = Parser(StringIO(singleSlideA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'A: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(s_q[1], '')
        self.assertEqual(a[1], 'Answer')
        self.assertEqual(a_s[1], '')
        self.assertEqual(s_a[1], '')

    def testSingleSlideA_S(self):
        p = Parser(StringIO(singleSlideA_S))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'A_S: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(s_q[1], '')
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], 'Answer')
        self.assertEqual(s_a[1], '')

    def testSingleSlideS_A(self):
        p = Parser(StringIO(singleSlideS_A))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(n[1], 'S_A: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(s_q[1], '')
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(s_a[1], 'Answer')

    def testSingleSlideQAndA(self):
        p = Parser(StringIO(singleSlideQAndA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(n[1], 'Q: Question<br><br>A: Answer')
        self.assertEqual(q[1], 'Question')
        self.assertEqual(a[1], 'Answer')

    def testMultipleSlideQAndA(self):
        p = Parser(StringIO(multipleSlideQAndA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(n[1], 'Q: Question-1<br><br>A: Answer-1')
        self.assertEqual(n[2], 'Q: Question-2<br><br>A: Answer-2')
        self.assertEqual(q[1], 'Question-1')
        self.assertEqual(a[1], 'Answer-1')
        self.assertEqual(q[2], 'Question-2')
        self.assertEqual(a[2], 'Answer-2')

    def testMultiLineeQAndA(self):
        p = Parser(StringIO(multiLineQAndA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(n[1], 'Q: Question-1<br><br>Q: Question-2<br><br>A: Answer-1<br><br>A: Answer-2')
        self.assertEqual(q[1], 'Question-1<br><br>Question-2')
        self.assertEqual(a[1], 'Answer-1<br><br>Answer-2')

    def testEmptyLineQAndA(self):
        p = Parser(StringIO(emptyLineQAndA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(n[1], 'Q: Question-1<br><br>A: Answer-1')
        self.assertEqual(n[2], 'Q: Question-2<br><br>A: Answer-2')
        self.assertEqual(q[1], 'Question-1')
        self.assertEqual(a[1], 'Answer-1')
        self.assertEqual(q[2], 'Question-2')
        self.assertEqual(a[2], 'Answer-2')

    def testMultipleSlideMentionsQAndA(self):
        p = Parser(StringIO(multipleSlideMentionsQAndA))
        n, q, q_s, s_q, a, a_s, s_a = p.getNotesParsing()

        self.assertEqual(len(n), 2)
        self.assertEqual(len(q), 2)
        self.assertEqual(len(a), 2)
        self.assertEqual(n[1], 'Q: Question-a<br><br>A: Answer-a<br><br>Q: Question-c<br><br>A: Answer-c')
        self.assertEqual(n[2], 'Q: Question-b<br><br>A: Answer-b')
        self.assertEqual(q[1], 'Question-a<br><br>Question-c')
        self.assertEqual(a[1], 'Answer-a<br><br>Answer-c')
        self.assertEqual(q[2], 'Question-b')
        self.assertEqual(a[2], 'Answer-b')

    def testSingleSlideQ_SCrop(self):
        p = Parser(StringIO(singleSlideQ_SCrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'Q_S[0:50,50:100]: Question')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], 'Question')
        self.assertEqual(q_s_c[1], [[0, 50], [50,100]])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(a_s_c[1], [])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideS_QCrop(self):
        p = Parser(StringIO(singleSlideS_QCrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'S_Q[25-50,50-75]: Question')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(q_s_c[1], [])
        self.assertEqual(s_q[1], 'Question')
        self.assertEqual(s_q_c[1], [[25,50], [50,75]])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(a_s_c[1], [])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideA_SCrop(self):
        p = Parser(StringIO(singleSlideA_SCrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'A_S[10-40,10:100]: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(q_s_c[1], [])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], 'Answer')
        self.assertEqual(a_s_c[1], [[10,40], [10,100]])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideS_ACrop(self):
        p = Parser(StringIO(singleSlideS_ACrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'S_A[0:100,0-10]: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(q_s_c[1], [])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(a_s_c[1], [])
        self.assertEqual(s_a[1], 'Answer')
        self.assertEqual(s_a_c[1], [[0,100], [0,10]])

    def testSingleSlideQ_SCropBadValues(self):
        p = Parser(StringIO(singleSlideQ_SCropBadValues))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'Q_S[50:0,100:10]: Question')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], 'Question')
        self.assertEqual(q_s_c[1], [[0, 100], [0,100]])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(a_s_c[1], [])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideA_SCropBadValues(self):
        p = Parser(StringIO(singleSlideA_SCropBadValues))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'A_S[0:0,100:100]: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(q_s_c[1], [])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], 'Answer')
        self.assertEqual(a_s_c[1], [[0,100], [0,100]])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideQ_SAndA_SNumericalCrop(self):
        p = Parser(StringIO(singleSlideQ_SAndA_SNumericalCrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'Q_S[0-25, 25-50]: Question<br><br>A_S[50-75, 75-100]: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], 'Question')
        self.assertEqual(q_s_c[1], [[0,25], [25, 50]])
        self.assertEqual(s_q[1], '')
        self.assertEqual(s_q_c[1], [])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], 'Answer')
        self.assertEqual(a_s_c[1], [[50,75], [75,100]])
        self.assertEqual(s_a[1], '')
        self.assertEqual(s_a_c[1], [])

    def testSingleSlideS_QAndS_AAlphabeticalCrop(self):
        p = Parser(StringIO(singleSlideS_QAndS_AAlphabeticalCrop))
        n, q, q_s, q_s_c, s_q, s_q_c, a, a_s, a_s_c, s_a, s_a_c = p.getNotesAndCropsParsing()

        self.assertEqual(len(n), 1)
        self.assertEqual(len(q), 1)
        self.assertEqual(len(q_s), 1)
        self.assertEqual(len(q_s_c), 1)
        self.assertEqual(len(s_q), 1)
        self.assertEqual(len(s_q_c), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(a_s), 1)
        self.assertEqual(len(a_s_c), 1)
        self.assertEqual(len(s_a), 1)
        self.assertEqual(len(s_a_c), 1)
        self.assertEqual(n[1], 'S_Q[t]: Question<br><br>S_A[b]: Answer')
        self.assertEqual(q[1], '')
        self.assertEqual(q_s[1], '')
        self.assertEqual(q_s_c[1], [])
        self.assertEqual(s_q[1], 'Question')
        self.assertEqual(s_q_c[1], [[0,100], [0, 50]])
        self.assertEqual(a[1], '')
        self.assertEqual(a_s[1], '')
        self.assertEqual(a_s_c[1], [])
        self.assertEqual(s_a[1], 'Answer')
        self.assertEqual(s_a_c[1], [[0,100], [50,100]])

