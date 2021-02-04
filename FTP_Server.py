###################################
#                                 #
#     John Moore - COMP 431       #
#   Starter server code for HW1   #
#          Version 1.2            #
###################################

import os
import sys
import shutil
# Define important ASCII character decimal representations
# These are helpful for defining various command grammars  
# Use ord(char) to get decimal ascii code for char
cr = ord('\r')  # = 13
lf = ord('\n')  # = 10
crlf_vals = [cr, lf]

# Define known server commands (case insensitive). Add to this as commands are added
command_list = ["USER", "PASS", "TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]

# Manage valid response messages for every command
valid_responses = {
    "USER" : "331 Guest access OK, send password.\r\n",
    "TYPEA" : "200 Type set to A.\r\n",
    "TYPEI" : "200 Type set to I.\r\n",
    "SYST" : "215 UNIX Type: L8.\r\n",
    "NOOP" : "200 Command OK.\r\n",
    "PASS": "230 Guest login OK.\r\n",
    "QUIT" : "200 Command OK.\r\n"
    # "RETR" : "\r\n",
    # "RETR" : "\r\n",
    # "RETR" : "\r\n",
}

##############################################################################################
#                                                                                            # 
#     This function is intended to manage the command processing loop.                       #
#     The general idea is to loop over the input stream, identify which command              #
#     was entered, and then delegate the command-processing to the appropriate function.     #
#                                                                                            #
##############################################################################################
def read_commands():
    # FTP service always begins with "220 COMP 431 FTP server ready.\r\n"
    sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
    # Keep track of the expected commands, initially only "USER" and "QUIT" are valid commands
    expected_commands = ["USER", "QUIT"]
    success_login = False
    port = False
    file_num = 0
    for command in sys.stdin:       # Iterate over lines from input stream until EOF is found
        # Echo the line of input
        sys.stdout.write(command)
        
        # Split command into its tokens and parse relevant command
        tokens = command.split()    # Assume tokens are delimited by <SP>, <CR>, <LF>, or <CRLF>

        # Check to make sure there are tokens in the line, and assign command_name
        command_name = tokens[0].upper() if len(tokens) > 0 else "UNKNOWN"       # Commands are case-insensitive
        # Check first token in list to see if it matches any valid commands
        if command_name in command_list and not command[0].isspace():
            if command_name in expected_commands:
                #############################################################
                #  This is intended to delegate command processing to       #
                #  the appropriate helper function. Helper function parses  #
                #  command, performs any necessary work, and returns        #
                #  updated list of expected commands                        #
                #############################################################
                if command_name == "USER":         
                    result, expected_commands = parse_user(tokens)
                elif command_name == "PASS":         
                    result, expected_commands = parse_pass(tokens)
                elif command_name == "TYPE":         
                    result, expected_commands= parse_type(tokens)
                elif command_name == "NOOP":         
                    result, expected_commands = parse_noop(command)
                elif command_name == "PORT":         
                    result, expected_commands, info = parse_port(tokens)
                elif command_name == "SYST":         
                    result, expected_commands = parse_syst(command)
                elif command_name == "QUIT":         
                    result, dumb = parse_quit(command)
                elif command_name == "RETR":         
                    result, expected_commands, address = parse_retr(command)
                

                ##################################################
                #  After command processing, the following code  #
                #  prints the appropriate response message       #
                ##################################################
                if len(result) > 3:
                    sys.stdout.write(result)
                else:
                    if ord(command[-1]) == lf and ord(command[-2]) == cr:       # The ord(char) function gives decimal ascii code of char
                        
                        if command_name == "TYPE":
                            sys.stdout.write(valid_responses[command_name+result])
                        elif command_name == "RETR":
                            source = address
                            file_num = file_num + 1
                            destination = "retr_files" + '/' + 'file' + f'{file_num}'
                            if os.access(source, os.F_OK):
                                shutil.copy(source, destination)
                                port = False
                                sys.stdout.write("150 File status okay.\r\n")
                                sys.stdout.write("250 Requested file action completed.\r\n")
                            else:
                                file_num = file_num - 1
                                sys.stdout.write(f'550 File not found or access denied.\r\n')
                          
                            
                            
                            
                        elif command_name == "PORT":
                            port = True
                            sys.stdout.write(f'200 Port command successful ({info}).\r\n')
                        elif command_name == "PASS":
                            success_login = True
                            sys.stdout.write(valid_responses[command_name])
                        elif command_name == "QUIT":
                            sys.stdout.write(valid_responses[command_name])
                            sys.exit()
                        else:
                            sys.stdout.write(valid_responses[command_name])
                        
                        if port:
                            expected_commands.append('RETR')
                        
                    else:
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        ######################################################
                        #  Update expected_commands list if incorrect CRLF   #
                        #  changes the possible commands that can come next  #     
                        ######################################################
                        
                        if command_name == "USER" or "PASS":
                            expected_commands = ["USER", "QUIT"]
                        elif command_name == "QUIT":
                            if not success_login:
                                expected_commands = ["USER", "QUIT"]
                            elif not port:
                                expected_commands = ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
                            else:
                                expected_commands = ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
            else:
                # Out of order command received
                if not success_login:
                    sys.stdout.write("530 Not logged in.\r\n")
                    expected_commands = ["QUIT", "USER"]
                else:
                    sys.stdout.write("503 Bad sequence of commands.\r\n")
        else:
            # No valid command was input
            sys.stdout.write("500 Syntax error, command unrecognized.\r\n")

################################################################################
#                                                                              # 
#     Parse the USER command to check if tokens adhere to grammar              #
#     The "tokens" parameter is a list of the elements of the command          #
#     separated by whitespace. The return value indicates if the command       #
#     is valid or not, as well as the next list of valid commands.             #
#                                                                              #
################################################################################
def parse_user(tokens):
    # Check to make sure there is at least one token after "USER"
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    else:
        # Iterate through remaining tokens and check that no invalid usernames are entered
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals:     # Byte values > 127 along with <CRLF> are not valid for usernames
                    return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    return "ok", ["USER", "PASS", "QUIT"]      # If the function makes it here, the input adheres to the grammar for this command

def parse_pass(tokens):
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    else:
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals:     
                    return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]

def parse_noop(command):
    if command[:-2].upper() == "NOOP":
        return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
    else:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]

def parse_syst(command):
    if command[:-2].upper() == "SYST":
        return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
    else:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]


def parse_type(tokens):
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
    else:
        if tokens[1] == "A" or tokens[1] == "I":
            return  tokens[1] , ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]  
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]

def parse_quit(command):
    if command[:-2].upper() == "QUIT":
        return "ok", []
    else:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]

def parse_port(tokens):
    temp = tokens[1].split(',')
    if len(tokens) > 2 or len(temp) != 6:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"], ''
    for num in temp:
        if not num.isdigit():
            return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"], ''
    
    return 'ok', ["TYPE", "SYST", "NOOP", "QUIT", "PORT"], f'{temp[0]}.{temp[1]}.{temp[2]}.{temp[3]},{int(temp[4])*256 + int(temp[5])}'
def parse_retr(command):
    tokens = command.split()
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"], ''
    else:
        # Iterate through remaining tokens and check that no invalid usernames are entered
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals:     # Byte values > 127 along with <CRLF> are not valid for usernames
                    return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"], ''
    return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"], f'{command[5:-2]}'





read_commands()
