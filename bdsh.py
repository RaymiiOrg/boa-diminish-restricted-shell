#!/usr/bin/python
# Copyright (C) 2013 - Remy van Elst

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script can act as a shell for a user, allowing specific commands only.
# It tries its best to only allow those comamnds and strip possibly dangerous
# things like ; or >. But it won't protect you if you allow the vim command
# and the user executes !bash via vim (and such). It also logs everything to
# syslog for audit trailing purposes.

# It currently only checks commands, no parameters. This is on purpose.

import getpass, os, re, sys, syslog, signal, socket, readline, subprocess

# format of whitelist: one command or regex per line
command_whitelist = "/etc/bdsh_whitelist.conf"
username = getpass.getuser()
hostname = socket.gethostname()

def log_command(command, status):
    """Log a command to syslog, either successfull or failed. """
    global username
    logline_failed  = "[RESTRICTED SHELL]: user \"" + username + "\" NOT allowed for " + command
    logline_danger  = "[RESTRICTED SHELL]: user \"" + username + "\" dangerous characters in " + command
    logline_success = "[RESTRICTED SHELL]: user \"" + username + "\" executed " + command
    if status == "success":
        syslog.syslog(logline_success)
    elif status == "failed":
        syslog.syslog(logline_failed)
    elif status == "danger":
        syslog.syslog(logline_danger)

def dangerous_characters_in_command(command):
    # via http://www.slac.stanford.edu/slac/www/resource/how-to-use/cgi-rexx/cgi-esc.html
    danger = [';', '&', '|', '>', '<', '*',
              '?', '`', '$', '(', ')', '{',
              '}', '[', ']', '!', '#']
    for dangerous_char in danger:
        for command_char in command:
            if command_char == dangerous_char:
                return True

def execute_command(command):
    """First log, then execute a command"""
    log_command(command, "success")
    try:
        subprocess.call(command, shell=False)
    except OSError:
        pass
    # os.system(command)

def command_allowed(command, whitelist_file=command_whitelist):
    """Check if a command is allowed on the whitelist."""
    try:
        with open(whitelist_file, mode="r") as whitelist:
            for line in whitelist:
                # No idea why the \n is needed but it is...
                if command + "\n" == line:
                    return True
                else:
                    continue

    except IOError as e:
        sys.exit("Error: %s" % e)

def interactive_shell():
    global username
    global hostname
    while True:
        prompt = username + "@" + hostname + ":" + os.getcwd() + " $ "
        try:
            if sys.version_info[0] == 2:
                command = raw_input(prompt)
            else:
                command = input(prompt)
        # Catch CRTL+D
        except EOFError:
            print("")
            sys.exit()
        if command == "exit" or command == "quit":
            sys.exit()
        elif command:
            if command_allowed(command.split(" ", 1)[0]):
                for chars in command:
                    if dangerous_characters_in_command(chars):
                        log_command(command, "danger")
                        # Don't let the user know via an interactive shell and don't exit
                        command=""
                execute_command(command)
   
if __name__ == "__main__":
    ## Catch CTRL+C / SIGINT.
    s = signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    arguments = ""

    for args in sys.argv:
        if dangerous_characters_in_command(args):
            log_command(args, "danger")
            sys.exit()

    ## No Arguments? Then we start an interactive shell.
    if len(sys.argv) < 2:
        interactive_shell()
    else:
        ## Check if we are not launched via the local shell with a command (./shell.py ls)
        if sys.argv[1] and sys.argv[1] != "-c" and command_allowed(sys.argv[1].split(" ", 1)[0]):
            for arg in sys.argv[1:]:
                arguments += arg
                arguments += " "
            execute_command(arguments)
        ## Check if we are launched via the local shell and the command is not allowed
        elif len(sys.argv) < 3:
            for arg in sys.argv:
                arguments += arg
                arguments += " "
            log_command(arguments, "failed")
        elif sys.argv[2] and command_allowed(sys.argv[2].split(" ", 1)[0]):
            for arg in sys.argv[2:]:
                arguments += arg
                arguments += " "
            execute_command(arguments)
        else:
            for arg in sys.argv:
                arguments += arg
                arguments += " "
            log_command(arguments, "failed")
            # Debug use
            # print("\"" + arguments + "\"")
    ## Give back the CTRL+C / SIGINT
    signal.signal(signal.SIGINT, s)