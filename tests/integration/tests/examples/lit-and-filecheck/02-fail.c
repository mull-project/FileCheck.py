/**
; RUN: gcc %s -o %S/hello-world && %S/hello-world | filecheck %s; test $? = 1
; CHECK: Wrong line
 */

#include <stdio.h>
int main() {
  printf("Hello world\n");
  return 0;
}
