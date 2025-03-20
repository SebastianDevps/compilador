/****************************************************/
/* File: cgen.h                                      */
/* Interfaz del generador de código para el          */
/* compilador TINY                                   */
/****************************************************/

#ifndef _CGEN_H_
#define _CGEN_H_

#include "globals.h"  /* Para TreeNode */

/* Procedimiento cGen genera código en un nodo */
void cGen(TreeNode * tree);

/* Procedimiento codeGen genera código para la máquina TM */
void codeGen(TreeNode * syntaxTree, char * codefile);

#endif 