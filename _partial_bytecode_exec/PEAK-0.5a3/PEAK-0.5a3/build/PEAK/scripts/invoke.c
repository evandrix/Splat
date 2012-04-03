#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

int argcount(char *arg1) {
    /* Count number of runs of non-blank characters in 'arg1' */
    int ct;
    char *p;
    ct = 0;

    for (p = arg1; *p; p++) {
        /* count if nonspace found and previous character is a space or BOF */
        if (' '!=*p && (p==arg1 || *(p-1)==' '))
            ct++;
    }
    return ct;
}
























int main(int argc, char **argv) {

    char **useargs = argv;
    char **newargs;
    char *p;
    int argct;

    if ( argc>1 ) {

        /* printf("2 or more args\n"); */
        argct = argcount(argv[1]);      /* printf("argct=%d\n", argct); */
        newargs = useargs = (char **)calloc(argct+argc+1, sizeof(char *));
        *newargs++ = argv[0];

        for (p=argv[1]; *p; p++) {
            /* save ptr if nonspace and previous character wasn't space/BOF */
            if (' '==*p) {
                /* convert spaces to end-of-string */
                *p=0;
            } else if (p==argv[1] || !*(p-1)) {
                *newargs++ = p;
                /* printf("%s\n", p); */
            }
        }

        argv+=2;
        argc-=2;

        while(argc--)
            *newargs++ = *argv++;

        *newargs = NULL;

        /* printf("doing exec\n"); */
        execvp(useargs[1], useargs+1);
    }
    return 2; /* if we're still here, it's a usage error */
}



