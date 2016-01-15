# fightclub-5e-fill
Take character sheets exported from [Fight Club 5e](https://itunes.apple.com/au/app/fight-club-5th-edition/id901057473) and use them to populate form-fillable D&amp;D character sheets using [pdftk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)

Most of the code is just working out a mapping from the Fight Club XML to the form fields. Some of the more complex bits are taking into account proficiencies and modifiers from different sources and using them to calculate ability and skill modifiers.

Usage:

1. Install pdftk
2. <code> pip install fdfgen </code>
3. Add XML file to directory and change refernece to it in python file. Will change to command line arg later.
4. <code> python3 fightclub-5e-fill.py </code>
