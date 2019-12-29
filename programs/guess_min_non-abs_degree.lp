%selection of buckets, 19 vertices
%b(1..19).

%source of projection variables, vertices 1, 2, ..., 100
%p(1..100).

N { abs(X) : p(X) } N :- N = #max{ C : b(C)}.

degree(X,D) :- D = #count{ Y: edge(X,Y), not abs(X); Y: edge(Y,X), not abs(X) }, abs(X).

:~ degree(X,D). [D,X]

#show abs/1.
%#show degree/2.

