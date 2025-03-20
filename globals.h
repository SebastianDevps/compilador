/****************************************************/
/* File: globals.h                                  */
/* Global types y variables para el compilador TINY  */
/* debe ir antes que otros archivos include         */
/* Construcción de Compiladores: Principios y       */
/* Práctica - Kenneth C. Louden                     */
/****************************************************/

#ifndef _GLOBALS_H_
#define _GLOBALS_H_

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#ifndef FALSE
#define FALSE 0
#endif

#ifndef TRUE
#define TRUE 1
#endif

/* MAXRESERVED = cantidad de palabras reservadas */
#define MAXRESERVED 8

typedef enum {
    /* palabras reservadas */
    IF,THEN,ELSE,ENDIF,REPEAT,UNTIL,READ,WRITE,WHILE,ENDWHILE,
    /* tokens multicaracter */
    ID,NUM,STRING,  /* Agregado STRING explícitamente */
    /* símbolos especiales */
    ASSIGN,EQ,LT,PLUS,MINUS,TIMES,OVER,LPAREN,RPAREN,SEMI,
    /* otros */
    ENDFILE,ERROR
} TokenType;

extern FILE* source; /* archivo de texto del código fuente */
extern FILE* listing; /* archivo de texto de salida del listado */
extern FILE* code; /* archivo de texto de código para el simulador TM */

extern int lineno; /* número de línea del código fuente para el listado */

/**************************************************/
/***********   Árbol sintáctico para parsing *******/
/**************************************************/

typedef enum {StmtK,ExpK} NodeKind;
typedef enum {IfK,RepeatK,AssignK,ReadK,WriteK} StmtKind;
typedef enum {OpK,ConstK,IdK,StringK} ExpKind;  /* Agregado StringK */

/* ExpType es usado para verificación de tipos */
typedef enum {Void,Integer,Boolean,String} ExpType;  /* Agregado String */

#define MAXCHILDREN 3

typedef struct treeNode
   { struct treeNode * child[MAXCHILDREN];
     struct treeNode * sibling;
     int lineno;
     NodeKind nodekind;
     union { StmtKind stmt; ExpKind exp;} kind;
     union { TokenType op;
             int val;
             char * name; } attr;
     ExpType type; /* para verificación de tipos de expresiones */
   } TreeNode;

/**************************************************/
/***********   Banderas para rastreo   ************/
/**************************************************/

/* EchoSource = TRUE hace que el programa fuente se
 * muestre en el archivo de listado con números de línea
 * durante el parsing
 */
extern int EchoSource;

/* TraceScan = TRUE hace que la información de tokens
 * se imprima en el archivo de listado cuando cada token
 * es reconocido por el scanner
 */
extern int TraceScan;

/* TraceParse = TRUE hace que el árbol sintáctico
 * se imprima en el archivo de listado en forma linealizada
 * (usando indentación para los hijos)
 */
extern int TraceParse;

/* TraceAnalyze = TRUE hace que las inserciones y búsquedas
 * en la tabla de símbolos se reporten en el archivo de listado
 */
extern int TraceAnalyze;

/* TraceCode = TRUE hace que se escriban comentarios
 * en el archivo de código TM mientras se genera el código
 */
extern int TraceCode;

/* Error = TRUE previene pases adicionales si ocurre un error */
extern int Error;
#endif