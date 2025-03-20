/****************************************************/
/* File: symtab.h                                    */
/* Tabla de símbolos para el compilador TINY         */
/****************************************************/

#ifndef _SYMTAB_H_
#define _SYMTAB_H_

#include <stdio.h>
#include "globals.h"

/* Procedimiento st_insert inserta línea y 
 * localización de memoria para una variable
 */
void st_insert(char * name, int lineno, int loc);

/* Función st_lookup retorna la localización de memoria
 * de una variable o -1 si no se encuentra
 */
int st_lookup(char * name);

/* Procedimiento printSymTab imprime una lista formateada 
 * del contenido de la tabla de símbolos
 */
void printSymTab(FILE * listing);

#endif 