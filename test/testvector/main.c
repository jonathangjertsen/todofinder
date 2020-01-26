#include <stdio.h>
int main() {
   printf("Hello, World!"); // TODO: something
   /**
   TODO: catch multline comment
   */
   int todo = 0; // shouldn't catch this one
   int x = 1; /* inline multiline-style comment TODO: catch*/
   return todo; /* not this either */
    // TODO: catch standalone comment
    //TODO:catch without spaces
    /*TODO:catch multiline without spaces TODO another*/
}
