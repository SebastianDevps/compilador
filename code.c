/****************************************************/
/* File: code.c                                      */
/* Generador de código TM para el compilador TINY    */
/****************************************************/

#include "globals.h"
#include "code.h"

/* TM location number for current instruction emission */
static int emitLoc = 0;

/* Highest TM location emitted so far
   For use in conjunction with emitSkip,
   emitBackup, and emitRestore */
static int highEmitLoc = 0;

/* Procedimiento emitComment imprime un comentario 
 * en el archivo de código ensamblador
 */
void emitComment(char * c) {
    if (TraceCode) fprintf(code,"* %s\n",c);
}

/* Procedimiento emitRO emite una instrucción de registro
 * op = código de operación
 * r = registro destino
 * s = primer registro fuente
 * t = segundo registro fuente
 * c = comentario a ser impreso si TraceCode es TRUE
 */
void emitRO(char *op, int r, int s, int t, char *c) {
    fprintf(code,"%3d:  %5s  %d,%d,%d",emitLoc++,op,r,s,t);
    if (TraceCode) fprintf(code,"\t%s",c);
    fprintf(code,"\n");
    if (highEmitLoc < emitLoc) highEmitLoc = emitLoc;
}

/* Procedimiento emitRM emite una instrucción de registro a memoria
 * op = código de operación
 * r = registro destino
 * d = desplazamiento
 * s = registro base
 * c = comentario a ser impreso si TraceCode es TRUE
 */
void emitRM(char * op, int r, int d, int s, char *c) {
    fprintf(code,"%3d:  %5s  %d,%d(%d)",emitLoc++,op,r,d,s);
    if (TraceCode) fprintf(code,"\t%s",c);
    fprintf(code,"\n");
    if (highEmitLoc < emitLoc) highEmitLoc = emitLoc;
}

/* Función emitSkip salta "howMany" localidades de código
 * para después ser llenadas. También retorna la posición
 * actual del código generado
 */
int emitSkip(int howMany) {
    int i = emitLoc;
    emitLoc += howMany;
    if (highEmitLoc < emitLoc) highEmitLoc = emitLoc;
    return i;
}

/* Procedimiento emitBackup respalda a 
 * una localización previa en el código
 */
void emitBackup(int loc) {
    if (loc > highEmitLoc) emitComment("BUG en emitBackup");
    emitLoc = loc;
}

/* Procedimiento emitRestore restaura la posición actual
 * del código a la más alta posición previamente emitida
 */
void emitRestore(void) {
    emitLoc = highEmitLoc;
}

/* Procedimiento emitRM_Abs convierte una referencia absoluta
 * a una referencia relativa al pc emitiendo una instrucción
 * de registro a memoria
 */
void emitRM_Abs(char *op, int r, int a, char * c) {
    fprintf(code,"%3d:  %5s  %d,%d(%d)",emitLoc,op,r,a-(emitLoc+1),pc);
    ++emitLoc;
    if (TraceCode) fprintf(code,"\t%s",c);
    fprintf(code,"\n");
    if (highEmitLoc < emitLoc) highEmitLoc = emitLoc;
}

/* Procedure emitString emits a string constant
 * to the TM code
 */
void emitString(char * str)
{ 
  /* Eliminar las comillas del string */
  char * cleanStr = str;
  if (str[0] == '"' && str[strlen(str)-1] == '"') {
    cleanStr = str + 1;
    cleanStr[strlen(cleanStr)-1] = '\0';
  }
  fprintf(code,"%3d:  .STRING \"%s\"\n",emitLoc++,cleanStr);
  if (highEmitLoc < emitLoc) highEmitLoc = emitLoc;
} 