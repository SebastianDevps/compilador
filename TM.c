#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MEMORY_SIZE 1000
#define MAX_INSTRUCTIONS 1000

typedef struct {
    int loc;        // número de línea
    char op[10];    // operación (LD, ST, LDC, etc)
    int r;          // primer registro
    int s;          // segundo valor
    int t;          // tercer valor
} Instruction;

int memory[MEMORY_SIZE];           // memoria de datos
int reg[10];                       // registros
Instruction program[MAX_INSTRUCTIONS]; // memoria de programa
int numInstructions = 0;           // número de instrucciones cargadas

// Carga el programa desde el archivo .tm
void loadProgram(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("Error: No se puede abrir %s\n", filename);
        exit(1);
    }

    char line[200];
    while (fgets(line, sizeof(line), file)) {
        // Ignorar líneas de comentario y vacías
        if (line[0] == '*' || line[0] == '\n') {
            continue;
        }

        int loc;
        char op[10];
        int r, s, t;
        
        // Intentar diferentes formatos de instrucción
        if (sscanf(line, "%d: %s %d,%d(%d)", &loc, op, &r, &s, &t) == 5 ||
            sscanf(line, "%d: %s %d,%d,%d", &loc, op, &r, &s, &t) == 5) {
            
            program[numInstructions].loc = loc;
            strcpy(program[numInstructions].op, op);
            program[numInstructions].r = r;
            program[numInstructions].s = s;
            program[numInstructions].t = t;
            printf("Cargada instrucción %d: %s %d,%d,%d\n", 
                   loc, op, r, s, t);
            numInstructions++;
        }
    }
    fclose(file);
    printf("Total instrucciones cargadas: %d\n", numInstructions);
}

// Ejecuta una instrucción
void executeInstruction(Instruction inst) {
    printf("Ejecutando [%d]: %s %d,%d,%d | ", 
           inst.loc, inst.op, inst.r, inst.s, inst.t);

    if (strcmp(inst.op, "LD") == 0) {
        reg[inst.r] = memory[inst.s + reg[inst.t]];
        printf("R%d = memory[%d] = %d\n", inst.r, inst.s + reg[inst.t], reg[inst.r]);
    }
    else if (strcmp(inst.op, "ST") == 0) {
        memory[inst.s + reg[inst.t]] = reg[inst.r];
        printf("memory[%d] = R%d = %d\n", inst.s + reg[inst.t], inst.r, reg[inst.r]);
    }
    else if (strcmp(inst.op, "LDC") == 0) {
        reg[inst.r] = inst.s;
        printf("R%d = %d\n", inst.r, inst.s);
    }
    else if (strcmp(inst.op, "ADD") == 0) {
        reg[inst.r] = reg[inst.s] + reg[inst.t];
        printf("R%d = R%d + R%d = %d\n", inst.r, inst.s, inst.t, reg[inst.r]);
    }
    else if (strcmp(inst.op, "SUB") == 0) {
        reg[inst.r] = reg[inst.s] - reg[inst.t];
        printf("R%d = R%d - R%d = %d\n", inst.r, inst.s, inst.t, reg[inst.r]);
    }
    else if (strcmp(inst.op, "MUL") == 0) {
        reg[inst.r] = reg[inst.s] * reg[inst.t];
        printf("R%d = R%d * R%d = %d\n", inst.r, inst.s, inst.t, reg[inst.r]);
    }
    else if (strcmp(inst.op, "DIV") == 0) {
        if (reg[inst.t] == 0) {
            printf("Error: División por cero\n");
            exit(1);
        }
        reg[inst.r] = reg[inst.s] / reg[inst.t];
        printf("R%d = R%d / R%d = %d\n", inst.r, inst.s, inst.t, reg[inst.r]);
    }
    else if (strcmp(inst.op, "OUT") == 0) {
        printf("\n==========================================");
        printf("\n=          RESULTADO: %d                =", reg[inst.r]);
        printf("\n==========================================\n");
    }
    else if (strcmp(inst.op, "HALT") == 0) {
        printf("Programa terminado.\n");
        exit(0);
    }
    else {
        printf("Operación desconocida: %s\n", inst.op);
    }
}

void dumpRegisters() {
    printf("\nEstado de registros:\n");
    for (int i = 0; i < 7; i++) {
        printf("R%d = %d  ", i, reg[i]);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Uso: %s <archivo.tm>\n", argv[0]);
        return 1;
    }

    // Inicializar memoria y registros
    memset(memory, 0, sizeof(memory));
    memset(reg, 0, sizeof(reg));

    printf("Cargando programa...\n");
    loadProgram(argv[1]);

    printf("\nEjecutando programa...\n");
    for (int i = 0; i < numInstructions; i++) {
        executeInstruction(program[i]);
        if ((i + 1) % 5 == 0) {  // Mostrar estado cada 5 instrucciones
            dumpRegisters();
        }
    }
    dumpRegisters();

    return 0;
}