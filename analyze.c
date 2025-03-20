/****************************************************/
/* File: analyze.c                                   */
/* Implementación del analizador semántico           */
/****************************************************/

#include "globals.h"
#include "symtab.h"
#include "analyze.h"

/* contador para localidades de memoria */
static int location = 0;

/* recorre el árbol sintáctico para insertar identificadores
 * en la tabla de símbolos
 */
static void traverse(TreeNode * t,
               void (* preProc) (TreeNode *),
               void (* postProc) (TreeNode *) )
{ if (t != NULL)
  { preProc(t);
    { int i;
      for (i=0; i < MAXCHILDREN; i++)
        traverse(t->child[i],preProc,postProc);
    }
    postProc(t);
    traverse(t->sibling,preProc,postProc);
  }
}

/* nullProc es un procedimiento que no hace nada
 * para generar traversals del árbol donde no se
 * necesita pre o post procesamiento
 */
static void nullProc(TreeNode * t)
{ if (t==NULL) return;
  else return;
}

/* Procedimiento insertNode inserta 
 * identificadores almacenados en t en 
 * la tabla de símbolos 
 */
static void insertNode(TreeNode * t)
{ switch (t->nodekind)
  { case StmtK:
      switch (t->kind.stmt)
      { case AssignK:
        case ReadK:
          if (st_lookup(t->attr.name) == -1)
          /* not yet in table, so treat as new definition */
            st_insert(t->attr.name,t->lineno,location++);
          else
          /* already in table, so ignore location, 
           add line number of use only */ 
            st_insert(t->attr.name,t->lineno,0);
          break;
        default:
          break;
      }
      break;
    case ExpK:
      switch (t->kind.exp)
      { case IdK:
          if (st_lookup(t->attr.name) == -1)
          /* not yet in table, so treat as new definition */
            st_insert(t->attr.name,t->lineno,location++);
          else
          /* already in table, so ignore location, 
           add line number of use only */ 
            st_insert(t->attr.name,t->lineno,0);
          break;
        case StringK:
          /* No necesitamos insertar strings en la tabla de símbolos */
          t->type = String;
          break;
        case ConstK:
          t->type = Integer;
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
}

/* Función buildSymtab construye la tabla de símbolos
 * recorriendo el árbol sintáctico
 */
void buildSymtab(TreeNode * syntaxTree)
{ traverse(syntaxTree,insertNode,nullProc);
  if (TraceAnalyze)
  { fprintf(listing,"\nTabla de Símbolos:\n\n");
    printSymTab(listing);
  }
}

static void typeError(TreeNode * t, char * message)
{ fprintf(listing,"Error de tipo en línea %d: %s\n",t->lineno,message);
  Error = TRUE;
}

/* Procedimiento checkNode realiza
 * verificación de tipos en un solo nodo
 */
static void checkNode(TreeNode * t)
{ switch (t->nodekind)
  { case ExpK:
      switch (t->kind.exp)
      { case OpK:
          if ((t->child[0]->type != Integer) ||
              (t->child[1]->type != Integer))
            typeError(t,"Op aplicado a no integer");
          if ((t->attr.op == EQ) || (t->attr.op == LT))
            t->type = Boolean;
          else
            t->type = Integer;
          break;
        case ConstK:
          t->type = Integer;
          break;
        case IdK:
          t->type = Integer;
          break;
        case StringK:
          t->type = String;
          break;
        default:
          break;
      }
      break;
    case StmtK:
      switch (t->kind.stmt)
      { case IfK:
          if (t->child[0]->type == Integer)
            typeError(t->child[0],"if test no es boolean");
          break;
        case AssignK:
          if (t->child[0]->type != Integer)
            typeError(t->child[0],"asignación de no integer");
          break;
        case WriteK:
          /* Permitir tanto Integer como String en write */
          if (t->child[0] != NULL && 
              t->child[0]->type != Integer && 
              t->child[0]->type != String)
            typeError(t->child[0],"write de tipo no válido");
          break;
        case RepeatK:
          if (t->child[1]->type == Integer)
            typeError(t->child[1],"repeat test no es boolean");
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
}

/* Procedimiento typeCheck realiza verificación de tipos
 * recorriendo el árbol sintáctico
 */
void typeCheck(TreeNode * syntaxTree)
{ traverse(syntaxTree,nullProc,checkNode);
} 