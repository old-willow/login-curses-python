#! /usr/bin/python
#coding:utf-8

import sys, os
import locale
import datetime
import curses
import re
import sqlite3 as sqlite


locale.setlocale(locale.LC_ALL, '')
#code = locale.getpreferredencoding()


class Window:
    '''Base class for windows.'''
    def __init__(self, fieldname, parentScreen): 
        self.parentHeight, self.parentWidth = parentScreen.getmaxyx() # Base window dimensions.
        self.parentYpos, self.parentXpos = parentScreen.getbegyx()    # Top right corner of window.


class WarningWindow(Window):
    '''This is a Warrning window:
        It pops-up if some of the fields are empty or
        some other error ocours.'''
    def __init__(self, fieldname, parentScreen):
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()
        fieldLen = len(fieldname)
       # height, width = screen.getmaxyx()
       # ypos, xpos = screen.getbegyx()
        self.height = 7
        self.width = 44
        self.ypos = ((self.parentHeight - self.height) / 2) + self.parentYpos
        self.xpos = ((self.parentWidth - self.width) / 2) + self.parentXpos

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
        self.win.keypad(1)
        self.win.attron(curses.color_pair(1))
        self.win.bkgd(' ', curses.color_pair(1))
        strHeader = ' Warning! '
        strOK =     ' OK '
        self.win.box()
        self.win.addstr(1, (self.width - 11) / 2,
                        strHeader, curses.A_REVERSE | curses.A_BOLD)
        self.win.addstr(5, (self.width - 4) / 2,
                        strOK, curses.A_REVERSE)
        self.win.attroff(curses.color_pair(1))
        self.win.refresh()

    def getch(self):
        while True:
            key = self.win.getch()
            if key == ord('\n'): # Since curses.KEY_ENTER don't work, this will
                break;

    def addstr(self, y, x, string):
        self.win.addstr(y, x, string)
        self.win.refresh()

    def flushinp(self):
        self.win.flushinp()

    def refresh(self):
        self.win.refresh()

    def destroy(self):
        self.win.touchwin()
        self.win.refresh()
        del self.win


class MenuWindow(Window):
    '''This is Menu Window for:
        choosing between Login or Register page'''
    def __init__(self, parentScreen):
        # Make it green
        #curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.noecho()
        curses.curs_set(0)
        curses.raw()
        #stdscrDim = stdscr.getmaxyx()
        self.height = 9
        self.width = 50
        self.ypos = (self.parentHeight - self.height) / 2
        self.xpos = (self.parentWidth - self.width) / 2

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        #self.win.attron(curses.color_pair(1))
        self.win.keypad(1)
        strHeader =   ' Welcome to My Application '
        strExplain =  'Press key in [] to enter:'
        strLogin =    '[L]      - Login'
        strRegester = '[R]      - Registration'
        strQuit =     '[CTRL-X] - Exit'
        self.win.box()
        self.win.addstr(1, (self.width-len(strHeader))/2,
                        strHeader, curses.A_REVERSE)
        self.win.addstr(3, (self.width-len(strExplain))/2,
                        strExplain, curses.A_BOLD)
        self.win.addstr(5, 5, strLogin, curses.A_NORMAL)
        self.win.addstr(6, 5, strRegester, curses.A_NORMAL)
        self.win.addstr(7, 5, strQuit, curses.A_NORMAL)
        self.win.refresh()

    def putwin(self, filename): # Not implemented yet!
        self.win.putwin(filename)

    def get_choice(self):
        while True:
            choice = self.win.getch()
            
            if choice == ord('l'):
                break
            elif choice == ord('r'):
                break
            else:
                kname = curses.keyname(choice)
                if kname == '^X':
                    return unicode(kname)

        return choice
        
    def destroy(self):
        self.win.touchwin()
        self.win.refresh()
        del self.win


