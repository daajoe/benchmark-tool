%v(X) :- edge(X,_).
%v(X) :- edge(_,X).

%selection of buckets, 19 vertices
%b(1..19).

%source of projection variables, vertices 1, 2, ..., 100
%p(1..100).

1 { abstract(B,X) : p(X)} 1 :- b(B).

:- abstract(B,X), abstract(B2,X), B != B2.

bucket(B,X) :- abstract(B,X).
bucket(B,Z) :- bucket(B,Y), abstract(B,Y), edge(Y,Z).
bucket(B,Z) :- bucket(B,Y), abstract(B,Y), edge(Z,Y).

abs(X) :- abstract(_,X).

bucket(B,Z) :- bucket(B,Y), not abs(Y), edge(Y,Z).
bucket(B,Z) :- bucket(B,Y), not abs(Y), edge(Z,Y).

:~ X < Y, abstract(B,X), abstract(_,Y), bucket(B,Y). [1,X,Y]
%:~ abstract(B,X), abstract(_,Y), bucket(B,Y). [10,X]

%aedge(X,Y) :- X < Y, abstract(B,X), abstract(_,Y), bucket(B,Y). %[1,X,Y]
%#show aedge/2.

#show abs/1.
%#show abstract/2.

%#show vertex/1.
%vertex(X) :- aedge(X,_).
%vertex(X) :- aedge(_,X).

