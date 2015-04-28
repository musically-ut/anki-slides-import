# anki-slides-import

Import pdf slides + text notes into [Anki](http://ankisrs.net/).

Convert:

<p align="center">
<img alt="Slides and notes" src="http://musicallyut.in/docs/anki-import-slides/slides-notes.png" width="80%" />
</p>

to:

<p align="center">
<img alt="Anki deck" src="http://musicallyut.in/docs/anki-import-slides/in-anki.png" width="80%" align="center" />
</p>

## Usage

 0. ~~Clone this repo and run `pip -r requirements.txt` to install dependencies.~~
 0. Use `pip` to install it on your system: `pip install git+https://github.com/musically-ut/anki-slides-import@master#egg=AnkiSlidesImport`
 1. Write your notes slide by slide in a [(formatted) plain text file](https://github.com/musically-ut/anki-slides-import/blob/master/test/example_notes.txt). 
 2. Obtain the slides in pdf format.
 3. Run `slides2anki <notes.txt> <slides.pdf> <output.deck>`. 
     - Currently, you need to add `-U "~/Documents/Anki/User 1"` to explicitly provide you [user profile folder](http://ankisrs.net/docs/manual.html#file-locations).
     - If you cloned this repository, then replace `slides2anki` with `./slides_import.py` while in the repository root.
 4. Open Anki and import the `<output.deck>` as a CSV file.

The deck should be ready to use.

### Dependencies 

You can set up the dependencies required by the files by running the following:

    pip install -r requirements.txt

You may have to [install ImageMagick](http://docs.wand-py.org/en/0.4.0/guide/install.html) for your system separately.

The reason this is not available as an addon for Anki is because [only 32 bit binaries are distributed for Anki](https://anki.tenderapp.com/discussions/ankidesktop/12256-anki-app-on-mac-osx-runs-in-32-bit-mode) and that makes it impossible to use 64-bit ImageMagick libraries. Also, it is tricky to install the 32 bit libraries for ImageMagick using the standard tools (at least on Mac with `homebrew`).

If I release an addon, then it will run if one checks-out and runs [Anki from source](https://github.com/dae/anki) (`./runanki` from the terminal). The version from source will use and update the database used by the system-wide Anki version. However, if one is willing to go through the trouble of doing that, then one might as well use this tool from the command line.

## Help

Use `./slides_import.py -h` to see advanced help on command line options.

## Why?

I made this with two use cases in mind:

 1. Some concepts are easier to understand in images and extracting images from pdfs to put in cards is cumbersome.
 2. This will allow one to take notes slide by slide in class and then directly import them into Anki.

## Next steps

 - Allow markdown in the slide notes
