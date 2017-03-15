class bcolors:
   HEADER = '\033[95m'
   OKBLUE = '\033[94m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'

def die(s):
   print bcolors.FAIL+s+bcolors.ENDC
   raise Exception(s)

def report(s):
   print bcolors.OKGREEN+s+bcolors.ENDC

def warn(s):
   print bcolors.OKBLUE+s+bcolors.ENDC
