import argparse
import json
import acronym_config as config
import sys


def process_arguments(arglist):

    parser = argparse.ArgumentParser(description="Add or list acronyms!")

    # We can only do one operation at a time.
    command = parser.add_mutually_exclusive_group(required=True)

    # Add an acronym
    command.add_argument('-a', '--add', nargs='+',
    help='accepts a string and automatically uses the first letter of each word to create an ACRONYM.')
    
    # Look up an acronym
    command.add_argument('-d', '--def', nargs=1,
    help='accepts a string and returns all entries where the ACRONYM matches')
    
    # Look up an acronym
    command.add_argument('-f', '--find', nargs='+',
    help='accepts a string and returns all entries where either the ACRONYM or the DEFINITION match')


    # NOT Mutually exclusive, but will be ignored if we aren't using --add
    # We can also manually define the letters for the acronym
    parser.add_argument('-m', '--manual', nargs=1,
    help='use with --add. accepts a string with no spaces after this to manually designate an ACRONYM')

    # Parse it
    args = parser.parse_args(arglist)

    return args

def acronym(args):
    # Load file information from config
    acronym_list_file_name = config.storage_file
    with open(acronym_list_file_name,'r+b') as acronym_list_file:
        acronym_list_json = json.load(acronym_list_file)

    arguments = request.form['text'].split(':',1)

    if len(arguments) >= 2:
        command = arguments[0].strip(' ').lower()
        cmdarg = arguments[1].strip(' ')
    elif "listall" in arguments:
        command = 'listall'
    else:
        command = 'help'
        cmdarg = ''

    response=''
    responsetype='ephemeral'
    if  command == 'auto' or command == 'add':
        if cmdarg.replace(' ','').replace(',','',1).replace(';','',1).replace(':','',1).replace("'",'',2).isalnum():
            words = cmdarg.split(' ')
            acro_builder=''
            if len(words)>1:
                for word in words:
                    acro_builder += word[0]
                acro_builder = acro_builder.upper()

                cmdarg=cmdarg.title()

                if acro_builder in acronym_list_json and cmdarg not in acronym_list_json[acro_builder]:
                    acronym_list_json[acro_builder].append(cmdarg)
                else:
                    acronym_list_json.update([ (acro_builder, [cmdarg] ) ])

                response += 'Added entry:\n' + bold(acro_builder) + ': ' + cmdarg
                responsetype='in_channel'
            else:
                response += 'Cannot add one-word acronyms'
        else:
            response+= 'Alphanumeric characters and spaces only please.'


    elif command == 'manual':
        cmdarg=cmdarg.split(':',1)
        if cmdarg[0].replace(' ','').isalnum():
            if len(cmdarg) == 2 and len(cmdarg[1].split(' ')) > 1 and len(cmdarg[0]) > 1:
                acr=cmdarg[0].upper().strip(' ')
                words=cmdarg[1].title().strip(' ')
                if acr in acronym_list_json and words not in acronym_list_json[acr]:
                    acronym_list_json[acr].append(words)
                else:
                    acronym_list_json.update([ (acr, [words] ) ])

                response += 'Added entry:\n' + bold(acr) + ': ' + words
                responsetype='in_channel'
            else:
                response+= 'Manual usage: `/ab manual : [acronym] : [meaning]`\nAcronym must be longer than one character. Definition must be longer than one word.'
        else:
            response+='Alphanumeric characters and spaces only in acronym please.'

    elif command == 'def' or command == 'get' or command == 'decode' or command == 'define':
        cmdarg=cmdarg.upper()
        if cmdarg in acronym_list_json:
            possibilities = len(acronym_list_json[cmdarg])
        else:
            possibilities = 0


        if possibilities == 0:
            response+='I do not have any definitions for *' + cmdarg + '*. Consider adding one?'
        elif possibilities == 1:
            response+= bold(cmdarg) + ': ' + acronym_list_json[cmdarg][0]
            responsetype='in_channel'
        else:
            response+='I have multiple entries for ' + bold(cmdarg) + ':\n'
            responsetype='in_channel'
            for possible in acronym_list_json[cmdarg]:
                response+='  -' + italic(possible) + '\n'

    elif command == 'find' or command == 'search':
        if len(cmdarg) >= 2:
            cmdarg=cmdarg.lower()
            responsetype='in_channel'
            for x in sorted(acronym_list_json):
                if cmdarg in x.lower():
                    response += bold(x) + ': ' + str(acronym_list_json[x]) + '\n'

            for x in sorted(acronym_list_json):
                for y in acronym_list_json[x]:
                    if cmdarg in y.lower():
                        response += bold(x) + ': ' + y + '\n'
            if response == '':
                response = "I ain't found shit"
                responsetype='in_channel'
        else:
            response = "Please make search terms at least 2 characters."

    elif command == 'listall':
        ENABLED = True
        if ENABLED == True:
            html='<!DOCTYPE html>\n<body>'
            for x in sorted(acronym_list_json):
                html += '<b>'+x+'</b>: <br><ul>\n'
                for y in sorted(acronym_list_json[x]):
                    html+='<li>'+y+'</li>\n'
                html +='\n</ul><br>\n'
            html +='</body>'
            with open('/home/pricecomstock/slash-selfie/acronyms/acronym_list.html','w') as ab_html:
                ab_html.write(html)
            response = 'List updated: http://pricecomstock.pythonanywhere.com/ab_list'
        else:
            response = 'That command is not currently enabled.'

    else:
        response+='Usage: /ab [command] : [args]\nExamples:\n  `add : phrase to become acronym`\n  `manual : P2BA : phrase to become acronym`\n  `def : ATBP`\n  `find : text`'

    # print(str(request.form))

    acronym_list_file.truncate(0)
    acronym_list_file.seek(0)
    acronym_list_file.write(json.dumps(acronym_list_json,sort_keys=True, indent=4))
    acronym_list_file.close()

    return jsonify({'response_type':responsetype,'text':response})
    # return jsonify({'response_type':responsetype,'text':response,'thread_ts':request.form['ts']})

if  __name__ == "__main__": # used for testing pretty much
    args = process_arguments(sys.argv[1:])
    acronym(args)