PROGRAM testprog;
CONST number = +1;
      blabla = -5#13;
VAR (* comments *)
    var1, var2, var3, var4, var5: SIGNAL FLOAT, FLOAT, INTEGER, [1 .. 7], SIGNAL INTEGER;
DEFFUNC 
    add = i+2 \ 5 , 15;
PROCEDURE proc1 (param1, param2: BLOCKFLOAT, INTEGER);
BEGIN 
    LINK var1 IN 12;
    LINK var5 OUT 5;
END.
