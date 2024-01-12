#!/usr/bin/python3
#
# auditd2json
# Purpose: This script can be used to convert an auditd file into JSON. Script excepts one liners or whole files
# Python 3.X
# https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/security_guide/sec-understanding_audit_log_files

import argparse
import time, sys, json

#### Configure commandline options ####
#
#

parser = argparse.ArgumentParser(description='Convert an auditd file or line into JSON')
parser.add_argument('-f', '--file', help='Specify the complete path of file to convert to JSON', dest='file', required=False)
parser.add_argument('-l', '--line', help='Specify a single line in "" to convert to JSON', dest='line', required=False)
parser.add_argument('-o', '--output_file', help='Specify a destination file for file conversion output', dest='output', required=False)

#
#
####

#### Function Definitions ####
#
#

def getTimeAndID(line):
    timestamp, id = line.replace('msg=audit(','').replace('):','').split(':')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(timestamp[0])))
    return timestamp, id

def makeReadable(key):
    return{
        'acct': 'account',
        'res': 'result',
        'comm': 'command-line',
        'pid': 'process_id',
        'uid': 'user_id',
        'auid': 'audit_user_id',
        'exe': 'executable'
    }.get(key, key)

def displayStartText():
    print("Running audit2json...")
    time.sleep(0.5)

def processFile(path, output):
    entries = []
    with open(path,'r') as f:
        event_id = -1
        event = []
        for line in f:
            record = processLine(line.replace('\n',''))
            if output:
                # if this is a new event then append the record and update event and id
                if event_id != record['event_id']:
                    entries.append(event)
                    event = [record]
                    event_id = record['event_id']
                else: # This is another record in the same event
                    event.append(record)

            else:
                printResult(entry)

    if len(entries) > 0:
        with open(output, 'w') as w:
            w.write(json.dumps(entries, indent=4))

def processLine(line):
    entry = {}
    attributes = line.split(' ')
    for attribute in attributes:
        if 'msg=audit' in attribute:
            entry['timestamp'], entry['event_id'] = getTimeAndID(attribute) 
        else:
            try:
                attribute = attribute.replace('msg=','').replace('\'','').replace('"','').split('=')
                if 'cmd' in attribute[0] or 'proctitle' in attribute[0]:
                    attribute[1] = bytearray.fromhex(attribute[1]).decode()
                entry[makeReadable(attribute[0])] = attribute[1]
            except:
                pass

    return entry

def printResult(result):
    print(json.dumps(result, indent=4))

#
#
####

#### Script Start ####
#
#
# Parse and process options
try:
    if __name__ == "__main__":
        # Parse argparse arguments
        args = vars(parser.parse_args())

        # Interpret options
        if args['file']:
            displayStartText()
            print("\nConverting file...\n")
            if args['output']:
                output = args['output']
            else:
                output = None
            processFile(args['file'], output)
            print("Conversion completed!")
        elif args['line']:
            displayStartText()
            print("\nConverting line...\n")
            printResult(processLine(args['line']))
            print("\nConversion completed!")
        else:
            print("\nOooops! No actionable arguments supplied....let me run the help for you\n")
            time.sleep(1)
            parser.print_help()

# Properly hanle exceptions
except (KeyboardInterrupt):
    print('terminated.')
sys.exit(0)

#
#
####
