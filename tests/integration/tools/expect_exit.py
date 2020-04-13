import subprocess
import sys

if len(sys.argv) <= 2:
    print("error: expect_exit: expect arguments to be provided")
    exit(1)

expected_exit_code_arg = sys.argv[1]
try:
    expected_exit_code = int(expected_exit_code_arg)
    if expected_exit_code < 0 or expected_exit_code > 127:
        raise ValueError
except ValueError:
    print("error: expect_exit: expect numeric exit code within range [0, 127]: {}"
          .format(expected_exit_code_arg))
    exit(1)

data = sys.stdin.readlines()

args = sys.argv.copy()

args.pop(0)
args.pop(0)

# To capture the output from the subprocess we set up stderr to be written to
# stdout. This ensures that we see the output from the subprocess in the same
# order as we do in a shell however this does not allow us to capture what is
# actually stdout and what is stderr.
process = subprocess.Popen(args,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
for line in data:
    process.stdin.write(line.encode())

stdout, stderr = process.communicate()

output_lines = stdout.decode('utf-8').split('\n')
# The last '\n' never belongs to the output, it is produced by decode-split.
if len(output_lines) > 0:
    del output_lines[-1]

for word in output_lines:
    print(word)

if process.returncode == expected_exit_code:
    exit(0)
else:
    exit(1)
