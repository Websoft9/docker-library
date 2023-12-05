import sys

# sys.argv[1] is the first argument passed to the script
input_arg = sys.argv[1]

# Split the input argument on commas to get a list of filenames
filenames = input_arg.split(',')

# Remove any empty strings from the list
filenames = [filename for filename in filenames if filename]

print(filenames)  # This will print the list of filenames