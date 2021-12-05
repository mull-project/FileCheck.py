/**
RUN: gcc "%s" -o %S/hello-world-1 && %S/hello-world-1 | %FILECHECK_EXEC %s
CHECK: Hello world
 */

#include <stdio.h>
int main() {
  printf("Hello world\n");
  return 0;
}
