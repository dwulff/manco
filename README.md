# **manco**

**manco** is a graphical user interface for semi-automaized, **man**ual spelling **co**rrection and processing of human language data written in python using the tkinter library. It incorporates a simple spelling correction algorithm based on Peter Norvig's tutorial (http://norvig.com/spell-correct.html) and the Snowball stemmer of Python's nltk library (http://www.nltk.org/).

## Installation

To run the software copy the files onto the harddrive and then execute `python pylap.py` in the terminal from within the program folder. Software depends on: `TKinter`, `nltk`, `sys`, `re`, `os`, `pickle`, `time`, and `random`.

## Use

### Get started

When using the software for the first time, the first thing to do is to import a list of words that needs to be processed. words in word file must be separated either by new line or by separator specified by `Settings/Separator`.

When loaded, the program renders all words lower case. Then the program reduces the list of words to its unique entries and checks them against the internal list of correct word forms. The program then present only unique words not contained in that list (based on the original order).

The list of correct word forms is adapted from the German aspell dictionary (http://aspell.net/).

### Correct spellings

Given a current word, displayed on the top of the screen, the program provides several options to enter its corrected form. 

- *Suggestions* In the top left corner up to three buttons display suggestions from the spellchecker. Note that set of suggestions always contains the current word. Therefore, even if there are no alternate suggestions, the current word is given as an option.

- *Entry* Using the entry filed located below the suggestion buttons the correction can be entered manually. The field will present as the defaul value the current word. To enter a correction use the plus button right below the entry field or press ENTER. You can also change the entry field to whatever entry in the dictionary by clicking on the respective field in the dictionary. This will pull the corrected word form from the dictionary. You can also reset the entry field content by clicking on the current word to be corrected.

- *NA* To indicate that a word is not actually a word, click the **NA** button below the entry and plus fields. 

### Dictionary

The program stores a dictionary of the corrections made. The dictionary is displayed on the top right corner in terms of a *wrong word* → *corrected corrected* mapping. 

The dictionary can be inspected in two ways. First, by moving the mouse into the history field the user can scroll up and down. Entries are ordered according to their point of creation, with new entries being added at the bottom. Second, the dictionary can be searched by entering letters or words into field below the history, which will subset the dictionary to those entries that contain the entered string. To reset the selection simply delete all entered strings in the search field. 

To alter entries in the dictionary, select an entry and press the **-** button, which will remove the entry from the list and make the *wrong word* the current word. 

There is two ways of including a dictionary: It can be from an *.mancodict* file or it can be imported from a text file. In both cases entries not presently included in any current dictionary will be added to the current dictionary. When importing from text file you must adhere to the following format: 1) one line per entry and 2) wrong and correct word form must be separated by `Settings/Separator`. Also make sure that the last line is not empty.

To save a dictionary use `File/Save/Dictionary`. The file will be stored in pylap's dictionary file format *.mancodict*. 

### Processing

Language like German permit compound words that are correct, but not are not contained in common lists of correct word forms. In order to detect such words select `Processing/Detect compounds`. This will initiate a process that will go through all of the words and check whether the word is entirely composed of two words from the correct word form list. The detected compounds will then be removed from the list of to be corrected words and handled accordingly in exporting the data.

### Project

Projects can be interrupted and continued later. To do this save the project via `File/Save/Project`. The project will be stored in pylap's project file format *.plproject*. The project stores a complete representation of the current program including the word list, the dictionary, and the chosen language.

Note that loading a project implies discarding the current one. 

### Autosave

At the beginning of a session the program sets an autosave file, which is updated at every correction. The autosaves contain the full project and can be retrieved via `File/Load/Autosave`.  

Note that autosaves are only available for the the ten most recent sessions. Autosaves are named by the at which the session was initiated.

### Language

Pylap has rudimentary support for English. Change language via `Settings/Language`.

### Export

The program exports data in two different ways, either including or excluding the stemmed word forms. To export only the original and corrected word forms (for every non-unique entry in the loaded word list) as a .txt file separated by `Settings/Separator` select `Export/Export`. To both including also the stemmed wordforms select `Export/Export and stem`.


