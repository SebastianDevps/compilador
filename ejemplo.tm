* Compilación TINY a código TM
* File: ejemplo.tm
* Preludio estándar:
  0:     LD  6,0(0)	cargar maxaddress desde localización 0
  1:     ST  0,0(0)	clear localización 0
* End of standard prelude.
* -> assign
* -> Const
  2:    LDC  0,10(0)	cargar const
* <- Const
  3:     ST  0,0(5)	assign: almacenar valor
* <- assign
* -> assign
* -> Const
  4:    LDC  0,5(0)	cargar const
* <- Const
  5:     ST  0,1(5)	assign: almacenar valor
* <- assign
* -> assign
* -> Op
* -> Id
  6:     LD  0,0(5)	cargar id value
* <- Id
  7:     ST  0,0(6)	op: push left
* -> Id
  8:     LD  0,1(5)	cargar id value
* <- Id
  9:     LD  1,0(6)	op: cargar left
 10:    MUL  0,1,0	op *
* <- Op
 11:     ST  0,2(5)	assign: almacenar valor
* <- assign
* -> Id
 12:     LD  0,2(5)	cargar id value
* <- Id
 13:    OUT  0,0,0	write ac
* End of execution.
 14:   HALT  0,0,0	