class LoginForm(Window):
    def __init__(self, stdscr):
        '''Login window'''
        # This part is for cursor positions.
        self.STARTPOS = 14
        self.ENDPOS   = 15
        self.maxInput = self.STARTPOS + self.ENDPOS

        curses.curs_set(1)
        curses.noraw()
        #stdscrDim = stdscr.getmaxyx()
        self.height = 10
        self.width = 50
        self.ypos = (Window.height - self.height) / 2
        self.xpos = (Window.width - self.width) / 2

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        self.win.keypad(1)
        strHeader =   ' Welcome to Login Form '
        strUserName = 'User name:'
        strPassword = 'Password:'
        self.win.box()
        self.win.addstr(1, (self.width - len(strHeader)) / 2,
                        strHeader, curses.A_REVERSE)
        self.win.addstr(3, 2,
                        strUserName, curses.A_NORMAL)
        self.win.addstr(5, 2,
                        strPassword, curses.A_NORMAL)

        # Buttons
        self.win.addstr(8, 2, ' [CTRL-B] - Back ', curses.A_REVERSE)
        self.win.addstr(8, 30, ' [CTRL-L] - Login ', curses.A_REVERSE)
        self.win.refresh()
        stdscr.refresh() # If terminal window is resized, refresh the parent.
        
    # Wrapping functions
    def getch(self, flag, end):
        '''
        flag -> If True=We are in password field.
        end  -> Did we finished filling the form? True=Yes.
                This is needed after last field is populated.
        '''
        container = ''
        y, x = self.win.getyx()
        movingX = x
        rightX = self.STARTPOS

        while True:
            if end:
                curses.raw()
                curses.noecho()
                self.win.keypad(1)
                curses.curs_set(0)

                ch = self.win.getch()
                kname = curses.keyname(ch)
                if kname == '^L':
                    return kname

            elif not end:
                curses.raw()
                curses.noecho()
                self.win.keypad(1)

                ch = self.win.getch()
                kname = curses.keyname(ch)

                if ch == 2: # If user hits CTRL-B
                    container = ''
                    return 2

                elif kname == '^L':
                    return kname

                elif ch == curses.KEY_BACKSPACE: # Backspace
                    if rightX > self.STARTPOS: # If cursor is bigger then start position.
                        container = container[:-1] # Delete the last character.
                        y, x = self.win.getyx()
                        x -= 1                    # --+
                        rightX -= 1               #   |--> Keep track of pointers
                        movingX -= 1              # --+
                        self.win.addch(y, x, ' ') # Remove last char fom screen.
                        self.win.move(y, x)       # Move back the cursor
                        self.win.refresh()
                    else:
                        self.warning()

                elif ch == 9: # TAB ('^I') for Gnome-terminal
                    return ch

                elif ch == curses.KEY_BTAB: # SHIFT+TAB for Gnome-terminal
                    return ch

                elif ch == curses.KEY_HOME:
                    self.win.move(y, self.STARTPOS)
                    movingX = self.STARTPOS

                elif ch == curses.KEY_END:
                    self.win.move(y, self.STARTPOS + len(container))
                    movingX = self.STARTPOS + len(container)
                    x = self.STARTPOS + len(container)

                elif ch == 10:          # If user hits the enter,
                    if container != '': # if we have something in container and
                        return container
                    else:
                        return 10       # or we don't.

                elif ch == curses.KEY_LEFT:
                    y, x = self.win.getyx()
                    movingX = x # probably movingX has to be a static variable
                    if movingX > self.STARTPOS:
                        movingX -= 1 # Tracking the X position
                        self.win.move(y, movingX)
                    else:
                        self.win.move(y, self.STARTPOS)
                        self.warning()

                elif ch == curses.KEY_RIGHT:
                    y, x = self.win.getyx()
                    movingX = x
                    if movingX < self.maxInput and movingX < rightX:
                        movingX += 1 # Tracking the X position
                        self.win.move(y, movingX)
                    else:
                        if movingX == self.maxInput:
                            self.win.move(y, self.maxInput)
                            curses.beep()
                            curses.flash()
                        elif movingX == rightX:
                            self.win.move(y, rightX)
                            self.warning()

                elif ch in range(65, 91) or \
                     ch in range(97, 123) or \
                     ch in range(49, 58) or \
                     ch == ord('_'):

                    curses.noraw()

                    if not flag and movingX == rightX: # If we arn't in the password
                        if rightX < self.maxInput: # max right position
                            self.win.addch(ch) # field and no arrow key used yet.
                            container += chr(ch)
                            movingX += 1
                            rightX += 1
                        else:
                            self.warning()

                    # Creating illusion of input on screen...
                    elif not flag and movingX < rightX: # If we moved with arrow keys
                        if rightX < self.maxInput: # max right position
                            containerLeft = container[:movingX-self.STARTPOS]
                            containerRight = container[movingX-self.STARTPOS:]
                            container = containerLeft
                            container += chr(ch)
                            container += containerRight
                            movingX += 1
                            rightX += 1
                            self.win.addstr(y, self.STARTPOS, container)
                            self.win.move(y, movingX)
                            self.win.refresh()
                        else:
                            self.warning()

                    elif flag: # If we are in the password field
                        if rightX < self.maxInput: # max right position
                            curses.echo()
                            container += chr(ch)
                            self.win.addch(curses.ACS_DIAMOND)
                            movingX += 1
                            rightX += 1
                        else:
                            self.warning()


    def getstr(self):
        return self.win.getstr()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def getbegyx(self):
        return self.win.getbegyx()

    def move(self, y, x):
        self.win.move(y, x)

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def clrtoeol(self):
        self.win.clrtoeol()

    def box(self):
        self.win.box()

    def warning(self):
        curses.beep()
        curses.flash()

    def destroy(self):
        self.win.touchwin() # I use the above touchwin()
        self.win.refresh()
        del self.win


