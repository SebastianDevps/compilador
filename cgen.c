/****************************************************/
/* File: cgen.c                                      */
/* Generación de código para el compilador TINY      */
/****************************************************/

#include "globals.h"
#include "symtab.h"
#include "code.h"
#include "cgen.h"

/* tmpOffset es el desplazamiento de memoria para
 * almacenar valores temporales para la evaluación de expresiones
 */
static int tmpOffset = 0;

/* Prototipos de funciones */
static void genStmt(TreeNode * tree);
static void genExp(TreeNode * tree);
void cGen(TreeNode * tree);

/* Procedimiento cGen recorre recursivamente el árbol sintáctico y genera
 * código en cada nodo
 */
void cGen(TreeNode * tree)
{ if (tree != NULL)
  { switch (tree->nodekind) {
      case StmtK:
        genStmt(tree);
        break;
      case ExpK:
        genExp(tree);
        break;
      default:
        break;
    }
    cGen(tree->sibling);
  }
}

/* Procedimiento genStmt genera código en un nodo de sentencia */
static void genStmt(TreeNode * tree)
{ TreeNode * p1, * p2, * p3;
  int savedLoc1,savedLoc2,currentLoc;
  int loc;
  switch (tree->kind.stmt) {
    case AssignK:
      /* generar código para evaluar la expresión */
      genExp(tree->child[0]);
      /* ahora almacenar el resultado */
      loc = st_lookup(tree->attr.name);
      emitRM("ST",ac,loc,gp,"asignar: almacenar valor");
      break;
    case ReadK:
      emitRO("IN",ac,0,0,"read integer value");
      loc = st_lookup(tree->attr.name);
      emitRM("ST",ac,loc,gp,"read: almacenar valor");
      break;
    case WriteK:
      /* generar código para evaluar la expresión */
      if (tree->child[0]->nodekind == ExpK && 
          tree->child[0]->kind.exp == StringK) {
        /* Para strings, emitimos cada carácter individualmente */
        char * str = tree->child[0]->attr.name;
        /* Eliminar las comillas del string */
        if (str[0] == '"' && str[strlen(str)-1] == '"') {
          str = str + 1;
          str[strlen(str)-1] = '\0';
        }
        /* Emitir cada carácter */
        for (int i = 0; str[i] != '\0'; i++) {
          emitRM("LDC",ac,str[i],0,"cargar carácter");
          emitRO("OUT",ac,0,0,"escribir carácter");
        }
        /* Emitir un salto de línea */
        emitRM("LDC",ac,10,0,"cargar salto de línea");
        emitRO("OUT",ac,0,0,"escribir salto de línea");
      } else {
        genExp(tree->child[0]);
        /* ahora escribir */
        emitRO("OUT",ac,0,0,"escribir ac");
      }
      break;
    case IfK:
      if (TraceCode) emitComment("-> if");
      p1 = tree->child[0];
      p2 = tree->child[1];
      p3 = tree->child[2];
      /* generar código para la prueba */
      genExp(p1);
      savedLoc1 = emitSkip(1);
      emitComment("if: saltar a else si falso");
      /* recurrir por la rama then */
      genStmt(p2);
      savedLoc2 = emitSkip(1);
      emitComment("if: saltar a end");
      currentLoc = emitSkip(0);
      emitBackup(savedLoc1);
      emitRM_Abs("JEQ",ac,currentLoc,"if: jmp to else");
      emitRestore();
      /* recurrir por la rama else */
      if (p3 != NULL)
      { genStmt(p3);
        currentLoc = emitSkip(0);
        emitBackup(savedLoc2);
        emitRM_Abs("LDA",pc,currentLoc,"jmp to end");
        emitRestore();
      }
      if (TraceCode)  emitComment("<- if");
      break;
    case RepeatK:
      if (TraceCode) emitComment("-> repeat");
      p1 = tree->child[0];
      p2 = tree->child[1];
      savedLoc1 = emitSkip(0);
      emitComment("repeat: marca el inicio del cuerpo");
      /* generar código para el cuerpo */
      genStmt(p1);
      /* generar código para la prueba */
      genExp(p2);
      emitRM_Abs("JEQ",ac,savedLoc1,"repeat: saltar de nuevo si la prueba es falsa");
      if (TraceCode)  emitComment("<- repeat");
      break;
    default:
      break;
  }
}

/* Procedimiento genExp genera código en un nodo de expresión */
static void genExp(TreeNode * tree)
{ int loc;
  char * str;
  int i;
  switch (tree->nodekind) {
    case ExpK:
      switch (tree->kind.exp) {
        case ConstK:
          emitRM("LDC",ac,tree->attr.val,0,"cargar constante");
          break;
        case IdK:
          loc = st_lookup(tree->attr.name);
          emitRM("LD",ac,loc,gp,"cargar id value");
          break;
        case OpK:
          genExp(tree->child[0]);
          emitRM("ST",ac,tmpOffset--,mp,"op: push left");
          genExp(tree->child[1]);
          emitRM("LD",ac1,++tmpOffset,mp,"op: load left");
          switch (tree->attr.op) {
            case PLUS:
              emitRO("ADD",ac,ac1,ac,"op +");
              break;
            case MINUS:
              emitRO("SUB",ac,ac1,ac,"op -");
              break;
            case TIMES:
              emitRO("MUL",ac,ac1,ac,"op *");
              break;
            case OVER:
              emitRO("DIV",ac,ac1,ac,"op /");
              break;
            case LT:
              emitRO("SUB",ac,ac1,ac,"op <");
              emitRM("JLT",ac,2,pc,"br if true");
              emitRM("LDC",ac,0,0,"false case");
              emitRM("LDA",pc,1,pc,"unconditional jmp");
              emitRM("LDC",ac,1,0,"true case");
              break;
            case EQ:
              emitRO("SUB",ac,ac1,ac,"op ==");
              emitRM("JEQ",ac,2,pc,"br if true");
              emitRM("LDC",ac,0,0,"false case");
              emitRM("LDA",pc,1,pc,"unconditional jmp");
              emitRM("LDC",ac,1,0,"true case");
              break;
            default:
              emitComment("BUG: Unknown operator");
              break;
          }
          break;
        case StringK:
          /* Para strings, emitimos cada carácter individualmente */
          str = tree->attr.name;
          /* Eliminar las comillas del string */
          if (str[0] == '"' && str[strlen(str)-1] == '"') {
            str = str + 1;
            str[strlen(str)-1] = '\0';
          }
          /* Emitir cada carácter */
          for (i = 0; str[i] != '\0'; i++) {
            emitRM("LDC",ac,str[i],0,"cargar carácter");
            emitRO("OUT",ac,0,0,"escribir carácter");
          }
          /* Emitir un salto de línea */
          emitRM("LDC",ac,10,0,"cargar salto de línea");
          emitRO("OUT",ac,0,0,"escribir salto de línea");
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
}

/* Procedimiento codeGen genera código para la máquina TM */
void codeGen(TreeNode * syntaxTree, char * codefile) {
    char * s = malloc(strlen(codefile)+7);
    strcpy(s,"File: ");
    strcat(s,codefile);
    emitComment("Compilación TINY a código TM");
    emitComment(s);
    /* generar código estándar de preludio */
    emitComment("Preludio estándar:");
    emitRM("LD",mp,0,ac,"cargar maxaddress desde localización 0");
    emitRM("ST",ac,0,ac,"clear localización 0");
    emitComment("End of standard prelude.");
    /* generar código para TINY */
    cGen(syntaxTree);
    /* terminar */
    emitComment("End of execution.");
    emitRO("HALT",0,0,0,"");
} 