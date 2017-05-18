# -*- coding: utf-8 -*-
from __future__ import division
from Tkinter import *
from correct import correct
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import showwarning
from nltk import stem
from collections import Counter
import sys, re, os, pickle, nltk, time, random, ttk
import numpy as np

class Application(Frame):
    """pylap"""

    # ------------------------------------------------------------------------------------------------------------------
    #       INIT
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, parent):
        """
        Initialize the GUI
        - places the GUI on the grid
        - run startup settings
        - creates menu
        - create widgets
        """

        # place GUI on grid
        Frame.__init__(self, parent)
        self.grid()

        # store parent
        self.parent = parent

        # startup settings
        self.settings()

        # create menu
        self.create_menu()

        # initialize word processors
        self.init_wordprocessers()

        # create widgets
        self.create_widgets()

    # ------------------------------------------------------------------------------------------------------------------
    #       STARTUP
    # ------------------------------------------------------------------------------------------------------------------

    def settings(self):
        """
        Startup settings
        - define paths
        - creates bunch of variables
        - sets defaults for index, language, and separator
        - place entry instructions
        """

        # define paths
        self.path = os.path.realpath(__file__).replace('pylap.py','')
        self.autosave_path = self.path + '_autosave/'

        # define containers
        self.accepts = set()

        # create variables
        self.ind = IntVar()
        self.ind_text = StringVar()
        self.curr_word = StringVar()
        self.curr_sugg1 = StringVar()
        self.curr_sugg2 = StringVar()
        self.curr_sugg3 = StringVar()
        self.entry_text = StringVar()
        self.search_text = StringVar()
        self.language = StringVar()
        self.separator = StringVar()
        self.export = StringVar()

        # set variables
        self.ind.set(0)
        self.language.set('German')
        self.separator.set('tab')

        # entry instruction
        self.instruct = Label(text = 'Please load word list or project',
                              font = ('Times New Roman', 16, 'italic'),
                              wraplength = 400)
        self.instruct.grid(column = 0, columnspan = 1, row = 4)

    def init_wordprocessers(self):
        """
        Initialize Word processors depending on the language
        """

        if self.language.get() == 'English':
            self.stemmer = stem.snowball.EnglishStemmer()
            self.corr = correct('en')
            return 'en'
        else:
            self.stemmer = stem.snowball.GermanStemmer()
            self.corr = correct('de')
            return 'de'

    def create_menu(self):
        """
        Create menu
        - create toplevel menu
        - create file menu
        - create settings menu
        - create export menu
        """

        # create a toplevel menu
        self.parent.title("spellchecker")
        menubar = Menu(self.parent)
        self.parent.configure(menu=menubar)

        # create and add & load open menu
        file_menu = Menu(menubar)
        open_menu = Menu(file_menu)
        load_menu = Menu(file_menu)
        import_menu = Menu(file_menu)
        save_menu = Menu(file_menu)
        open_menu.add_command(label = "Word list", command = self.open_wordlist)
        open_menu.add_command(label = 'Project', command = self.open_project)
        open_menu.add_separator()
        open_menu.add_command(label='Autosave', command=self.open_autosave)
        load_menu.add_command(label = 'Dictionary', command = self.load_dictionary)
        import_menu.add_command(label = 'Dictionary', command = self.import_dictionary)
        save_menu.add_command(label = 'Project', command = self.save_project)
        save_menu.add_command(label = 'Dictionary', command = self.save_dictionary)
        file_menu.add_cascade(label = "Open", menu = open_menu)
        file_menu.add_cascade(label = "Load", menu = load_menu)
        file_menu.add_cascade(label = "Import", menu = import_menu)
        file_menu.add_cascade(label = "Save", menu = save_menu)
        file_menu.add_separator()
        file_menu.add_command(label = "Quit", command = self.quit)
        menubar.add_cascade(label = "File", menu = file_menu)

        # create processing menu
        processing_menu = Menu(menubar)
        processing_menu.add_command(label = "Compound detection", command = self.identify_compounds)
        menubar.add_cascade(label = "Processing", menu = processing_menu)


        # create settings menu
        settings_menu = Menu(menubar)
        language_menue = Menu(settings_menu)
        seperator_menue = Menu(settings_menu)
        processing_menue = Menu(settings_menu)
        language_menue.add_radiobutton(label="English", variable = self.language, command = self.init_wordprocessers())
        language_menue.add_radiobutton(label="German", variable = self.language, command = self.init_wordprocessers())
        settings_menu.add_cascade(label="Language", menu=language_menue)
        seperator_menue.add_radiobutton(label="space", variable = self.separator)
        seperator_menue.add_radiobutton(label="tab", variable = self.separator)
        seperator_menue.add_radiobutton(label="comma", variable = self.separator)
        seperator_menue.add_radiobutton(label="semicolon", variable = self.separator)
        settings_menu.add_cascade(label="Separator", menu=seperator_menue)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # create export menu
        export_menu = Menu(menubar)
        export_menu.add_command(label = "Export", command = self.export_corrections)
        menubar.add_cascade(label = "Export", menu = export_menu)

    # ------------------------------------------------------------------------------------------------------------------
    #       HELPERS
    # ------------------------------------------------------------------------------------------------------------------

    def get_separator(self):
        """ Retrieve value of separator variable """

        if self.separator.get() == 'space':
            return ' '
        elif self.separator.get() == 'tab':
            return '\t'
        elif self.separator.get() == 'comma':
            return ','
        else:
            return ';'

    # ------------------------------------------------------------------------------------------------------------------
    #       PROJECT HELPERS
    # ------------------------------------------------------------------------------------------------------------------

    def create_project(self):

        # init
        self.project = dict()

        # store
        self.project['ind'] = self.ind.get() - 1
        self.project['lang'] = self.language.get()
        if hasattr(self, 'words'):
            self.project['words'] = self.words
            self.project['unknowns'] = [self.curr_word.get()] + self.unknowns
            self.project['len'] = self.len_unknowns
        if hasattr(self, 'dictionary'):
            self.project['dict'] = self.dictionary

    def handle_project(self):

        # get project
        project = pickle.load(open(self.f_proj, 'rb'))

        # extract i
        self.ind.set(project['ind'])

        # initialize word processors
        self.language.set(project['lang'])

        # initialize dictionary
        if 'dict' in project.keys():
            self.dictionary = project['dict']
            self.update_listbox()
            self.show_listbox()

            # add to accepts
            [self.accepts.add(w[0]) for w in self.dictionary.values()]

        # extract words
        if 'words' in project.keys():
            self.unknowns = project['unknowns']
            self.words = project['words']
            self.len_unknowns = project['len']
            self.show_header()
            self.show_input()

    def check_wordlist(self):

        # start if words exist
        if hasattr(self, 'words'):

            # destroy instruct
            self.instruct.grid_remove()

            # next word
            self.next()
        else:
            self.instruct['text'] = 'Word list missing. Please load word list.'

    # ------------------------------------------------------------------------------------------------------------------
    #       DICTIONARY HELPERS
    # ------------------------------------------------------------------------------------------------------------------

    def handle_dictionary(self, dictionary):

        # create or update dictionary
        if hasattr(self, 'dictionary'):

            # determine max index of existing dictionary
            max_ind = len(self.dictionary)

            # iterate through the entries and shift index by max_ind
            for key, value in dictionary.iteritems():
                dictionary[key] = [value[0], value[1] + max_ind]

            # update dictionary
            self.dictionary.update(dictionary)

            # add to accepts
            [self.accepts.add(w[0]) for w in dictionary.values()]

        else:
            self.dictionary = dictionary


    # ------------------------------------------------------------------------------------------------------------------
    #       OPENERS | LOADERS | IMPORTERS
    # ------------------------------------------------------------------------------------------------------------------

    def open_wordlist(self):
        """
        Function laods a word list. It also creates a dictionary if needed, it makes the dictionary and word widgets 
        visible, it destroys the instruct message, and calls the next item method.
        """

        # get filename
        f_words = askopenfilename()

        # read and preprocess
        self.words = open(f_words, 'rb').read().lower().replace('\n',self.get_separator())

        # split and remove white
        self.words = [unicode(word.strip()) for word in self.words.split(self.get_separator())]

        # determine unknowns and number of unknowns
        self.unknowns = self.corr.unknown(self.words)
        self.len_unknowns = len(self.unknowns)

        # initialize dictionary (if not loaded)
        if not hasattr(self,'dictionary'):
            self.dictionary = dict()

        # start if words exist
        if hasattr(self, 'words'):

            # destroy instruct
            self.instruct.grid_remove()

            # show widgets
            self.show_header()
            self.show_input()
            self.show_listbox()

            # next item
            self.next()
        else:
            self.instruct['text'] = 'Word list missing. Please load word list.'


    def open_project(self):
        """
        Function loads a project file. It asks to select a filename, which then is passed to the project handler. If
        self.words exist next() is called.
        """

        # get project
        self.f_proj = askopenfilename()

        # test if .plproject
        if '.plproject' in self.f_proj:

            # handle project
            self.handle_project()

            # check for word list
            self.check_wordlist()

        else:
            showwarning('Wrong filetype', 'Can only load *.plproject files.')


    def open_autosave(self):
        """
        Function loads an autosave file. It asks to select a filename, which then is passed to the project handler. If
        self.words exist next() is called.
        """

        # get project
        self.f_proj = askopenfilename(initialdir = self.autosave_path)

        # test if .plproject
        if '.plproject' in self.f_proj:

            # handle project
            self.handle_project()

            # check for word list
            self.check_wordlist()

        else:
            showwarning('Wrong filetype', 'Can only load *.plproject files.')



    def load_dictionary(self):
        """
        Function loads a dictionary file. It asks to select a filename, which is then loaded as a pickle. It then checks
        if a dictionary already exists, in which case the dictionary is added with updated indices.
        self.words exist next() is called.
        """

        # get filename
        f_dict = askopenfilename()

        # load dictionary
        loaded_dict = pickle.load(open(f_dict,'rb'))

        # test if .plproject
        if '.pldict' in f_dict:

            # handle dictionary
            self.handle_dictionary(loaded_dict)

            # update listbox to show new content
            self.update_listbox()

            # update intro text if needed
            if not hasattr(self, 'words'):
                self.instruct['text'] = 'Dictionary loaded. Please load word list.'

        else:
            showwarning('Wrong filetype', 'Can only load *.pldict files.')


    def import_dictionary(self):
        """
        Function loads a dictionary from text file. Text file must have two columns with each row containing pairs of
        the uncorrected and corrected word forms separated by self.separator.
        """

        # init loaded dict
        imported_dict = dict()

        # get dictionary filename
        f_dict = askopenfilename()

        # test if .txt or .csv
        if '.txt' in f_dict or '.csv' in f_dict:

            # set index to 0
            ind = 0

            # import dict
            for line in open(f_dict, 'rb'):

                # increment index
                ind += 1

                # retrieve entry pair
                entry = line.lower().replace('\n','').split(self.get_separator())

                # store pair plus index in dictionary
                imported_dict[entry[0]] = [entry[1], ind]

                # store in accepts
                self.accepts.add(entry[1])

            # add dictionary
            self.handle_dictionary(imported_dict)

            # fill dictionary
            self.update_listbox()

            # update intro text if needed
            if not hasattr(self, 'words'):
                self.instruct['text'] = 'Dictionary imported. Please load word list.'

        else:
            showwarning('Wrong filetype', 'Can only import *.txt and *.csv files.')


    # ------------------------------------------------------------------------------------------------------------------
    #       SAVERS
    # ------------------------------------------------------------------------------------------------------------------

    def save_dictionary(self):
        """
        Function saves dictionary as *.pldict file. 
        """

        # check if there is a dictionary
        if hasattr(self, 'dictionary'):

            # get filename
            f_dict = asksaveasfilename(defaultextension = '.pldict')

            # dump dictionary as pickle
            pickle.dump(self.dictionary, open(f_dict, 'wb'), pickle.HIGHEST_PROTOCOL)

        else:
            showwarning('Dictionary missing', 'No dictionary found. Load word list or project.')

    def save_project(self):
        """
        Function saves project as *.plproject file. 
        """

        # create project
        self.create_project()

        # get filename
        f_proj = asksaveasfilename(defaultextension = '.plproject')

        # dump project as pickle
        pickle.dump(self.project, open(f_proj, 'wb'), pickle.HIGHEST_PROTOCOL)

    def auto_save(self):
        '''
        Function dumps auto-saves every ten words. Auto-saves are projects files named using a random code and stored
        in the default auto-save folder in the programs home directory.
        '''

        # get list of existing autosave files
        files = sorted(os.listdir(self.autosave_path))

        # remove all but the last ten
        if len(files) == 10:
            for filename in files[9:]:
                os.remove(self.autosave_path + filename)

        # create autosave filename
        if not hasattr(self, 'autosave_f'):

            # get random letter code
            letters = list('abcdefghijklmnopqrstuvwxyz0123456789')
            random.shuffle(letters)
            self.code = ''.join(letters[:6])

            # determine autosave filename
            self.autosave_f = self.autosave_path + time.strftime("%d-%m-%y_%H:%M:%S") + self.code + '.plproject'

        # create project
        self.create_project()

        # dump as pickle
        pickle.dump(self.project, open(self.autosave_f, 'wb'), pickle.HIGHEST_PROTOCOL)


    # ------------------------------------------------------------------------------------------------------------------
    #       EXPORT
    # ------------------------------------------------------------------------------------------------------------------

    def get_corrections(self):
        """
        Function creates list of corrected word forms.
        """

        # create empty list
        self.corr_words = []

        # create uncorrected counter
        self.n_uncorrected = 0

        # get set of knowns
        known = self.corr.known(self.words)

        # get known compounds
        compounds = self.COMPOUNDS

        # get accepts
        accepts = self.accepts

        # iterate over the words in self.words
        for word in self.words:

            # append word if known
            if word in known or word in compounds or word in accepts:
                self.corr_words.append(word)

            # append correct form if in dict
            elif word in self.dictionary.keys():
                self.corr_words.append(self.dictionary[word][0])

            else:
                self.corr_words.append('@uncorrected@')
                self.n_uncorrected += 1

    def get_stems(self):
        """
        Function creates list of stemmed word forms.
        """

        # create empty list
        self.stem_words = []

        for word in self.corr_words:
            self.stem_words.append(self.stemmer.stem(word))

    def get_lemmas(self):
        """
        Function creates list of lemmas, where each stem is replaced by its most frequent lemma.
        """

        # create empty list
        self.lemma_words = []

        # create dict
        lemmas = dict()

        # iterate through stemmed words
        for word in self.stem_words:

            # check if already encountered
            if word in lemmas.keys():

                # retrieve word from dict
                self.lemma_words.append(lemmas[word])

            else:

                # get indices
                indices = [index for index, value in enumerate(self.stem_words) if value == word]

                # collect lemmas
                candidates = [self.words[i] for i in indices]

                # get most frequent
                self.count = Counter(candidates)
                lemma = self.count.most_common(1)[0][0]

                # add to list
                self.lemma_words.append(lemma)

                # add to lemma dict
                lemmas[word] = lemma

    # ------------------------------------------------------------------------------------------------------------------
    #       EXPORT
    # ------------------------------------------------------------------------------------------------------------------

    def export_corrections(self):
        """
        Function collects the corrected word forms for each word in self.words and identifies its stem and most commen
        lemma. The results are written into a *.txt or *.csv file using self.separator.
        """


        # get expo
        f_export = asksaveasfilename(defaultextension='.txt')

        if '.txt' in f_export or '.csv' in f_export:

            # get separator
            sep = self.get_separator()

            # get corrections
            self.get_corrections()

            # get stems
            self.get_stems()

            # get lemmas()
            self.get_lemmas()


            # open file connection
            with open(f_export, 'wb') as f_expo:

                # iterate over the words in self.words
                for i in range(len(self.words)):

                    f_expo.write(self.words[i] +
                                 sep +
                                 self.corr_words[i] +
                                 sep +
                                 self.stem_words[i] +
                                 sep +
                                 self.lemma_words[i] +
                                 '\n')

            # show warning for uncorrected words
            if self.n_uncorrected > 0:
                showwarning('Uncorrected words', "Word list contains %d uncorrected words. "
                                                 "Their correct form has been set to @uncorrected@" % self.n_uncorrected)
        else:
            showwarning('Wrong filetype', 'Can only export *.txt and *.csv files.')

        # report
        self.instruct['text'] = 'Data exported to ' + f_export

    # ------------------------------------------------------------------------------------------------------------------
    #       DETECT COMPOUNDS
    # ------------------------------------------------------------------------------------------------------------------

    def identify_compounds(self):

        # create set of compounds
        COMPOUNDS = set()

        # create fast add function
        COMPOUNDS_add = COMPOUNDS.add

        # get lexicond of words
        WORDS = self.corr.WORDS

        # get words
        words = self.unknowns

        # index
        i = 0
        n = len(words)
        steps = [ind for ind in range(101)]

        # iterate through words
        for word in words:

            # update progress bar
            if 100 * (i / n) >= steps[0]:
                self.ind_text.set('Detecting compounds: ' + str(steps.pop(0))  + '%')
                self.progress.update()
                if not steps:
                    break

            # update index
            i += 1

            # find words with partial matches
            finds = [w for w in WORDS if w in word]

            # iterate over partial matches
            for find in finds:

                # remove previously matched part
                half = word.replace(find, '')

                # check if in lexicon
                if half in WORDS:
                    COMPOUNDS_add(word)
                    break

        # store result
        self.COMPOUNDS = COMPOUNDS

        # reset unknowns
        self.unknowns = [word for word in words if word not in COMPOUNDS] + [self.curr_word.get()]
        self.len_unknowns = len(self.unknowns)

        # reset index
        self.ind.set(self.ind.get() - 1)

        # return
        self.next()

    # ------------------------------------------------------------------------------------------------------------------
    #       HEADER WIDGET
    # ------------------------------------------------------------------------------------------------------------------

    def create_header_widgets(self):
        """
        Create header widgets containing the text of the current word, the progress line, and placeholders.  
        """

        # top border
        self.pl0 = Label(self, text = '', font = ('Helvetica',4)).grid(row = 0, column = 0)
        self.pl2 = Label(self, text = '', font = ('Helvetica',4)).grid(row = 0, column = 2)

        # progress
        self.progress = Label(self, textvariable = self.ind_text,
                            font=("Helvetica", 10))

        # word
        self.word = Label(self,
                          textvariable = self.curr_word,
                          font = ("Helvetica", 32, 'bold'),
                          pady = 12,
                          wraplength = 350)
        self.word.bind('<Button-1>', self.reset_entry)

    def reset_entry(self, event):
        """
        Create entry to listbox select.
        """

        # update entry default text to new word
        self.entry.delete(0, END)
        self.entry.insert(0, self.curr_word.get())
        self.entry.update_idletasks()

        # set focus back to entry
        self.entry.focus_set()


    def show_header(self):
        """
        Function puts header widgets on the grid
        """

        # word
        self.progress.grid(row = 1, column = 1, columnspan = 3)
        self.word.grid(row = 2, column = 1, columnspan = 3)

    # ------------------------------------------------------------------------------------------------------------------
    #       SUGGESTION WIDGET
    # ------------------------------------------------------------------------------------------------------------------

    def create_suggestion_widgets(self):
        """
        Create suggestion widgets.  
        """

        # suggestions 1
        self.sugg1 = Button(self,
                            textvariable = self.curr_sugg1,
                            font = ("Times New Roman", 16),
                            command = self.next,
                            width = 22)
        self.sugg1.bind('<Button-1>',self.accept_sugg1)

        # suggestions 2
        self.sugg2 = Button(self,
                            textvariable=self.curr_sugg2,
                            font=("Times New Roman", 16),
                            command=self.next,
                            width=22)
        self.sugg2.bind('<Button-1>',self.accept_sugg2)

        # suggestions 3
        self.sugg3 = Button(self,
                            textvariable=self.curr_sugg3,
                            font=("Times New Roman", 16),
                            command=self.next,
                            width=22)
        self.sugg3.bind('<Button-1>',self.accept_sugg3)

    # ------------------------------------------------------------------------------------------------------------------
    #       INPUT WIDGETS
    # ------------------------------------------------------------------------------------------------------------------

    def create_input_widgets(self):
        """
        Create input widgets comprised of free text entry and setNA.  
        """

        # self entry
        self.entry = Entry(self,
                           textvariable = self.entry_text,
                           justify = 'center',
                           font=("Times New Roman", 16),
                           width = 24)
        self.entry.bind('<Return>',self.accept_enter)

        # accept self entry
        self.accept = Button(self,
                             text = '+',
                             font=("Times New Roman", 16, 'bold'),
                             command = self.next,
                             width = 22)
        self.accept.bind('<Button-1>',self.accept_entry)

        # set NA
        self.setna = Button(self,
                            text = 'NA',
                            font=("Times New Roman", 16, 'bold'),
                            command = self.next,
                            width = 22)
        self.setna.bind('<Button-1>',self.accept_setna)

        # entry offset
        self.offset = Label(self, text='')

    def accept_enter(self, event):

        # accept entry
        self.accept_entry(event)

        # get next
        self.next(event)

    def show_input(self):
        """
        Show input widgets.
        """

        # free entry
        self.entry.grid(row = 3,  column = 1, padx = 2)
        self.accept.grid(row = 4, column = 1, padx = 2)
        self.setna.grid(row = 5,  column = 1, padx = 2)

    # ------------------------------------------------------------------------------------------------------------------
    #       PLACEHOLDER WIDGETS
    # ------------------------------------------------------------------------------------------------------------------

    def create_placeholder_widgets(self):
        """
        Create placeholder widgets.
        """

        # place holders
        self.ph1 = Label(self, text=' ', font = (16), pady = 4)
        self.ph2 = Label(self, text=' ', font = (16), pady = 4)
        self.ph3 = Label(self, text=' ', font = (16), pady = 4)

    # ------------------------------------------------------------------------------------------------------------------
    #       LISTBOX WIDGET
    # ------------------------------------------------------------------------------------------------------------------

    def create_listbox_widget(self):
        """
        Create listbox widget. Listbox shows dictionary.
        """

        # create dictionary listbox
        self.listbox = Listbox(self,
                            borderwidth = 0,
                            height = 10,
                            width = 42,
                            activestyle = 'none',
                            font = ('Times New Roman',16))
        self.listbox.bind('<<ListboxSelect>>', self.change_entry)

        # self entry
        self.search = Entry(self,
                            textvariable = self.search_text,
                            justify = 'center',
                            font=("Times New Roman", 16),
                            width = 24)
        self.search.bind('<KeyRelease>', self.search_listbox)

        # remove
        self.remove = Button(self,
                             text = '-',
                             font=("Times New Roman", 16, 'bold'),
                             command = self.remove_entry,
                             width=22)

    def change_entry(self, event):
        """
        Change entry to listbox select.
        """

        # get active entry
        index = event.widget.curselection()[0]
        entry = event.widget.get(index)

        # update entry default text to new word
        self.entry.delete(0, END)
        self.entry.insert(0, entry.strip().split(' ' + u'\u2192' + ' ')[1])
        self.entry.update()

        # set focus back to entry
        self.entry.focus_set()

    def update_listbox(self):
        """
        Create listbox widget. Listbox shows dictionary.
        """

        # remove everything
        self.listbox.delete(0, END)

        # sort dictionary by index
        sorted_dictionary = sorted(self.dictionary.iteritems(), key=lambda (k,v): v[1])

        # iterate through dictionary sorted by
        for key, value in sorted_dictionary:

            # create entry string
            string = ' ' + key + ' ' + u'\u2192' + ' ' + value[0]

            # insert entry string
            self.listbox.insert(0, string)

        # redraw listbox
        self.listbox.update_idletasks()

    def search_listbox(self, event):
        """
        Create listbox widget. Listbox shows dictionary.
        """

        # remove everything
        self.listbox.delete(0, END)

        # setup regex
        r = re.compile(self.search_text.get())

        # sort dictionary by index
        sorted_dictionary = sorted(self.dictionary.iteritems(), key=lambda (k,v): v[1])

        # iterate over sorted dictionary
        for key, value in sorted_dictionary:

            # check if regex is true
            if (r.search(key) is not None) | (r.search(value[0]) is not None):

                # create entry string
                string = ' ' + key + ' ' + u'\u2192' + ' ' + value[0]

                # insert entry string
                self.listbox.insert(0, string)

        # redraw listbox
        self.listbox.update_idletasks()

    def addto_listbox(self, key, value):
        """
        Add item to listbox.
        """

        # create entry string
        string = ' ' + key + ' ' + u'\u2192' + ' ' + value

        # insert entry string
        self.listbox.insert(0, string)

        # redraw listbox
        self.listbox.update_idletasks()

    def remove_entry(self):
        """
        Remove item from listbox and add to unknowns.
        """

        # check if anything is selected
        if self.listbox.curselection() is not ():

            # get entry pair
            item = self.listbox.get(ACTIVE).strip().split(' ' + u'\u2192' + ' ')[0]

            # remove item from dictionary
            del self.dictionary[item]

            # update litsbox using reduced dictionary
            self.update_listbox()

            # add word to front of unknowns
            self.unknowns = [item, self.curr_word.get()] + self.unknowns

            # set index back
            self.ind.set(self.ind.get() - 2)

            # next item, which is removed item
            self.next()

    def show_listbox(self):
        """
        Put listbox and the search and remove fields on the grid.
        """

        # separator
        Label(self, text=' ', font=2).grid(row = 6, column = 1)
        Label(self, text=' ', font=2).grid(row = 6, column = 2)

        # put listbox on the grid
        self.listbox.grid(row = 7, column = 1, rowspan = 10,
                          columnspan = 2,
                          pady = 5,
                          sticky = W)

        # put remove button on the grid
        self.remove.grid(row=17, column=1, padx = 2)

        # put seach field on the grid
        self.search.grid(row=17, column=2, padx = 2)


    # ------------------------------------------------------------------------------------------------------------------
    #       CREATE & DELETE WIDGET WRAPPERS
    # ------------------------------------------------------------------------------------------------------------------

    def create_widgets(self):
        """
        Calls all widget creators.
        """

        self.create_header_widgets()
        self.create_suggestion_widgets()
        self.create_input_widgets()
        self.create_placeholder_widgets()
        self.create_listbox_widget()

    def onlykeep_listbox(self):
        """
        Destroy all but listbox.
        """

        self.word.grid_remove()
        self.progress.grid_remove()
        self.sugg1.grid_remove()
        self.sugg2.grid_remove()
        self.sugg3.grid_remove()
        self.ph1.grid_remove()
        self.ph2.grid_remove()
        self.ph3.grid_remove()
        self.entry.grid_remove()
        self.accept.grid_remove()
        self.setna.grid_remove()
        self.listbox.grid_remove()
        self.search.grid_remove()
        self.remove.grid_remove()

    # ------------------------------------------------------------------------------------------------------------------
    #       RECORDERS
    # ------------------------------------------------------------------------------------------------------------------

    def accept_sugg1(self, event):
        """ Accept suggestions 1 """

        # add to dictionary
        self.dictionary[self.curr_word.get()] = [self.sugg1.cget('text'), len(self.dictionary) + 1]

        # add to listbox
        self.addto_listbox(self.curr_word.get(),self.sugg1.cget('text'))

        # add to accepts
        self.accepts.add(self.sugg1.cget('text'))

    def accept_sugg2(self, event):
        """ Accept suggestions 2 """

        # add to dictionary
        self.dictionary[self.curr_word.get()] = [self.sugg2.cget('text'), len(self.dictionary) + 1]

        # add to listbox
        self.addto_listbox(self.curr_word.get(),self.sugg2.cget('text'))

        # add to accepts
        self.accepts.add(self.sugg2.cget('text'))

    def accept_sugg3(self, event):
        """ Accept suggestions 3 """

        # add to dictionary
        self.dictionary[self.curr_word.get()] = [self.sugg3.cget('text'), len(self.dictionary) + 1]

        # add to listbox
        self.addto_listbox(self.curr_word.get(),self.sugg3.cget('text'))

        # add to accepts
        self.accepts.add(self.sugg3.cget('text'))

    def accept_entry(self, event):
        """ Accept entry """

        # add to dictionary
        self.dictionary[self.curr_word.get()] = [self.entry.get(), len(self.dictionary) + 1]

        # add to listbox
        self.addto_listbox(self.curr_word.get(),self.entry.get())

        # add to accepts
        self.accepts.add(self.entry.get())

    def accept_setna(self, event):
        """ Set NA """

        # add to dictionary
        self.dictionary[self.curr_word.get()] = ['@NA@', len(self.dictionary) + 1]

        # add to listbox
        self.addto_listbox(self.curr_word.get(),'@NA@')

    # ------------------------------------------------------------------------------------------------------------------
    #       NEXT ITEM
    # ------------------------------------------------------------------------------------------------------------------

    def next(self, event = None):
        '''main player. controls iteration through word list.'''

        # create empty suggestions
        suggestions = None
        word = None

        # iterate through words as long found in dictionary and words remain
        while len(self.unknowns) > 0:

            # increment index
            self.ind.set(self.ind.get() + 1)

            # collect word next word
            word = unicode(self.unknowns.pop(0))

            # identify suggestions
            suggestions = self.corr.word(word)

            if word not in self.dictionary.keys() and word not in self.accepts:
                break

        # update index text
        self.ind_text.set('Word ' + str(self.ind.get()) + ' of ' + str(self.len_unknowns))

        # set new word
        if word is not None:

            # set new word
            self.curr_word.set(word)

            # update entry default text to new word
            self.entry.delete(0, END)
            self.entry.insert(0, word)

        else:

            # destroy header
            self.onlykeep_listbox()

            # add new info field
            self.instruct['text'] = 'No more words.'
            self.instruct.grid()

        # check if suggestions exist
        if suggestions is not None:

            # fill first suggestion and plot suggestion widget and placeholders
            if len(suggestions) > 0:
                self.ph1.grid_remove()
                self.sugg1.grid(row = 3, column = 2, padx = 2)
                self.curr_sugg1.set(suggestions[0])
            else:
                self.sugg1.grid_remove()
                self.ph1.grid(row = 3, column = 2)
                self.update_idletasks()

            # fill second suggestion and plot suggestion widget and placeholders
            if len(suggestions) > 1:
                self.ph2.grid_remove()
                self.sugg2.grid(row = 4, column = 2, padx = 2)
                self.curr_sugg2.set(suggestions[1])
            else:
                self.sugg2.grid_remove()
                self.ph2.grid(row = 4, column = 2)
                self.update_idletasks()

            # fill third suggestion and plot suggestion widget and placeholders
            if len(suggestions) > 2:
                self.ph3.grid_remove()
                self.sugg3.grid(row = 5, column = 2, padx = 2)
                self.curr_sugg3.set(suggestions[2])
            else:
                self.sugg3.grid_remove()
                self.ph3.grid(row = 5, column = 2)
                self.update_idletasks()

        # clear listbox selection
        self.listbox.selection_clear(0, END)

        # move listbox focus to last items
        self.listbox.see(0)

        # move focus to entry
        #self.focus_force()
        self.entry.focus_set()

        # self auto save
        if self.ind.get() % 10 == 0:
            self.auto_save()

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

# start GUI
root = Tk()
root.title('Spellchecker')
root.geometry('500x480')

# give weight to left column
root.grid_columnconfigure(0, weight = 1)

# create app
app = Application(root)

# run
root.mainloop()