class RegisterForm:
    def __init__(self, stdscr):
        '''Registration window'''
        # This part is for cursor positions.
        self.STARTPOS = 21
        self.ENDPOS   = 30
        self.maxInput = self.STARTPOS + self.ENDPOS

        curses.curs_set(1)
        curses.noraw()
        stdscrDim = stdscr.getmaxyx()
        self.height = 22
        self.width = 55
        self.ypos = (stdscrDim[0] - self.height) / 2
        self.xpos = (stdscrDim[1] - self.width) / 2

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        self.win.keypad(1)
        strHeader =          ' Welcome to Registration Form '
        strGender =          'Gender:'
        strFirstName =       'First name:'
        strLastName =        'Last name:'
        strUserName =        'User name:'
        strEmail =           'E-mail:'
        strPassword =        'Password:'
        strConfirmPassword = 'Confirm password:'
        strDateOfBirth =     'Date of birth:'
        self.win.box()
        self.win.addstr(1, (self.width-len(strHeader))/2,
                        strHeader, curses.A_REVERSE)
        self.win.addstr(3, 2,
                        strGender, curses.A_NORMAL)
        self.win.addstr(5, 2,
                        strFirstName, curses.A_NORMAL)
        self.win.addstr(7, 2,
                        strLastName, curses.A_NORMAL)
        self.win.addstr(9, 2,
                        strUserName, curses.A_NORMAL)
        self.win.addstr(11, 2,
                        strEmail, curses.A_NORMAL)
        self.win.addstr(13, 2,
                        strPassword, curses.A_NORMAL)
        self.win.addstr(15, 2,
                        strConfirmPassword, curses.A_NORMAL)
        self.win.addstr(17, 2,
                        strDateOfBirth, curses.A_NORMAL)
        self.win.refresh()

        # Buttons
        self.win.addstr(20, 2, ' [CTRL-B] - Back ', curses.A_REVERSE)
        self.win.addstr(20, 32, ' [CTRL-R] - Register ', curses.A_REVERSE)
        self.win.refresh()
        stdscr.refresh() # If terminal window is resized, refresh the parent.

    # Wrapping functions
    def box(self):
        self.win.box()

    def getch(self, flag, end):
        container = ''
        y, x = self.win.getyx()
        movingX = x
        rightX = self.STARTPOS

        while True:
            if end:
                curses.raw()
                curses.noecho()
                self.win.keypad(1)
                curses.curs_set(0)

                ch = self.win.getch()
                kname = curses.keyname(ch)
                if kname == '^R':
                    return kname

            elif not end:
                curses.raw()
                curses.noecho()
                self.win.keypad(1)

                ch = self.win.getch()
                kname = curses.keyname(ch)

                if ch == 2: # If user hits CTRL-B
                    return 2

                elif kname == '^R':
                    return '^R'

                elif ch == curses.KEY_BACKSPACE: # Backspace
                    if rightX > self.STARTPOS: # If cursor is bigger then start position.
                        container = container[:-1] # Delete the last character.
                        y, x = self.win.getyx()
                        x -= 1                    # --+
                        rightX -= 1               #   |--> Keep track of pointers
                        movingX -= 1              # --+
                        self.win.addch(y, x, ' ') # Remove last char from screen.
                        self.win.move(y, x)       # Move back the cursor
                        self.win.refresh()
                    else:
                        self.warning()

                elif ch == 127: # DEL
                    pass

                elif ch == 9: # TAB ('^I') for Gnome-terminal
                    return ch

                elif ch == curses.KEY_BTAB: # SHIFT+TAB for Gnome-terminal
                    return ch

                elif ch == curses.KEY_HOME:
                    self.win.move(y, self.STARTPOS)
                    movingX = self.STARTPOS

                elif ch == curses.KEY_END:
                    x = self.STARTPOS + len(container)
                    self.win.move(y, self.STARTPOS + len(container))
                    movingX = x
                    rightX = x

                elif ch == 10:          # If user hits the enter,
                    if container != '': # if we have something in container and
                        return container
                    else:
                        return 10       # or we don't.

                elif ch == curses.KEY_LEFT:
                    y, x = self.win.getyx()
                    movingX = x # probably movingX has to be a static variable
                    if movingX > self.STARTPOS:
                        movingX -= 1 # Tracking the X position
                        self.win.move(y, movingX)
                    else:
                        self.win.move(y, self.STARTPOS)
                        self.warning()

                elif ch == curses.KEY_RIGHT:
                    y, x = self.win.getyx()
                    movingX = x
                    if movingX < self.maxInput and movingX < rightX:
                        movingX += 1 # Tracking the X position
                        self.win.move(y, movingX)
                    else:
                        if movingX == self.maxInput:
                            self.win.move(y, self.maxInput)
                            curses.beep()
                            curses.flash()
                        elif movingX == rightX:
                            self.win.move(y, rightX)
                            self.warning()

                elif ch in range(65, 91) or \
                     ch in range(97, 123) or \
                     ch in range(48, 58) or \
                     ch == ord('_') or \
                     ch == ord('-') or \
                     ch == ord('.') or \
                     ch == ord('@'):

                    curses.noraw()

                    if not flag and movingX == rightX: # If we aren't in the password
                        if rightX < self.maxInput: # max right position
                            self.win.addch(ch)     # field and no arrow key used yet.
                            container += chr(ch)
                            movingX += 1
                            rightX += 1
                        else:
                            self.warning()

                    elif not flag and movingX < rightX: # If we moved with arrow keys
                        if rightX < self.maxInput: # max right position
                            containerLeft = container[:movingX-self.STARTPOS]
                            containerRight = container[movingX-self.STARTPOS:]
                            container = containerLeft
                            container += chr(ch)
                            container += containerRight
                            movingX += 1
                            rightX += 1
                            self.win.addstr(y, self.STARTPOS, container)
                            self.win.move(y, movingX)
                            self.win.refresh()
                        else:
                            self.warning()

                    elif flag: # If we are in the password field
                        if rightX < self.maxInput: # max right position
                            curses.echo()
                            container += chr(ch)
                            self.win.addch(curses.ACS_DIAMOND)
                            movingX += 1
                            rightX += 1
                        else:
                            self.warning()


    def getstr(self):
        return self.win.getstr()

    def getmaxyx(self):
        return self.win.getmaxyx()

    def getbegyx(self):
        return self.win.getbegyx()

    def move(self, y, x):
        self.win.move(y, x)

    def clrtoeol(self):
        self.win.clrtoeol()

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def warning(self):
        curses.beep()
        curses.flash()

    def destroy(self):
        self.touchwin() # I use the above touchwin()
        self.win.refresh()
        del self.win


