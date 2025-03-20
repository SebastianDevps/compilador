/****************************************************/
/* File: analyze.h                                   */
/* Analizador semántico para el compilador TINY      */
/****************************************************/

#ifndef _ANALYZE_H_
#define _ANALYZE_H_

#include "globals.h"

/* Función buildSymtab construye la tabla de símbolos 
 * recorriendo el árbol sintáctico
 */
void buildSymtab(TreeNode *);

/* Procedimiento typeCheck realiza la verificación de tipos 
 * en el árbol sintáctico
 */
void typeCheck(TreeNode *);

#endif 