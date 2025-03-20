/****************************************************/
/* File: globals.c                                   */
/* Implementación de variables globales              */
/****************************************************/

#include "globals.h"

/* Variables globales */
FILE* source;  /* archivo de código fuente */
FILE* listing; /* archivo de listado */
FILE* code;    /* archivo de código */

int lineno = 0; /* número de línea del código fuente */

/* Banderas de rastreo */
int EchoSource = TRUE;
int TraceScan = TRUE;
int TraceParse = TRUE;
int TraceAnalyze = TRUE;
int TraceCode = TRUE;
int Error = FALSE; /* indica si se encontró un error */