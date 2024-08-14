% Unification

fruit(banana).
fruit(apple).
fruit(orange).

vegetable(carrot).
vegetable(broccoli).
vegetable(peas).

tasty(X) :- fruit(X).

fruitOrVeg(X) :- fruit(X).
fruitOrVeg(X) :- vegetable(X).

% Predicates
max(X, Y, Z) :- X > Y,
    			X = Z.

max(X, Y, Z) :- X =< Y,
    			Y = Z.
% Recursion

maxList([X], X).
maxList([H|T], Max) :- maxList(T, Max2),
    					max(H, Max2, Max).

% Lists
append([], Ys, Ys).
append([X|Xs], Ys, [X|Zs]) :- append(Xs, Ys, Zs).
sublist(Xs, Ys) :- append(_As, XsBs, Ys), append(Xs, _Bs, XsBs).

row_of_eight(Row) :- Row = [_,_,_,_,_,_,_,_].

seating_plan(X) :- row_of_eight(X),
    				sublist([alice,_,bob],X),
    				sublist([charlie,_,david],X),
    				sublist([e,f,g],X),
    				sublist([h],X).

% Arithmatics

collatz(1,[1]) :- !.

collatz(N,L) :- 0 is N mod 2,
    			N2 is N / 2,
    			L = [N|L2],
    			collatz(N2, L2).

collatz(N,L) :- 1 is N mod 2,
    			N2 is N * 3 + 1,
    			L = [N|L2],
    			collatz(N2,L2).





