#! /usr/bin/python
#coding:utf-8

# For some reason utf-8 and/or unicode
# is not working on Python 2.7.2, maybe my bad compilig on Debian!

import sys, os
import locale
import datetime
import curses
import re
import sqlite3 as sqlite

from loginclasses import * # my class!


#locale.setlocale(locale.LC_ALL, '')

DB = 'login_register' # Database file name

def input_processing(window, person, fieldName, flag, y):
    '''input_processing():
        Should take user input and check it if it is a valid
        window    -> window (login either register)
        fieldName -> ...
        flag      -> if password curses.noecho() else curses.echo()
        y         -> window.move(y, positionX), for cursor position.
    '''
    if isinstance(window, LoginForm):
        positionX = window.STARTPOS
    elif isinstance(window, RegisterForm):
        positionX = window.STARTPOS

    if flag: # Question: is this a password field? If yes then noecho!
        curses.noecho()
    elif not flag:
        curses.echo()
    window.move(y, positionX)

    while True:
        value = window.getch(flag, False) # Container for field input

        if value == 2:  # CTRL-B was pressed
            # Process the actual window destroying
            return value

        elif value == 10: # If no string in value container
            if fieldName != person.dob[1]:
                warning_processing(window, fieldName, flag, y, positionX)
            else: # if this is a 'dob' field in registration form.
                curses.curs_set(0)
                return 10

        elif value == '^L' and isinstance(window, LoginForm):
            if login(person): # Successfully loged in!
                break
            else: # If user hits '^L' before filling out the form.
                warning_processing(window, 'Can\'t login. Fill the form!', \
                                   flag, y, positionX)

        elif value == '^R' and isinstance(window, RegisterForm):
            if register(person): # Successfully registered!
                break
            else: # If user hits '^R' before filling out the form.
                warning_processing(window, 'Can\'t register. Fill the form!', \
                                   flag, y, positionX)

        elif value == 9 or value == curses.KEY_BTAB:
            tabbing()

        elif type(value) is type(''): # If value is of type string
            return value


def check_user(window, username, y, x):
    '''Checks if there is already a user with username in db
    '''
    conn = sqlite.connect(DB)
    curs = conn.cursor()

    query = 'SELECT username FROM users WHERE username=?'

    curs.execute(query, (username,))
    conn.commit()
    un = curs.fetchall()

    if isinstance(window, LoginForm):
        if un != []:
            conn.close() # Close db
            return True
        else:            # Stop! No such user! Can't continue.
            conn.close() # Close db
            warning = 'No user with \'' + username + u'\' name.'
            warning_processing(window, warning, False, y, x)
            return False

    elif isinstance(window, RegisterForm):
        if un == []:     # There is no username in db, we can continue
            conn.close() # Close db
            return True
        else:            # Stop there is already username!
            conn.close() # Close db
            warning = 'Already a user with \'' + username + u'\' user name.'
            warning_processing(window, warning, False, y, x)
            return False


def check_passwords(window, passw, confPassw, y, x):
    '''check_passwords():
        Check if passwords matches in Register window
        window    -> which window: login or register
        passw     -> login window: the actual password;
                  -> register window: the first password
        confPassw -> login window: None;
                  -> register window: second attempt
        y, x      -> for cursor position after back from warning if necesarry
    '''
    if isinstance(window, RegisterForm):
        if passw == confPassw:
            return True
        else:
            warning_processing(window, 'Passwords', True, 13, window.STARTPOS)
            return False

    elif isinstance(window, LoginForm):
        conn = sqlite.connect(DB)
        curs = conn.cursor()

        query = 'SELECT password FROM users WHERE password=?'

        curs.execute(query, (passw,))
        conn.commit()
        ps = curs.fetchall()

        if ps != []:
            conn.close() # Close db. We are in! Yeah!!!
            return True

        else:
            conn.close()
            warning = 'Wrong password! Try again.'
            warning_processing(window, warning, True, y, x)
            return False


