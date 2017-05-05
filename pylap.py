from Tkinter import *
from correct import correct
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import showwarning
from nltk import stem
import sys, re, os, pickle, nltk, time, random

class Application(Frame):
    ''' A GUI application with three buttons.'''

    def __init__(self, parent):
        ''' Initializes the Frame'''

        print os.getcwd()

        # init
        Frame.__init__(self, parent)
        self.grid()

        # constants
        self.path = os.path.realpath(__file__).replace('pylap.py','')
        self.autosave_path = self.path + '_autosave/'

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

        # create a toplevel menu
        parent.title("spellchecker")
        menubar = Menu(parent)
        parent.configure(menu=menubar)

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

        # create settings menu
        settings_menu = Menu(menubar)
        language_menue = Menu(settings_menu)
        seperator_menue = Menu(settings_menu)
        language_menue.add_radiobutton(label="English", variable = self.language)
        language_menue.add_radiobutton(label="German", variable = self.language)
        settings_menu.add_cascade(label="Language", menu=language_menue)
        seperator_menue.add_radiobutton(label="space", variable = self.separator)
        seperator_menue.add_radiobutton(label="tab", variable = self.separator)
        seperator_menue.add_radiobutton(label="comma", variable = self.separator)
        seperator_menue.add_radiobutton(label="semicolon", variable = self.separator)
        settings_menu.add_cascade(label="Separator", menu=seperator_menue)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # create export menu
        file_menu = Menu(menubar)
        export_menu = Menu(file_menu)
        export_menu.add_command(label = "Export", command = self.export_corrections)
        export_menu.add_command(label = "Export and stem", command = self.export_corrections)
        #export_menu.bind()
        menubar.add_cascade(label = "Export", menu = export_menu)

        # entry instruction
        self.instruct = Label(text = 'Please load word list or project', font = ('Times New Roman', 16, 'italic'))
        self.instruct.grid(column = 0, columnspan = 1, row = 4)

        # create widgets
        self.create_widgets()

    def init_wordprocessers(self):
        if self.language.get() == 'English':
            self.stemmer = stem.snowball.EnglishStemmer
            self.corr = correct('en')
            return 'en'
        else:
            self.stemmer = stem.snowball.GermanStemmer
            self.corr = correct('de')
            return 'de'

    # get separator
    def get_separator(self):
        if self.separator.get() == 'space':
            return ' '
        elif self.separator.get() == 'tab':
            return '\t'
        elif self.separator.get() == 'comma':
            return ','
        else:
            return ';'

    def open_wordlist(self):

        # destroy instruct
        self.instruct.destroy()

        # initialize word processors
        self.init_wordprocessers()

        # initialize dictionary (if not loaded)
        if not hasattr(self,'dictionary'):
            self.dictionary = dict()

        # get word list
        f_words = askopenfilename()
        self.words = open(f_words, 'rb').read().lower().replace('\n',self.get_separator())
        self.words = self.words.split(self.get_separator())
        self.words = [word.strip() for word in self.words]
        self.unknowns = self.corr.unknown(self.words)
        self.len_unknowns = len(self.unknowns)

        # show widgets
        self.show_word()
        self.show_dict()

        # find suggestions
        self.next()

    def save_dictionary(self):

        # save dictionary
        if hasattr(self, 'dictionary'):
            f_dict = asksaveasfilename(defaultextension = '.pldict')
            pickle.dump(self.dictionary, open(f_dict, 'wb'), pickle.HIGHEST_PROTOCOL)
        else:
            showwarning('Dictionary missing', 'No dictionary found. Load word list or project.')

    def load_dictionary(self):

        # get dictionary
        f_dict = askopenfilename()
        if '.pldict' in f_dict:
            return None
        loaded_dict = pickle.load(open(f_dict,'rb'))

        # create or update dictionary
        if hasattr(self, 'dictionary'):

            # update index in loaded dictionary and append
            max_ind = len(self.dictionary)
            for key, value in loaded_dict.iteritems():
                loaded_dict[key] = [value[0], value[1] + max_ind]
            self.dictionary.update(loaded_dict)
        else:
            self.dictionary = loaded_dict

        # fill dictionary
        self.fill_listbox()

        # update intro text
        self.instruct['text'] = 'Dictionary loaded. Please load word list.'

    def import_dictionary(self):

        # init loaded dict
        imported_dict = dict()

        # get dictionary
        ind = 0
        f_dict = askopenfilename()
        for line in open(f_dict, 'rb'):
            ind += 1
            ntry = line.lower().replace('\n','').split(self.get_separator())
            print self.separator.get(), ntry
            imported_dict[ntry[0]] = [ntry[1], ind]

        # create or update dictionary
        if hasattr(self, 'dictionary'):

            # update index in loaded dictionary and append
            max_ind = len(self.dictionary)
            for key, value in imported_dict.iteritems():
                imported_dict[key] = [value[0], value[1] + max_ind]
            self.dictionary.update(imported_dict)
        else:
            self.dictionary = imported_dict

        # fill dictionary
        self.fill_listbox()

        # update intro text
        self.instruct['text'] = 'Dictionary imported. Please load word list.'

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

    def save_project(self):

        # create project
        self.create_project()

        # write
        f_proj = asksaveasfilename(defaultextension = '.plproject')
        pickle.dump(self.project, open(f_proj, 'wb'), pickle.HIGHEST_PROTOCOL)

    def open_autosave(self):

        # get project
        self.f_proj = askopenfilename(initialdir=self.autosave_path)

        # handle project
        self.handle_project()


    def open_project(self):

        # get project
        self.f_proj = askopenfilename()

        # handle project
        self.handle_project()


    def handle_project(self):

        # get project
        project = pickle.load(open(self.f_proj,'rb'))

        # extract i
        self.ind.set(project['ind'])

        # initialize word processors
        self.language.set(project['lang'])
        self.init_wordprocessers()

        # initialize dictionary
        if 'dict' in project.keys():
            self.dictionary = project['dict']
            self.fill_listbox()
            self.show_dict()

        # destroy instruct
        self.instruct.destroy()

        # extract words
        if 'words' in project.keys():
            self.unknowns = project['unknowns']
            self.words = project['words']
            self.len_unknowns = project['len']
            self.show_word()

            # find suggestions
            self.next()
        else:
            self.instruct['text'] = 'Word list missing. Please load word list.'


    def auto_save(self):
        '''do autosave of up to 10 files'''

        # clean up
        files = sorted(os.listdir(self.autosave_path))
        if len(files) == 10:
            os.remove(files[9])

        # create autosave file
        if not hasattr(self, 'autosave_f'):
            letters = list('abcdefghijklmnopqrstuvwxyz0123456789')
            random.shuffle(letters)
            self.code = ''.join(letters[:6])
            self.autosave_f = self.autosave_path + time.strftime("%d-%m-%y_%H:%M:%S") + \
                              self.code + '.plproject'

        # store
        self.create_project()

        # write
        pickle.dump(self.project, open(self.autosave_f, 'wb'), pickle.HIGHEST_PROTOCOL)

    def export_corrections(self):
        '''export the word list and corrections'''

        # get expo
        f_expo = asksaveasfilename(defaultextension='.txt')

        # get separator
        sep = self.get_separator()

        # get set of knowns
        known = self.corr.known(self.words)

        # write
        count = 0
        with open(f_expo, 'wb') as f_expo:
            for word in self.words:
                if word in known:
                    f_expo.write(word + sep + word + '\n')
                elif word in self.dictionary.keys():
                    f_expo.write(word + sep + self.dictionary[word][0] + '\n')
                else:
                    count += 1
                    f_expo.write(word + sep + '@uncorrected@')

        # show warning for uncorrected
        showwarning('Uncorrected words', "Word list contains %d uncorrected words. "
                                         "Words' corrections have been set to @uncorrected@" % count)

    def export_stem(self):
        '''export the word list and corrections'''

        # get expo
        f_expo = asksaveasfilename(defaultextension='.txt')

        # get separator
        sep = self.get_separator()

        # get set of knowns
        known = self.corr.known(self.words)

        # write
        count = 0
        with open(f_expo, 'wb') as f_expo:
            for word in self.words:
                if word in known:
                    f_expo.write(word + sep + word + sep + self.stem(word) + '\n')
                elif word in self.dictionary.keys():
                    cword = self.dictionary[word][0]
                    f_expo.write(word + sep + cword + sep + self.stem(cword) + '\n')
                else:
                    count += 1
                    f_expo.write(word + sep + '@uncorrected@' + sep + '@unstemmed@\n')

        # show warning for uncorrected
        showwarning('Uncorrected words', "Word list contains %d uncorrected words. "
                                         "Words' corrections have been set to @uncorrected@" % count)

    def create_widgets(self):
        '''create widgets'''

        # top border
        self.pl0 = Label(self, text = '', font = ('Helvetica',4)).grid(row = 0, column = 0)
        self.pl2 = Label(self, text = '', font = ('Helvetica',4)).grid(row = 0, column = 2)

        # header
        self.header = Label(self, textvariable = self.ind_text,
                            font=("Helvetica", 10))

        # word
        self.word = Label(self,
                          textvariable = self.curr_word,
                          font = ("Helvetica", 32, 'bold'),
                          pady = 12,
                          wraplength = 350)

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


        # self entry
        self.entry = Entry(self,
                           textvariable = self.entry_text,
                           justify = 'center',
                           font=("Times New Roman", 16),
                           width = 24)

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

        # place holders
        self.lab = Label(self, text='')
        self.ph1 = Label(self, text=' ', font = (16), pady = 4)
        self.ph2 = Label(self, text=' ', font = (16), pady = 4)
        self.ph3 = Label(self, text=' ', font = (16), pady = 4)

        # create history
        self.data = Listbox(self,
                            borderwidth = 0,
                            height = 7,
                            width = 22,
                            activestyle = 'none',
                            font = ('Times New Roman',16))


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

    def show_word(self):

        # word
        self.header.grid(row = 1, column = 1, columnspan = 3)
        self.word.grid(row = 2, column = 1, columnspan = 3)

        # free entry
        self.lab.grid(row=6, column=1)
        self.entry.grid(row = 7, column = 1)
        self.accept.grid(row = 8, column = 1)
        self.setna.grid(row = 9, column = 1)

    def show_dict(self):

        self.data.grid(row=3, column=3, rowspan = 5,
                       columnspan = 1,
                       padx = 20)
        self.search.grid(row = 8, column = 3)
        self.remove.grid(row = 9, column = 3)

    def accept_sugg1(self, event):
        self.dictionary[self.curr_word.get()] = [self.sugg1.cget('text'), len(self.dictionary) + 1]
        self.addto_listbox(self.curr_word.get(),self.sugg1.cget('text'))

    def accept_sugg2(self, event):
        self.dictionary[self.curr_word.get()] = [self.sugg2.cget('text'), len(self.dictionary) + 1]
        self.addto_listbox(self.curr_word.get(),self.sugg2.cget('text'))

    def accept_sugg3(self, event):
        self.dictionary[self.curr_word.get()] = [self.sugg3.cget('text'), len(self.dictionary) + 1]
        self.addto_listbox(self.curr_word.get(),self.sugg3.cget('text'))

    def accept_entry(self, event):
        self.dictionary[self.curr_word.get()] = [self.entry.get(), len(self.dictionary) + 1]
        self.addto_listbox(self.curr_word.get(),self.entry.get())

    def accept_setna(self, event):
        self.dictionary[self.curr_word.get()] = ['NA', len(self.dictionary) + 1]
        self.addto_listbox(self.curr_word.get(),'NA')

    def fill_listbox(self):
        self.data.delete(0, END)
        for key, value in sorted(self.dictionary.iteritems(), key=lambda (k,v): v[1]):
            string = key + u'\u2192' + value[0]
            self.data.insert(END, string)
            self.data.update()

    def search_listbox(self, event):
        self.data.delete(0, END)
        r = re.compile(self.search_text.get())
        for key, value in sorted(self.dictionary.iteritems(), key=lambda (k,v): v[1]):
            if (r.search(key) is not None) | (r.search(value[0]) is not None):
                string = key + u'\u2192' + value[0]
                self.data.insert(END, string)
        self.data.update()

    def addto_listbox(self, key, value):
        string = key + u'\u2192' + value
        self.data.insert(END, string)
        self.data.update()

    def remove_entry(self):
        '''removes entry from dictionary and adds to unknown list'''

        # remove entry
        if self.data.curselection() is not ():
            item = self.data.get(ACTIVE).split(u'\u2192')[0]
            del self.dictionary[item]
            self.fill_listbox()

            # add word to front
            self.unknowns = [item, self.curr_word.get()] + self.unknowns
            self.ind.set(self.ind.get() - 2)
            self.next()

    def next(self):
        '''main player. controls iteration through word list.'''

        # find word & suggestions
        sugg = []
        word = ''
        while((sugg == [] or word in self.dictionary.keys()) and
              len(self.unknowns) > 0):
            self.ind.set(self.ind.get() + 1)
            word = self.unknowns.pop(0)
            sugg = self.corr.word(word)

        # set i and word
        self.ind_text.set('Word ' + str(self.ind.get()) +
                          ' / ' + str(self.len_unknowns))
        self.curr_word.set(word)

        # fill suggestions
        if len(sugg) > 0:
            self.ph1.grid_remove()
            self.sugg1.grid(row = 3, column = 1)
            self.curr_sugg1.set(sugg[0])
        else:
            self.sugg1.grid_remove()
            self.ph1.grid(row = 3, column = 1)
        if len(sugg) > 1:
            self.ph2.grid_remove()
            self.sugg2.grid(row = 4, column = 1)
            self.curr_sugg2.set(sugg[1])
        else:
            self.sugg2.grid_remove()
            self.ph2.grid(row = 4, column = 1)
        if len(sugg) > 2:
            self.ph3.grid_remove()
            self.sugg3.grid(row = 5, column = 1)
            self.curr_sugg3.set(sugg[2])
        else:
            self.sugg3.grid_remove()
            self.ph3.grid(row = 5, column = 1)

        # clear entry
        self.entry.delete(0, END)
        self.entry.insert(0, word)

        # clear listbox selection
        self.data.selection_clear(0, END)

        # update header
        self.data.see("end")

        # move focus
        self.focus_force()

        # show End
        if word == '':
            self.curr_word.set('-FIN-')

        # self auto save
        self.auto_save()



# start GUI
root = Tk()
root.title('Spellchecker')
root.geometry('500x600')

# give weight to left column
root.grid_columnconfigure(0, weight = 1)

# create app
app = Application(root)

# run
root.mainloop()


