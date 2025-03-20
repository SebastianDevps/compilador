/****************************************************/
/* File: scan.h                                      */
/* Interface del scanner para el compilador TINY     */
/****************************************************/

#ifndef _SCAN_H_
#define _SCAN_H_
#include "globals.h"
/* MAXTOKENLEN es el tamaño máximo de un token */
#define MAXTOKENLEN 40

/* tokenString almacena el lexema de cada token */
extern char tokenString[MAXTOKENLEN+1];

/* función que obtiene el siguiente token */
TokenType getToken(void);

#endif 