def validate_email(window, person, y, x):
    '''validate_email():
        window -> parent window
        string -> the actual email address
        y, x   -> in case email address wasn't valid, put back the cursor
        ------------------------------------
        regexp for validating email address:
        ([a-zA-Z0-9-_+.]+)@([a-zA-Z0-9-_+]+)(\.[a-zA-Z]+){1,3}
    '''
    # TODO: have to CHECK regexp for end part of email addresses!!!!!!!!!
    string = person.email[0]
    emailRegexp = r'([a-zA-Z0-9-_+.]+)@([a-zA-Z0-9-_+]+)(\.[a-zA-Z]+){1,3}'
    comp = re.compile(emailRegexp)
    match = comp.match(string)
    if match:
        return True
    else:
        warning_processing(window, person.email[1], False, 11, window.STARTPOS)


def check_dob(window, person, y, x):
    '''Check if the date of birth (dob) input format is valid.
        person -> person object
        ------------------------------------
        regexp for validating date:
        [0-9]{4}-[0-9]{1,2}-[0-9]{1,2}
    '''
    string = person.dob[0]
    dobRegexp = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
    comp = re.compile(dobRegexp)
    match = comp.match(string)
    if match:
        month = int(string[5:7])
        day = int(string[8:])
        if day > 0 and day < 32 and month > 0 and month < 13:
            return True
        else:
            warning_processing(window, 'Wrong date format!', False, y, x)
            return False
    else:
        warning_processing(window, 'Wrong date format!', False, y, x)
        return False


def warning_processing(window, string, flag, y, x):
    '''warning_processing():
        Couses warning window to appear when some entry is wrong,
        or passwords don't match in form.
        NOTE: ### I mean this is pretty ugly and heavy function but it works!
              ### Very small amount of healthy logic inside!
        window -> parent window
        string -> the subject of error
        flag   -> if password curses.noecho() else curses.echo()
        y, x   -> window.move(y, x) for cursor position when
                  returned from warning window to parent window.
    '''
    def cleaning(window, warwin, flag):
        '''Simple local function for readability and not repeating myself.'''
        warwin.refresh()
        warwin.getch()
        curses.flushinp()
        warwin.destroy()
        del warwin
        curses.curs_set(1)

        if flag:
            curses.noecho()
        else:
            curses.echo()

        window.touchwin()

        # This is for registration form,
        # if passwords don't match, then clean both fields
        if y == 13:            # 13 is y position for password
            window.move(15, x) # 15 is y position for confirm password
            window.clrtoeol()

        window.move(y, x)
        window.clrtoeol()
        window.box()
        window.refresh()

    warwin = WarningWindow(string, window)
    warwin.refresh()

    if string == 'Passwords': # Passwords don't match in registration window
        warning = string + ' don\'t match!'
        warwin.addstr(3, (warwin.width - len(warning)) / 2, warning)
        cleaning(window, warwin, True)  # Calling local function

    elif string == 'Email': # Invalid email detected
        warning = 'Invalid email address!'
        warwin.addstr(3, (warwin.width - len(warning)) / 2, warning)
        cleaning(window, warwin, False) # Calling local function

    elif string[:12] == 'No user with': # If there is no typed user in login
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        cleaning(window, warwin, False) # Calling local function

    elif string[:7] == 'Already': # Register form: username exists already
        warning = 'Try again!'
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        warwin.addstr(4, (warwin.width - len(warning)) / 2, warning)
        cleaning(window, warwin, False) # Calling local function

    elif string[:5] == 'Wrong': # In login window, password wrong!
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        cleaning(window, warwin, True) # Calling local function

    elif string == 'Wrong date format':
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        cleaning(window, warwin, False) # Calling local function

    elif string[:4] == 'Type':
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        cleaning(window, warwin, False) # Calling local function
    
    elif string[:3] == 'Can': # Can't login or register. Fill the form!
        warwin.addstr(3, (warwin.width - len(string)) / 2, string)
        cleaning(window, warwin, False) # Calling local function

    else:
        if string != 'Date of Birth':
            warning = 'You forgot the \'' + string + '\' field!'
            warwin.addstr(3, (warwin.width - len(warning)) / 2, warning)
            cleaning(window, warwin, False) # Calling local function


