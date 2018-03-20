import argparse
import json
import acronym_config as config
import sys

# Global variable that will indicate whether ephemeral
# I've thought about this and I think this is actually the least clunky way to do this
ephemeral_response = True

def process_arguments(arglist):
    # This is a link to a lookup website full of acronyms
    lookup_link = config.lookup_link

    parser = argparse.ArgumentParser(description="Add or list acronyms!", prog="Acronym Bot",
    # add_help=False,
    formatter_class=argparse.RawTextHelpFormatter,
    usage='\n'.join([
        "\n*ADD:* `/ab -a Phrase to Add`",
        "*MANUAL:* `/ab -a Phrase to Add -m P2A`",
        "*DEFINE:* `/ab -d ATD`",
        "*FIND:* `/ab -f query`",
        ]),
    epilog=lookup_link)

    # We can only do one operation at a time.
    command = parser.add_mutually_exclusive_group(required=True)

    # Add an acronym
    command.add_argument('-a', '--add', nargs='+',
    help=argparse.SUPPRESS)
    # help='accepts a string and automatically uses the first letter of each word to create an ACRONYM.')
    
    # Look up an acronym
    command.add_argument('-d', '--define', nargs=1,
    help=argparse.SUPPRESS)
    # help='accepts a string and returns all entries where the ACRONYM matches')
    
    # Look up an acronym
    command.add_argument('-f', '--find', nargs='+',
    help=argparse.SUPPRESS)
    # help='accepts a string and returns all entries where either the ACRONYM or the DEFINITION match')


    # NOT Mutually exclusive, but will be ignored if we aren't using --add
    # We can also manually define the letters for the acronym
    parser.add_argument('-m', '--manual', nargs=1,
    help=argparse.SUPPRESS)
    # help='use with --add. accepts a string with no spaces after this to manually designate an ACRONYM')

    # Parse it
    try:
        args = parser.parse_args(arglist)
    except:
        # False indicates there was an issue and the second part is help
        return False, parser.format_help()
    # print(args)
    # True indicates everything went ok and the second part is args
    return True, args

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
    global ephemeral_response
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
        
        if acronym in acronym_dict and definition in acronym_dict[acronym]:
            return "That acronym and definition already exist together"
        else:
            acronym_dict.setdefault(acronym, []) # Add acronym to the dictionary if it isn't already
            acronym_dict[acronym].append(definition) # Add definition to the acronym's entry

            ephemeral_response = False
            return "Added entry:\n{}".format(stringify_acronym(acronym, definition))

    else:
        return "Invalid acronym"

def define_acronym(acronym_dict, acronym):
    global ephemeral_response
    acronym = acronym.upper()
    
    if acronym in acronym_dict:
        definition_list = acronym_dict[acronym]
        num_definitions = len(definition_list)
        ephemeral_response = False
        
        if num_definitions == 1:
            return stringify_acronym(acronym, definition_list[0])
        
        else:
            response_string = "I have {ct} entries for {acr}:\n".format(ct=str(num_definitions), acr=acronym)
            response_string += "\n".join(["_-{}_".format(definition) for definition in definition_list])
            return response_string
    
    else:
        return "I don't have any entries for {}".format(acronym)

def find_acronym(acronym_dict, query):
    global ephemeral_response
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
            ephemeral_response = False
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
    
    # Save Results
    with open(acronym_list_file_name,'w') as acronym_list_file:
        json.dump(acronym_list_json, acronym_list_file)
    
    # Return response text. It is not encapsulated into a specific format at this point, just text
    return response_text

# This is the interface for other programs to use.
def process_command(command):
    global ephemeral_response
    ephemeral_response = True # ephemeral by default
    
    # Parse Chat Command
    argparse_results = process_arguments(command.split())
    
    # successful argparse
    if argparse_results[0]:
        args = argparse_results[1]
        # print(args)
        # Send off to get executed
        result = process_acronym(args)
        print(result)
        print(ephemeral_response)
        return result, ephemeral_response
    
    else:
        # Return help
        return argparse_results[1], True #help should be ephemeral
    

if  __name__ == "__main__": # used for testing pretty much
    process_command(" ".join(sys.argv[1:]))