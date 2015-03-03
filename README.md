# anki-slides-import

Import pdf slides + text notes into [Anki](http://ankisrs.net/).

Convert:

![Slides and notes](http://musicallyut.in/docs/anki-import-slides/slides-notes.png)

to:

![Anki deck](http://musicallyut.in/docs/anki-import-slides/in-anki.png)

## Usage


 1. Write your notes slide by slide in a [(formatted) plain text file](https://github.com/musically-ut/anki-slides-import/blob/master/test/example_notes.txt). 
 2. Obtain the slides in pdf format.
 3. Run `./slides_import.py <notes.txt> <slides.pdf> <output.deck>`
     - Currently, you need to add `-U "~/Documents/Anki/User 1"` to explicitly provide you [user profile folder](http://ankisrs.net/docs/manual.html#file-locations).
 4. Open Anki and import the `<output.deck>` as a CSV file.

The deck should be ready to use.

### Dependencies 

You can set up the dependencies required by the files by running the following:

    pip install -r requirements.txt

## Help

Use `./slides_import.py -h` to see advanced help on command line options.

## Why?

I made this with two use-cases in mind:

 1. Some concepts are easier to understand in images and extracting images from pdfs to put in cards is cumbersome.
 2. This will potentially allow one to take notes slide by slide in class and then directly import them into Anki.

## Next steps

 - Allow markdown in the slide notes
