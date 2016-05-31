PROGRAM testprog;
CONST number = 1;
      blabla = -5#13;
VAR (* comments *)
    var1, var2, var3, var4: SIGNAL, FLOAT, INTEGER, [1 .. 7];
DEFFUNC 
    add = a \ 5 , 6;
PROCEDURE proc1 (param1, param2: BLOCKFLOAT, EXT);
BEGIN 
    LINK lnk IN 12;
    LINK lnk2 OUT 5;
END.