class LoggedUserWindow:
    def __init__(self, stdscr):
        # self.CURSPOS = ((6, 4), (7, 4), (8, 4), (11, 36))
        # self.STARTPOS and self.ENDPOS is only for last input field.
        self.STARTPOS = 40
        self.ENDPOS   = 25
        self.maxInput = self.STARTPOS + self.ENDPOS

        curses.curs_set(1)
        curses.noraw()
        curses.cbreak()
        
        stdscrDim = stdscr.getmaxyx()
        self.height = 20
        self.width = 70
        self.ypos = (stdscrDim[0] - self.height) / 2
        self.xpos = (stdscrDim[1] - self.width) / 2

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.win.bkgd(' ', curses.color_pair(4))


        strHeader1 = ' You Are Logged as a User '
        strHeader2 = 'Choose from options below:'
        strListAll = 'Mark with SPACE wich table to search.'
        #strKJI     = u'[ ] Kiemelt jelent\u030b\u006Fs\u0301\u0065g\u030B\u0075  int\u0301\u0065zm\u0301\u0065nyek'
        strKJI     = '[ ] Kiemelt jelentőségű intézmények'
        strEM      = '[ ] e-magyar'
        strKJII    = '[ ] Kiemelt jelentőségű ifjúsági intézmények'
        strSearch  = 'Search in marked tables for subject:'
        strList    = '[CTRL-L] List all from selected categories'
        strBack    = '[CTRL-B] Back to main window'
        strExit    = '[CTRL-X] - Exit'
        
        self.win.attron(curses.color_pair(2))
        self.win.box()
        self.win.addstr(1, (self.width - len(strHeader1)) / 2,
                        strHeader1, curses.A_REVERSE | curses.A_BOLD)
        self.win.addstr(2, (self.width - len(strHeader2)) / 2,
                        strHeader2, curses.A_NORMAL)
        self.win.addstr(4, 3, strListAll, curses.A_UNDERLINE)
        self.win.attroff(curses.color_pair(2))
        self.win.refresh()
        
        self.win.attron(curses.color_pair(3))
        self.win.addstr(6, 3, strKJI, curses.A_NORMAL)
        self.win.addstr(7, 3, strEM, curses.A_NORMAL)
        self.win.addstr(8, 3, strKJII, curses.A_NORMAL)
        self.win.addstr(11, 3, strSearch, curses.A_NORMAL)
        self.win.attroff(curses.color_pair(3))
        self.win.refresh()

        self.win.attron(curses.color_pair(4))
        self.win.addstr(16, 3, strList, curses.A_NORMAL)
        self.win.addstr(17, 3, strBack, curses.A_NORMAL)
        self.win.addstr(18, 3, strExit, curses.A_NORMAL)
        self.win.attroff(curses.color_pair(4))
        self.win.refresh()
        stdscr.refresh() # If terminal window is resized, refresh the parent.
        self.win.move(6, 4)

    def getch(self):
        def add_next_byte():
            '''Local function:
                for checking next byte if the input was
                different then ascii char set.'''
            c = self.win.getch()
            if 128 <= ch <= 191:
                return ch
            else:
                raise UnicodeError

        # Is the position X-ed (checked)?
        posy1 = False
        posy2 = False
        posy3 = False
        # Invoking needed variables for cursor position
        movingX = self.STARTPOS
        rightX = self.STARTPOS
        container = ''

        while True:
            curses.raw()
            self.win.keypad(1)
            ch = self.win.getch()
            kname = curses.keyname(ch)
            y, x = self.win.getyx()

            if kname == '^X':
                return '^X'

            elif ch == curses.KEY_UP:
                y, x = self.win.getyx()
                if y == 6:
                    if not posy1 and not posy2 and not posy3:
                        self.win.move(8, 4)
                    else:
                        self.win.move(11, 40)
                elif y == 8:
                    self.win.move(7, 4)
                elif y == 7:
                    self.win.move(6, 4)
                elif y == 11:
                    self.win.move(8, 4)

            elif ch == curses.KEY_DOWN:
                y, x = self.win.getyx()
                if y == 6:
                    self.win.move(7, 4)
                elif y == 7:
                    self.win.move(8, 4)
                elif y == 8:
                    if not posy1 and not posy2 and not posy3:
                        self.win.move(6, 4)
                    else:
                        self.win.move(11, 40)
                elif y == 11: 
                    self.win.move(6, 4)

            elif ch == curses.KEY_LEFT:
                y, x = self.win.getyx()
                if y == 11:
                    movingX = x # probably movingX has to be a static variable
                    if movingX > self.STARTPOS:
                        movingX -= 1 # Tracking the X position
                        self.win.move(y, movingX)
                    else:
                        self.win.move(y, self.STARTPOS)
                        self.warning()

            elif ch == curses.KEY_RIGHT:
                    y, x = self.win.getyx()
                    if y == 11:
                        movingX = x
                        if movingX < self.maxInput and movingX < rightX:
                            movingX += 1 # Tracking the X position
                            self.win.move(y, movingX)
                        else:
                            if movingX == self.maxInput:
                                self.win.move(y, self.maxInput)
                                curses.beep()
                                curses.flash()
                            elif movingX == rightX:
                                self.win.move(y, rightX)
                                self.warning()

            elif ch == curses.KEY_BACKSPACE:
                y, x = self.win.getyx()
                if y == 11:
                    if rightX > self.STARTPOS:
                        container = container[:-1]
                        x -= 1
                        rightX -= 1
                        movingX -= 1
                        self.win.addch(y, x, ' ')
                        self.win.move(y, x)
                        self.win.refresh()
                    else:
                        self.warning()

            elif ch == 127: # DEL
                pass

            elif ch == 10:
                pass

            elif ch == 9: # TAB ('^I') for Gnome-terminal
                pass

            elif ch == 2:
                return 2

            elif ch == curses.KEY_HOME:
                if y == 11:
                    self.win.move(y, self.STARTPOS)
                    movingX = self.STARTPOS

            elif ch == curses.KEY_END:
                if y == 11:
                    x = self.STARTPOS + len(container)
                    self.win.move(y, x)
                    movingX = x
                    rightX = x
                
            elif ch == 32: # Space character
                cursorPosition = self.win.getyx()
                if cursorPosition[0] != 11: # if y is different then 11.
                    curses.noraw()
                    if cursorPosition == (6, 4):
                        if not posy1:
                            self.win.addch('X')
                            self.win.move(6, 4)
                            self.win.refresh()
                            posy1 = True
                        elif posy1:
                            self.win.addch(' ')
                            self.win.move(6, 4)
                            self.win.refresh()
                            posy1 = False
                    elif cursorPosition == (7, 4):
                        if not posy2:
                            self.win.addch('X')
                            self.win.move(7, 4)
                            self.win.refresh()
                            posy2 = True
                        elif posy2:
                            self.win.addch(' ')
                            self.win.move(7, 4)
                            self.win.refresh()
                            posy2 = False
                    elif cursorPosition == (8, 4):
                        if not posy3:
                            self.win.addch('X')
                            self.win.move(8, 4)
                            self.win.refresh()
                            posy3 = True
                        elif posy3:
                            self.win.addch(' ')
                            self.win.move(8, 4)
                            self.win.refresh()
                            posy3 = False

            elif y == 11 and \
                 (ch in range(48, 58) or \
                  ch in range(65, 91) or \
                  ch in range(97, 123) or \
                  ch in range(127, 245) or \
                  ch == ord('_') or \
                  ch == ord('-') or \
                  ch == ord('.') or \
                  ch == ord('@')):

                curses.noraw()

                if movingX == rightX:
                    if rightX < self.maxInput:
                        if ch <= 127: # 1 byte
                            container += chr(ch)
                        elif 194 <= ch <= 223: # 2 byte
                            container += chr(ch)
                            container += chr(add_next_byte())
                        elif 224 <= ch <= 239: # 3 byte
                            container += chr(ch)
                            container += chr(add_next_byte())
                            container += chr(add_next_byte())
                        elif 240 <= ch <= 244: # 4 byte
                            container += chr(ch)
                            container += chr(add_next_byte())
                            container += chr(add_next_byte())
                            container += chr(add_next_byte())
                        self.win.addch(ch)
                        movingX += 1
                        rightX += 1
                        self.win.move(y, rightX)
                    else:
                        self.warning()

                elif movingX < rightX:
                    if rightX < self.maxInput:
                        containerLeft = container[:movingX-self.STARTPOS]
                        containerRight = container[movingX-self.STARTPOS:]
                        container = containerLeft
                        container += chr(ch)
                        container += containerRight
                        movingX += 1
                        rightX += 1
                        self.win.addstr(y, self.STARTPOS, container)
                        self.win.move(y, movingX)
                        self.win.refresh()
                    else:
                        self.warning
            else:
                pass

    def touchwin(self):
        self.win.touchwin()

    def warning(self):
        curses.beep()
        curses.flash()

    def destroy(self):
        self.touchwin() # I use the above touchwin()
        self.win.refresh()
        del self.win


