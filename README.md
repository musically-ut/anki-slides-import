# anki-slides-import

This is a fork of [Utkarsh Upadhyay's](https://github.com/musically-ut) [anki-slides-import](https://github.com/musically-ut/anki-slides-import) code for importing PDF slides + text notes into [Anki](http://ankisrs.net/) that includes some additional functionality.  This modified version allows for the PDF slides to be displayed either in the Anki card question or answer, to be included alongside some additional text either before or after the slide, or to be left out completely.  It also allows the slides to be cropped.

Convert:

<p align="center">
<img alt="Slides and notes" src="http://musicallyut.in/docs/anki-import-slides/slides-notes.png" width="80%" />
</p>

to:

<p align="center">
<img alt="Anki deck" src="http://musicallyut.in/docs/anki-import-slides/in-anki.png" width="80%" align="center" />
</p>

## Usage

 0. Use `pip` to install it on your system: 
  
        pip install git+https://github.com/barryridge/anki-slides-import

 1. Write your notes slide by slide in a [plain text file](https://github.com/barryridge/anki-slides-import/blob/master/test/example_notes.txt).
 2. Obtain the slides in pdf format.
 3. Run `slides2anki <notes.txt> <slides.pdf> <output.deck.name>`. 
     - Currently, you need to add `-U "~/Documents/Anki/User 1"` to explicitly provide you [user profile folder](http://ankisrs.net/docs/manual.html#file-locations).
     - If you cloned this repository, then replace `slides2anki` with `./slides_import.py` while in the repository root.
 4. Open Anki and import the `<output.deck>` as a CSV file.

The deck should be ready to use.

### Anki Card Modifiers

The [`test/example_notes_q_and_a.txt`](https://github.com/barryridge/anki-slides-import/blob/master/test/example_notes_q_and_a.txt) file provides examples of how to use Anki card modifiers to alter the behaviour of Anki card generation and slide insertion.  The available slide modifiers come in two varieties that allow for either positional control or slide cropping respectively, and are listed as follows:

#### Positional Control

  * `Q: ` - Include the succeeding text as a standalone question without a slide (default behaviour without card modifiers).
  * `Q_S: ` - Include the succeeding text as a question followed by the current slide.
  * `S_Q: ` - Include the current slide followed by the succeeding text as a question.
  * `A: ` - Include the succeeding text as a standalone answer without a slide.
  * `A_S: ` - Include the succeeding text as an answer followed by the current slide.
  * `S_A: ` - Include the current slide followed by the succeeding text as an answer.

#### Slide Cropping

##### Cropping with alphabetical codes

  This is probably the most convenient way to crop slides.  Four of the above positional control modifiers, `Q_S: `, `S_Q: `, `A_S: ` and `S_A: `, can be amended by including codes in square brackets before the colon, like `t`, for `top`, that would crop the top half of the slide, e.g. `Q_S[t]: `.  The full list of possible alphabetical cropping codes are as follows:

  * `a` or `w` - 'All' of the slide, or the 'whole' of the slide (Numerical: `[[0, 100], [0, 100]]`).
  * `t` or `th` - 'Top' or 'top half' of the slide (Numerical: `[[0, 100], [0, 50]]`).
  * `vmh` - 'Vertical middle half' of the slide (Numerical: `[[0, 100], [25, 75]]`).
  * `b` or `bh` - 'Bottom' or 'bottom half' of the slide (Numerical: `[[0, 100], [50, 100]]`).
  * `l` or `lh` - 'Left' or 'left half' of the slide (Numerical: `[[0, 50], [0, 100]]`).
  * `mh` or `hmh` - 'Middle half' or 'horizontal middle half' of the slide (Numerical `[[25, 75], [0, 100]]`).
  * `r` or `rh` - 'Right' or 'right half' of the slide (Numerical: `[[50, 100], [0, 100]]`).
  * `m` or `c` or `mq` or `cq` - 'Middle' or 'centre' or 'middle quarter' or 'centre quarter' of the slide (Numerical: `[[25, 75], [25, 75]]`).
  * `tl` or `tlq` - 'Top-left' or 'top-left quarter' of the slide (Numerical: `[[0, 50], [0, 50]]`).
  * `tr` or `trq` - 'Top-right' or 'top-right quarter' of the slide (Numerical: `[[50, 100], [0, 50]]`).
  * `bl` or `blq` - 'Bottom-left' or 'bottom-left quarter' of the slide (Numerical: `[[0, 50], [50, 100]]`).
  * `br` or `brq` - 'Bottom-right' or 'bottom-right quarter' of the slide (Numerical: `[[50, 100], [50, 100]]`).
  * `tt` - 'Top third' of the slide (Numerical: `[[0, 100], [0, 33]]`).
  * `vmt` - 'Vertical middle third' of the slide (Numerical: `[[0, 100], [33, 66]]`).
  * `bt` - 'Bottom third' of the slide (Numerical: `[[0, 100], [66, 100]]`).
  * `lt` - 'Left third' of the slide (Numerical: `[[0, 33], [0, 100]]`).
  * `mt` or `hmt` - 'Middle third' or 'horizontal middle third' of the slide (Numerical: `[[33, 66], [0, 100]]`).
  * `rt` - 'Right third' of the slide (Numerical: `[[66, 100], [0, 100]]`).

##### Cropping with numerical values

  Alternatively, for finer control, the cropping values may be specified numerically as percentages, by amending the positional control codes with `[[wmin, wmax], [hmin, hmax]]` codes before the colon, e.g. `A_S[[25,75], [0, 100]]: `.

### Dependencies 

You may have to [install ImageMagick](http://docs.wand-py.org/en/0.4.0/guide/install.html) for your system separately.

If you want to develop this tool, you can set up the dependencies required by the files by running the following:

    pip install -r requirements.txt

## Why is this not an Anki addon

The reason this is not available as an addon for Anki is because [only 32 bit binaries are distributed for Anki](https://anki.tenderapp.com/discussions/ankidesktop/12256-anki-app-on-mac-osx-runs-in-32-bit-mode) and that makes it impossible to use 64-bit ImageMagick libraries. Also, it is tricky to install the 32 bit libraries for ImageMagick using the standard tools (at least on Mac with `homebrew`).

If I release an addon, then it will run if one checks-out and runs [Anki from source](https://github.com/dae/anki) (`./runanki` from the terminal). The version from source will use and update the database used by the system-wide Anki version. However, if one is willing to go through the trouble of doing that, then one might as well use this tool from the command line.

## Help

Use `slides2anki -h` to see advanced help on command line options.

## Why?

I made this with two use cases in mind:

 1. Some concepts are easier to understand in images and extracting images from pdfs to put in cards is cumbersome.
 2. This will allow one to take notes slide by slide in class and then directly import them into Anki.

## Next steps

 - Allow markdown in the slide notes