def create_menu_window(stdscr):
    menuWin = MenuWindow(stdscr) # Creating menu window
    choice = menuWin.get_choice()
    fp = open('menuwin', 'w')
    menuWin.putwin(fp) # Dump menu window
    fp.close()

    menuWin.destroy() # Destroy the Menu window
    del menuWin

    stdscr.touchwin()
    stdscr.refresh()

    return choice


def choose_from(choice, person, stdscr):
    if choice == ord('l'):
        result = create_login_form(stdscr, person)
        return result

    elif choice == ord('r'):
        result = create_register_form(stdscr, person)
        return result

    elif choice == '^X':
        return '^X'


def tabbing():
    print 'I\'m tabing!'


def create_login_form(stdscr, person):
    '''Create Login window'''
    logwin = LoginForm(stdscr)

    ### Part for username
    while True:
        person.username[0] = input_processing(logwin, person, \
                                              person.username[1], False, 3)

        if person.username[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, logwin)
            return 2

        elif check_user(logwin, person.username[0], 3, 14):
            break

    ### Part for password
    while True:
        person.password[0] = input_processing(logwin, person, \
                                              person.password[1], True, 5)

        if person.password[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, logwin)
            return 2

        elif check_passwords(logwin, person.password[0], None, 5, 14):
            break

        else: # If nothing happens above reset the wrong password!
        # This is not needed in username becouse of login() funcion:
        # login(): first checks if username == '' and if it is False
        # then checks password == '' and it is True for now.
            person.password[0] = ''

    while True:
        l = logwin.getch(True, True)

        if l == '^L':
            # We are loged in!
            login(person)
            return ['^L', logwin] # Returning a list because of logwin.


