edge(X,Y) :- edge(Y,X).

vertex(X) :- edge(X,_).
vertex(X) :- edge(_,X).

_heuristic(selectedEdge(X,Y), init,U) :- edge(X,Y), _heuristic(vertex(X), init,U), _heuristic(vertex(Y), init,V), U > V, X < Y.
_heuristic(selectedEdge(X,Y), init,U) :- edge(X,Y), _heuristic(vertex(X), init,V), _heuristic(vertex(Y), init,U), U > V, X < Y.

{ selectedEdge(X,Y) } :- edge(X,Y), X < Y.

% all terminal vertices must be reached from arbitrarily picked terminal vertex

reached(Y) :- Y = #min{ X : terminalVertex(X) }.
reached(Y) :- reached(X), selectedEdge(X,Y).
reached(Y) :- reached(X), selectedEdge(Y,X).

:- terminalVertex(X), not reached(X).

% minimize selected edges

#minimize{ 1,X,Y : selectedEdge(X,Y) }.

#show selectedEdge/2.
#show _heuristic/3.
