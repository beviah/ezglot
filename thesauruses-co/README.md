# Thesauruses.co

This is series of ~20 scripts used for parsing and structuring Wiktionary data in a template (locale) agnostic way!
The same scripts are used to parse all 170+ wiktionary dumps!

Final dataset was and will be used again at https://www.ezglot.com/

We need to upgrade the server to handle the traffic with all new data we created over the years.

## Files

**1. wiki_parse.py**
  - Loads Wiktionary XML dumps from ./xmls folder
  - Detects templates and attempts replacements
  - Normalizes common wiki markups found in various locales (maybe it is not locale agnostic!)
              but does not rely on specific language strings (maybe it is!)
  - Converts content into node-property-relation like paths with more/less consistent levels..
              to be further dealt with in later script(s)

I thought I had the problem solved with this script, but oh boy, was I wrong.. took *a few* more processing steps...

**2. finer.py**

 - *Every few dozen stars will motivate me to add one more script ;-)*

**3. polngrams.py**

...