def create_register_form(stdscr, person):
    '''Create Register window'''
    regwin = RegisterForm(stdscr)

    ### Part for gender
    while True:
        person.gender[0] = input_processing(regwin, person, \
                                            person.gender[1], False, 3)

        if person.gender[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        elif person.gender[0] == 'male' or person.gender[0] == 'female':
            break

        else:
            warning_processing(regwin, 'Type only \'male\' or \'female\'.',
                               False, 3, regwin.STARTPOS)

    ### Part for firstname
    while True:
        person.firstname[0] = input_processing(regwin, person, \
                                               person.firstname[1], False, 5)

        if person.firstname[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        else:
            break

    ### Part for lastname
    while True:
        person.lastname[0] = input_processing(regwin, person, \
                                              person.lastname[1], False, 7)

        if person.lastname[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        else:
            break

    ### Part for username
    while True:
        person.username[0] = input_processing(regwin, person, \
                                              person.username[1], False, 9)

        if person.username[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        elif check_user(regwin, person.username[0], 9, regwin.STARTPOS):
            break

    ### Part for email
    while True:
        person.email[0] = input_processing(regwin, person, \
                                           person.email[1], False, 11)

        if person.email[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        elif validate_email(regwin, person, 11, regwin.STARTPOS):
            break

    while True:
        ### Part for password
        person.password[0] = input_processing(regwin, person,
                                              person.password[1], True, 13)

        if person.password[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        ### Part for confirm password
        person.confirmPassword[0] = input_processing(regwin, person,
                                                     person.confirmPassword[1],
                                                     True, 15)

        if person.confirmPassword[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        elif check_passwords(regwin, person.password[0],  \
                             person.confirmPassword[0], 15, regwin.STARTPOS):
            break

        else:
            # Reset password fields cause no match!!!!
            # Important!!!!!
            person.password[0] = ''
            person.confirmPassword[0] = ''

    ### Part for date of birth
    while True:
        person.dob[0] = input_processing(regwin, person,
                                      person.dob[1], False, 17)

        if person.dob[0] == 2: # We are going back to the menu window
            window_destroy(stdscr, regwin)
            return 2

        elif person.dob[0] == 10: # There was no input for 'dob'!
            break

        elif check_dob(regwin, person, 17, regwin.STARTPOS):
            break

        else:
            # Reset dob field in person object if it was wrong formatl!
            person.dob[0] = ''

    while True:
        r = regwin.getch(True, True)

        if r == '^R':
            # We are registered!
            register(person)
            return ['^R', regwin] # Returning a list because of regwin.


def login(person):
    '''
    '''
    if person.username[0] == '':
        return False
    if person.password[0] == '':
        return False

    return True # Successfully loged in!


def register(person):
    '''
    '''
    if person.gender[0] == '':
        return False
    if person.firstname[0] == '':
        return False
    if person.lastname[0] == '':
        return False
    if person.username[0] == '':
        return False
    if person.email[0] == '':
        return False
    if person.password[0] == '':
        return False
    if person.confirmPassword[0] == '':
        return False

    '''Writing stuf in to db.'''

    registDate = datetime.datetime.now()

    conn = sqlite.connect(DB)
    curs = conn.cursor()

    query = '''INSERT INTO users  (firstname, lastname, username, email, 
            password, old_password, date_of_birth, 
            registration_date_time, last_login_date_time) 
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    data = (person.firstname[0], person.lastname[0],
            person.username[0],
            person.email[0], person.password[0],
            person.password[0],
            person.dob[0], registDate, registDate)

    #curs.execute(query, (person.firstname[0], person.lastname[0], person.username[0],
    #                     person.email[0], person.password[0],
    #                     registDate, registDate))

    curs.execute(query, data)
    conn.commit()
    conn.close()

    return True # Successfully registered!


def window_destroy(stdscr, window):
    '''window_destroy():
        destroys the window object in parameter 'window',
        'stdscr' is only used for refreshing
    '''
    #window.touchwin() # Is this needed?????? (11 Jan, 2012.)
    window.destroy()
    del window

    stdscr.touchwin()
    stdscr.refresh()


def end(stdscr):
    '''End application'''
    stdscr.touchwin()
    stdscr.refresh()
    curses.beep()
    curses.flash()
    curses.endwin()

    # This removes the dumped menu window file, after exiting application
    list = os.listdir('.')
    for item in list:
        if item == 'menuwin':
            os.remove(item)
            break

    sys.exit(0)

def main(): # If using curses.wrapper(main), add win parametar to main()
    person = User() # Create person

    stdscr = curses.initscr() # Root window, used just for container.

    # Check if terminal can use custom colors
    if curses.can_change_color():
        curses.init_color(1, 54, 54, 54)
        curses.init_color(2, 170, 170, 170)
        curses.init_pair(1, 1, 2)
    else:
        curses.start_color()  # Initializes colors
        curses.use_default_colors()

    while True: # Main loop
        while True: # Basic loop smaller then main loop
            choice = create_menu_window(stdscr)
            result = choose_from(choice, person, stdscr)
             
            if result == 2: # Do nothing just skip! Ugly!!!
                del result
                pass

            elif result[0] == '^L':
                # You are successfully loged in.
                # First cleanup:
                window_destroy(stdscr, result[1])
                [ result.pop() for i in result ]
                result.pop()
                del result
                break

            elif result[0] == '^R':
                # You where successfully registered,
                # from here we start the manu window again.
                # destroy the registration form!
                window_destroy(stdscr, result[1])
                [ result.pop() for i in result ]
                del result
                pass

            elif result == '^X':
                end(stdscr) # Exit before app ends.
                #del result
                #break

            # Now invoke the second part of application
            # We have to remain in while loop, because sometime we need to go back
            # to create_menu_window function if user choose from admin page
        if person.username[0] != 'admin':
            logged = LoggedUserWindow(stdscr) 
            output = logged.getch()
            if output == '^X':
                end(stdscr)
            elif output == 2:
                window_destroy(stdscr, logged)
           
        elif person.username[0] == 'admin':
            adminLogged = LoggedAdminWindow(stdscr)
            output = adminLogged.getch()
            if output == '^X':
                end(stdscr)
            elif output == 1:
                window_destroy(stdscr, adminLogged)

            elif output == 2:
                pass

            elif output == 3:
                pass

            elif output == 4:
                pass

            elif output == 5:
                pass

            elif output == 6:
                pass

            elif output == 7:
                pass

            elif output == 8:
                pass

            elif output == 2:
                pass


if __name__ == '__main__':
    main()

# Or:
#curses.wrapper(main)
