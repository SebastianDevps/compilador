/****************************************************/
/* File: scan.c                                      */
/* Scanner para el compilador TINY                   */
/****************************************************/

#include "globals.h"
#include "util.h"
#include "scan.h"

/* estados del DFA */
typedef enum {
    START,INASSIGN,INCOMMENT,INNUM,INID,INSTRING,DONE
} StateType;

/* lexema actual */
char tokenString[MAXTOKENLEN+1];

/* palabras reservadas y sus tokens */
static struct {
    char* str;
    TokenType tok;
} reservedWords[MAXRESERVED] = {
    {"if",IF}, {"then",THEN}, {"else",ELSE}, {"end",ENDIF},
    {"repeat",REPEAT}, {"until",UNTIL}, {"read",READ}, {"write",WRITE}
};

/* getNextChar obtiene el siguiente caracter no blanco del archivo fuente */
static int getNextChar(void) {
    if (source != NULL) return getc(source);
    else return EOF;
}

/* ungetNextChar retrocede un caracter en el archivo fuente */
static void ungetNextChar(int c) {
    if (source != NULL) ungetc(c,source);
}

/* busca en la tabla de palabras reservadas */
static TokenType reservedLookup(char * s) {
    int i;
    for (i=0; i<MAXRESERVED; i++)
        if (!strcmp(s,reservedWords[i].str))
            return reservedWords[i].tok;
    return ID;
}

/* getToken retorna el siguiente token del archivo fuente */
TokenType getToken(void) {
    int tokenStringIndex = 0;
    TokenType currentToken;
    StateType state = START;
    int save;
    while (state != DONE) {
        int c = getNextChar();
        save = TRUE;
        switch (state) {
            case START:
                if (isdigit(c))
                    state = INNUM;
                else if (isalpha(c))
                    state = INID;
                else if (c == ':')
                    state = INASSIGN;
                else if ((c == ' ') || (c == '\t') || (c == '\n'))
                {
                    save = FALSE;
                    if (c == '\n') lineno++;
                }
                else if (c == '{')
                {
                    save = FALSE;
                    state = INCOMMENT;
                }
                else if (c == '"')
                {
                    save = FALSE;
                    state = INSTRING;
                }
                else
                {
                    state = DONE;
                    switch (c) {
                        case EOF:
                            save = FALSE;
                            currentToken = ENDFILE;
                            break;
                        case '=':
                            currentToken = EQ;
                            break;
                        case '<':
                            currentToken = LT;
                            break;
                        case '+':
                            currentToken = PLUS;
                            break;
                        case '-':
                            currentToken = MINUS;
                            break;
                        case '*':
                            currentToken = TIMES;
                            break;
                        case '/':
                            currentToken = OVER;
                            break;
                        case '(':
                            currentToken = LPAREN;
                            break;
                        case ')':
                            currentToken = RPAREN;
                            break;
                        case ';':
                            currentToken = SEMI;
                            break;
                        default:
                            currentToken = ERROR;
                            break;
                    }
                }
                break;
            case INCOMMENT:
                save = FALSE;
                if (c == EOF) {
                    state = DONE;
                    currentToken = ENDFILE;
                }
                else if (c == '}') state = START;
                break;
            case INASSIGN:
                state = DONE;
                if (c == '=')
                    currentToken = ASSIGN;
                else
                {
                    ungetNextChar(c);
                    save = FALSE;
                    currentToken = ERROR;
                }
                break;
            case INNUM:
                if (!isdigit(c)) {
                    ungetNextChar(c);
                    save = FALSE;
                    state = DONE;
                    currentToken = NUM;
                }
                break;
            case INID:
                if (!isalpha(c)) {
                    ungetNextChar(c);
                    save = FALSE;
                    state = DONE;
                    currentToken = ID;
                }
                break;
            case INSTRING:
                if (c == '"') {
                    save = FALSE;
                    state = DONE;
                    currentToken = STRING;
                }
                else if (c == EOF) {
                    state = DONE;
                    currentToken = ERROR;
                }
                break;
            case DONE:
            default:
                fprintf(listing,"Error del Scanner: estado = %d\n",state);
                state = DONE;
                currentToken = ERROR;
                break;
        }
        if ((save) && (tokenStringIndex <= MAXTOKENLEN))
            tokenString[tokenStringIndex++] = (char) c;
        if (state == DONE) {
            tokenString[tokenStringIndex] = '\0';
            if (currentToken == ID)
                currentToken = reservedLookup(tokenString);
        }
    }
    if (TraceScan) {
        fprintf(listing,"\t%d: ",lineno);
        printToken(currentToken,tokenString);
    }
    return currentToken;
} 