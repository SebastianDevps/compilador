/****************************************************/
/* File: main.c                                      */
/* Programa principal para el compilador TINY        */
/****************************************************/

#include "globals.h"
#include "util.h"
#include "scan.h"
#include "parse.h"
#include "analyze.h"
#include "cgen.h"

int main(int argc, char * argv[]) {
    TreeNode * syntaxTree;
    char pgm[120]; /* nombre del archivo fuente */
    if (argc != 2) {
        fprintf(stderr,"Uso: %s <nombre_archivo>\n",argv[0]);
        exit(1);
    }
    strcpy(pgm,argv[1]);
    if (strchr (pgm, '.') == NULL)
        strcat(pgm,".tny");
    source = fopen(pgm,"r");
    if (source==NULL) {
        fprintf(stderr,"Archivo %s no encontrado\n",pgm);
        exit(1);
    }
    listing = stdout; /* envía listado a la pantalla */
    fprintf(listing,"\nCompilación TINY: %s\n",pgm);
    
    syntaxTree = parse();
    if (TraceParse) {
        fprintf(listing,"\nÁrbol Sintáctico:\n");
        printTree(syntaxTree);
    }
    
    if (! Error) {
        if (TraceAnalyze) fprintf(listing,"\nConstruyendo Tabla de Símbolos...\n");
        buildSymtab(syntaxTree);
        if (TraceAnalyze) fprintf(listing,"\nVerificando Tipos...\n");
        typeCheck(syntaxTree);
        if (TraceAnalyze) fprintf(listing,"\nVerificación de Tipos Completada\n");
        if (! Error) {
            char * codefile;
            int fnlen = strcspn(pgm,".");
            codefile = (char *) calloc(fnlen+4, sizeof(char));
            strncpy(codefile,pgm,fnlen);
            strcat(codefile,".tm");
            code = fopen(codefile,"w");
            if (code == NULL) {
                printf("No se puede abrir %s\n",codefile);
                exit(1);
            }
            codeGen(syntaxTree, codefile);
            fclose(code);
        }
    }
    fclose(source);
    return 0;
} 