class LoggedAdminWindow:
    def __init__(self, stdscr):
        curses.curs_set(1)
        curses.noraw()
        
        stdscrDim = stdscr.getmaxyx()
        self.height = 20
        self.width = 50
        self.ypos = (stdscrDim[0] - self.height) / 2
        self.xpos = (stdscrDim[1] - self.width) / 2

        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)

        curses.raw()
        self.win.keypad(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)


        strHeader1 = ' You Are Logged as Administrator '
        strHeader2 = 'Choose from options below:'
        strCreateUser =     '[1] Create User (Go to register form)'
        strDeleteUser =     '[2] Delete User'
        strAddTable =       '[3] Add Category'
        strAddContact =     '[4] Add Contact'
        strEditContact =    '[5] Edit Contact'
        strDelContact =     '[6] Delete Contact'
        strListByCategory = '[7] List Contacts by Category'
        strListContact =    '[8] List All Contacts'
        strAdd =            '[CTRL-B] Back to main menu (Logout)'

        self.win.bkgd(' ', curses.color_pair(3))
        self.win.attron(curses.color_pair(2))

        self.win.addstr(1, (self.width-len(strHeader1)) / 2,
                        strHeader1, curses.A_BOLD)
        self.win.addstr(2, (self.width-len(strHeader2)) / 2,
                       strHeader2, curses.A_NORMAL)
        self.win.addstr(4, 3, strCreateUser, curses.A_NORMAL)
        self.win.addstr(5, 3, strDeleteUser, curses.A_NORMAL)
        self.win.addstr(6, 3, strAddTable, curses.A_NORMAL)
        self.win.addstr(7, 3, strAddContact, curses.A_NORMAL)
        self.win.addstr(8, 3, strEditContact, curses.A_NORMAL)
        self.win.addstr(9, 3, strDelContact, curses.A_NORMAL)
        self.win.addstr(10, 3, strListByCategory, curses.A_NORMAL)
        self.win.addstr(11, 3, strListContact, curses.A_NORMAL)
        self.win.addstr(18, 3, strAdd, curses.A_NORMAL)

        self.win.box()
        self.win.attroff(curses.color_pair(2))
        self.win.refresh()

    def getch(self):
        self.win.getch()

    def touchwin(self):
        self.win.touchwin()

    def warning(self):
        curses.beep()
        curses.flash()

    def destroy(self):
        self.touchwin() # I use the above touchwin()
        self.win.refresh()
        del self.win


class User:
    '''
    Construct the user data.
    '''
    def __init__(self):
        self.gender = ['', 'Gender']
        self.firstname = ['', 'Firstname']
        self.lastname = ['', 'Lastname']
        self.username = ['', 'Username']
        self.email = ['', 'Email']
        self.password = ['', 'Password']
        self.confirmPassword = ['', 'Confirm password']
        self.oldPassword = ['', 'oldPassword']
        self.dob = ['', 'Date of Birth']
        self.regDate = ['', 'regDate']
        self.lastLogDate = ['', 'lastLogDate']


if __name__ == '__main__':
    main()
