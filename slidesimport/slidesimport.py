# -*- coding: utf-8 -*-

from pdfpages import PdfPages
from parser import Parser, ParseException, NotesAndCropsParsing

import sys
import os
import argparse as A


def getMediaName(prefix, slideNumber, frmt='png'):
    """Returns the relative name of the media file."""
    return prefix + '-' + str(slideNumber) + '.' + frmt

def getMediaPath(collectionMediaPath, prefix, slideNumber, frmt='png'):
    """Return the file name of the destination media file."""
    return os.path.join(collectionMediaPath, getMediaName(prefix, slideNumber, frmt))

# TODO: Verify that argument parsers does not offer a fancy way of accepting
# paths while verifying that they exist or not, etc.

def run(rawArgs=None):
    argParser = A.ArgumentParser()
    argParser.add_argument( 'notes',
                            help = 'The notes for the lectures. For details on how to write notes, see: https://gist.github.com/musically-ut/5b5835c06470842cf752',
                            type = str
                          )

    argParser.add_argument( 'slides',
                            help = 'The pdf slides for the same lecture.',
                            type = str
                          )

    argParser.add_argument( 'deck',
                            help = 'The file to output the deck to.',
                            type = str
                          )

    argParser.add_argument( '-U', '--anki',
                            help = 'The Anki Profile folder to use.',
                            type = str
                          )

    argParser.add_argument( '-P', '--prefix',
                            help = 'The prefix to use for the deck. Must be unique. ',
                            type = str
                          )

    argParser.add_argument( '-f', '--force',
                            help = 'Force overwriting files.',
                            action = 'store_true'
                          )

    if rawArgs is not None:
        args = argParser.parse_args(rawArgs)
    else:
        args = argParser.parse_args()


    #########################################################################

    print 'Verifying arguments ...'

    # Check for existence of user folder first
    if args.anki is None:
        print >> sys.stderr, 'Giving a User folder is necessary.'
        print >> sys.stderr, 'Requirement will soon be removed.'
        sys.exit(-1)

    ankiPath = os.path.expanduser(args.anki)

    if not os.path.isdir(ankiPath):
        print >> sys.stderr, 'Folder: {} does not exist.'.format(ankiPath)
        sys.exit(-1)

    collectionMediaPath = os.path.join(ankiPath, 'collection.media')
    if not os.path.isdir(collectionMediaPath):
        print >> sys.stderr, 'Folder: {} does not exist.'.format(collectionMediaPath)
        print >> sys.stderr, 'Is "{}" the path to a user profile?'.format(ankiPath)
        sys.exit(-1)

    print 'Done.'


    #########################################################################

    print "Reading files ..."
    try:
        notesFilePath = os.path.expandvars(os.path.expanduser(args.notes))
        notes = Parser(file(notesFilePath, 'r')).getNotesAndCropsParsing()
        pdfPages = PdfPages(os.path.expandvars(os.path.expanduser(args.slides)))
    except IOError as e:
        print >> sys.stderr, "Error while reading source files: "
        print >> sys.stderr, e
        sys.exit(-1)
    except ParseException as e:
        print >> sys.stderr, "Parsing error:"
        print >> sys.stderr, e.message
        sys.exit(-1)

    print 'Done reading files.'

    #######################################################################
    # Determine if any file be overwritten
    #######################################################################

    prefix = args.prefix or os.path.basename(args.slides)
    if not args.force:
        for slideNum in notes.fullNotes:
            questionMediaFileName = getMediaPath(collectionMediaPath, prefix + '-question', str(slideNum))
            # For now, we leave this without an '-answer' suffix for backwards compatibility
            answerMediaFileName = getMediaPath(collectionMediaPath, prefix, str(slideNum))
            if os.path.exists(questionMediaFileName):
                print >> sys.stderr, 'File "{}" already exists. Choose a different prefix (using --prefix) or use -f to overwrite the files.'.format(questionMediaFileName)
                sys.exit(-1)
            if os.path.exists(answerMediaFileName):
                print >> sys.stderr, 'File "{}" already exists. Choose a different prefix (using --prefix) or use -f to overwrite the files.'.format(answerMediaFileName)
                sys.exit(-1)


    #######################################################################
    # Operation begins, potentially destructive changes beyond this point
    #######################################################################

    print 'Starting extraction ...'

    deckFilePath = os.path.expandvars(os.path.expanduser(args.deck))
    outputDeckFile = file(deckFilePath, 'w')

    for slideNum, qs in notes.fullNotes.items():
        questionMediaFilePath = ''
        questionMediaFileName = ''
        answerMediaFilePath = getMediaPath(collectionMediaPath, prefix, slideNum)
        answerMediaFileName = getMediaName(prefix, slideNum)
        questionCropPercentValues = [[0,100], [0,100]]
        answerCropPercentValues = [[0,100], [0,100]]
        outputString = ''

        # If the "question without slide" dict entry is not empty, write that
        if notes.questionsWithoutSlides[slideNum] != '':
            outputString += '"{0}"; '.format(notes.questionsWithoutSlides[slideNum])
        # Otherwise try "question followed by slide"
        elif notes.questionsFollowedBySlides[slideNum] != '':
            questionMediaFilePath = getMediaPath(collectionMediaPath, prefix + '-question', slideNum)
            questionMediaFileName = getMediaName(prefix + '-question', slideNum)
            outputString += '<div>{0}</div><img src="{1}" />; '.format(notes.questionsFollowedBySlides[slideNum], questionMediaFileName)
            if notes.questionsFollowedBySlidesCrops[slideNum] != []:
                questionCropPercentValues = notes.questionsFollowedBySlidesCrops[slideNum]
        # Otherwise try "slide followed by question"
        elif notes.slidesFollowedByQuestions[slideNum] != '':
            questionMediaFilePath = getMediaPath(collectionMediaPath, prefix + '-question', slideNum)
            questionMediaFileName = getMediaName(prefix + '-question', slideNum)
            outputString += '<img src="{0}" /><div>{1}</div>; '.format(questionMediaFileName, notes.slidesFollowedByQuestions[slideNum])
            if notes.slidesFollowedByQuestionsCrops[slideNum] != []:
                questionCropPercentValues = notes.slidesFollowedByQuestionsCrops[slideNum]
        # Otherwise fall back to default behaviour
        else:
            outputString += '"{0}"; '.format(qs)

        # If the "answer without slide" dict entry is not empty, write that
        if notes.answersWithoutSlides[slideNum] != '':
            outputString += '"{0}"\n'.format(notes.answersWithoutSlides[slideNum])
            answerMediaFileName = ''
        # Otherwise try "answer followed by slide"
        elif notes.answersFollowedBySlides[slideNum] != '':
            outputString += '<div>{0}</div><img src="{1}" />\n'.format(notes.answersFollowedBySlides[slideNum], answerMediaFileName)
            if notes.answersFollowedBySlidesCrops[slideNum] != []:
                answerCropPercentValues = notes.answersFollowedBySlidesCrops[slideNum]
        # Otherwise try "slide followed by answer"
        elif notes.slidesFollowedByAnswers[slideNum] != '':
            outputString += '<img src="{0}" /><div>{1}</div>\n'.format(answerMediaFileName, notes.slidesFollowedByAnswers[slideNum])
            if notes.slidesFollowedByAnswersCrops[slideNum] != []:
                answerCropPercentValues = notes.slidesFollowedByAnswersCrops[slideNum]
        # Otherwise fall back to default behaviour
        else:
            outputString += '<img src="{0}" />\n'.format(answerMediaFileName)

        # Write deck file output
        outputDeckFile.write(outputString)
        
        # print "notes.questionsFollowedBySlidesCrops:"
        # print notes.questionsFollowedBySlidesCrops

        # print "notes.answersFollowedBySlidesCrops:"
        # print notes.answersFollowedBySlidesCrops
        
        # Save question slide if necessary
        if questionMediaFilePath != '':
            # print "questionCropPercentValues:"
            # print questionCropPercentValues
            pdfPages.getCroppedPageAsPng(slideNum, questionCropPercentValues).save(filename=questionMediaFilePath)

        # Save answer slide if necessary
        if answerMediaFilePath != '':
            # print "answerCropPercentValues:"
            # print answerCropPercentValues
            pdfPages.getCroppedPageAsPng(slideNum, answerCropPercentValues).save(filename=answerMediaFilePath)
