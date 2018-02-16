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
    command.add_argument('-d', '--define', nargs=1,
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
    print(args)
    return args

def acronym_is_acceptable(acronym):
    return acronym.isalnum()

def definition_is_acceptable(definition_words):
    joined_definition_words = ''.join(definition_words)
    return all([
        len(definition_words) > 1,
        # Allow some common punctuation that isn't just trying to break everything
        joined_definition_words.replace(' ','').replace(',','',3).replace(';','',3).replace(':','',3).replace("'",'').isalnum()
    ])

def stringify_acronym(acronym, definition):
    return "*{}*: {}".format(acronym, definition)

def add_acronym(acronym_dict, definition_words, manual_acronym=None):
    
    acronym=''
    if definition_is_acceptable(definition_words):
        
        if manual_acronym:
            if acronym_is_acceptable(manual_acronym):
                acronym = manual_acronym.upper()
        else:
            # assemble first letters
            for word in definition_words:
                acronym += word[0]
            acronym = acronym.upper() #convert to all caps
        
        # join and capitalize each word of the acronym
        definition = ' '.join(definition_words).title()

        acronym_dict.setdefault(acronym, []) # Add acronym to the dictionary if it isn't already
        acronym_dict[acronym].append(definition) # Add definition to the acronym's entry

        print("Added entry:\n{}".format(stringify_acronym(acronym, definition)))

    else:
        return "Invalid acronym"

def define_acronym(acronym_dict, acronym):
    acronym = acronym.upper()
    
    if acronym in acronym_dict:
        definition_list = acronym_dict[acronym]
        num_definitions = len(definition_list)
        if num_definitions == 1:
            return stringify_acronym(acronym, definition_list[0])
        
        else:
            response_string = "I have {ct} entries for {acr}:\n".format(ct=str(num_definitions), acr=acronym)
            response_string += "\n".join(["_-{}_".format(definition) for definition in definition_list])
            return response_string
    
    else:
        return "I don't have any entries for {}".format(acronym)

def find_acronym(acronym_dict, query):
    query=" ".join(query).lower()
    if len(query) >= 2:
        response_text = "\n".join([stringify_acronym(acronym, str(acronym_dict[acronym])) # pass whole list as definition
                        for acronym in sorted(acronym_dict)
                        if query in acronym.lower()])
        response_text += "\n--------------\n"
        
        # This one gets real complicated as a list comprehension
        for acronym in sorted(acronym_dict):
            for entry in acronym_dict[acronym]:
                if query in entry.lower():
                    response_text += stringify_acronym(acronym, entry) + "\n"
        if response_text.strip().replace("-","") == '':
            response_text = "I ain't found shit"
    else:
        response_text = "Please make search terms at least 2 characters."
    
    return response_text

def process_acronym(args):
    # Load file information from config
    acronym_list_file_name = config.storage_file
    
    acronym_list_json = {} # set to empty in case file doesn't exist
    try:
        with open(acronym_list_file_name,'r') as acronym_list_file:
            acronym_list_json = json.load(acronym_list_file)
    except IOError:
        print("File does not exist, so a new one will be created.")
    except ValueError:
        print("File is broken, so a new one will be created.")

    # If arguments exist, that's our command
    if args.add:
        manual = None
        if args.manual:
            manual = args.manual[0]
        response_text = add_acronym(acronym_list_json, args.add, manual_acronym=manual)
    
    elif args.define:
        response_text = define_acronym(acronym_list_json, args.define[0])
    
    elif args.find:
        response_text = find_acronym(acronym_list_json, args.find)
    
    print(response_text)

    with open(acronym_list_file_name,'w') as acronym_list_file:
        json.dump(acronym_list_json, acronym_list_file)

    #############################################################
    #### OLD CODE
    #### BELOW THIS
    #### POINT
    #############################################################

def old_DO_NOT_USE():
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
    process_acronym(args)