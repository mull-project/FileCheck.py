/**
; RUN: clang %s -o %S/hello-world && %S/hello-world | filecheck %s
; CHECK: Wrong line
 */

#include <stdio.h>
int main() {
  printf("Hello world\n");
  return 0;
}
