import sys

if len(sys.argv) != 2:
    print("error: printf: expect one argument to be provided")
    exit(1)

formatted_string = sys.argv[1]

formatted_string = formatted_string.replace("\\n", "\n")

print(formatted_string, end="")
