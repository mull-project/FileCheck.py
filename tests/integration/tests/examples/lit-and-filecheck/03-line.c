/**
; RUN: gcc "%s" -o %S/line && %S/line | filecheck %s
 */

#include <stdio.h>
int main() {
  // CHECK: Hello from line [[# @LINE + 1 ]]
  printf("Hello from line %d\n", __LINE__);
  return 0;
}
