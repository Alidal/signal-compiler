type
	TSymbol = record
	value: Char;
	attr: Byte;
end;

{ Опис типів таблиць }
var
	Attributes: array [Char] of Byte;
	symbol: TSymbol;
	lexCode: Word;
	buf: string;
	SuppressOutput: Boolean;
	FINP: TextFile;

{Опис таблиць}
function Gets: TSymbol;
begin
	Read(FINP, Result.value);
	Result.attr := Attributes[Result.value];
end;

begin
	(*відкриття файлу початкової програми*)
	(*початкове встановлення таблиць ідентифікаторів і констант*)
	FillAttributes;
	if eof(FINP) then
		ShowError('Empty file');
	repeat
		symbol := Gets;
		buf := '';
		lexCode := 0;
		SuppressOutput := False;
		case symbol.attr of
			0: (*whitespace*)
			begin
				while not eof(FINP) do
				begin
					symbol := Gets;
					if symbol.attr <> 0 then
						Break;
				end;
				SuppressOutput := True;
			end;
			1: (*константа*)
			begin
				while not eof(FINP) and (symbol.attr = 1) do
				begin
					buf := buf + symbol.value;
					symbol := Gets;
				end;
				if ConstTabSearch then
					(* lexCode := <код константи> *)
				else
				begin
					(* lexCode := <код наступної константи> *)
					ConstTabForm;
				end;
			end;

			2: (*ідентифікатор*)
			begin
				while not eof(FINP) and ((symbol.attr = 2)
				or (symbol.attr = 1)) do
				begin
					buf := buf + symbol.value;
					symbol := Gets;
				end;

				if KeyTabSearch then
					(* lexCode := <код ключового слова> *)
				else
					if IdnTabSearch then
						(* lexCode := <код ідентифікатора> *)
					else
					begin
						(* lexCode := <код наступного ідентифікатора> *)
						IdnTabForm;
					end;
			end;
			3: (*можливий коментар, тобто зустрінута '(' *)
			begin
				if eof(FINP) then
					(* lexCode := <код відкриваючої дужки> *)
				else
				begin
					symbol := Gets;
					if symbol.value = '*' then
					begin
						if eof(FINP) then
							ShowError('*) expected but end of file found');
						else
						begin
							symbol := Gets;
							repeat
							while not eof(FINP) and (symbol.value <> '*') do
							symbol := Gets;
							if eof(FINP) then //якщо кінець файла
							begin
								ShowError('*) expected but end of file found');
								symbol.value = '+'; // все що завгодно, але не ')'
								Break;
							end
							else //була '*' і немає кінця файла
								symbol := Gets;
							until symbol.value = ')';
							if symbol.value = ')' then
								SuppressOutput := True;
							if not eof(FINP) then
								symbol := Gets;
						end;
						else
							(* lexCode := <код відкриваючої дужки> *)
					end;
				end;
			end;
			4: (*роздільник окрім '(' *)
			begin
				symbol := Gets;
				(* lexCode := <ASCII код односимвольного роздільника> *)
			end;
			5: (*помилка*)
			begin
				ShowError('Illegal symbol');
				symbol := Gets;
			end;
		end;
		(*case*)
		if not SuppressOutput then
			writeln('Output: ',' ',lexCode);
	until eof(FINP);
	Readln;
end.