/****************************************************/
/* File: code.h                                     */
/* Code emitting utilities for the TINY compiler    */
/* and interface to the TM machine                  */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                               */
/****************************************************/

#ifndef _CODE_H_
#define _CODE_H_

/* pc = program counter  */
#define  pc 7

/* mp = "memory pointer" points
 * to top of memory (for temp storage)
 */
#define  mp 6

/* gp = "global pointer" points
 * to bottom of memory for (global)
 * variable storage
 */
#define gp 5

/* accumulator */
#define  ac 0

/* 2nd accumulator */
#define  ac1 1

/* código de instrucciones de la máquina TINY */
typedef enum 
{
    HALT, IN, OUT, ADD, SUB, MUL, DIV, LD,
    ST, LDA, LDC, JLT, JLE, JGT, JGE, JEQ, JNE, JMP
} OpCode;

/* Función TM_codeGen genera código de instrucción */
void TM_codeGen(OpCode op, int r, int s, int t);

/* Procedimiento emitComment imprime comentarios de ensamblador */
void emitComment(char * c);

/* Procedimiento emitRO emite instrucción de registro */
void emitRO(char *op, int r, int s, int t, char *c);

/* Procedimiento emitRM emite instrucción de registro a memoria */
void emitRM(char * op, int r, int d, int s, char *c);

/* Función emitSkip salta "howMany" localidades de código
 * para fijar después. Retorna la posición actual
 * en el arreglo de código
 */
int emitSkip(int howMany);

/* Procedimiento emitBackup respalda a 
 * una localización previa en el código
 */
void emitBackup(int loc);

/* Procedimiento emitRestore restaura la posición actual
 * del código a la posición más recientemente respaldada
 */
void emitRestore(void);

/* Procedimiento emitRM_Abs convierte una referencia absoluta 
 * a una referencia relativa al pc emitiendo instrucción de 
 * registro a memoria
 */
void emitRM_Abs(char *op, int r, int a, char * c);

/* Procedimiento emitString emite una constante de cadena
 * a la máquina TINY
 */
void emitString(char * str);

#endif 