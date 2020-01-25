/**
; RUN: gcc %s -o %S/hello-world && %S/hello-world | filecheck %s
; CHECK: Hello world
 */

#include <stdio.h>
int main() {
  printf("Hello world\n");
  return 0;
}
