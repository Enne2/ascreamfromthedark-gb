# Unsafe historical rewriters

Questi script sono snapshot storici, conservati soltanto per consultazione.

Non fanno parte della build e **non devono essere eseguiti sul codice corrente**:
riscrivono file C o generatori con sostituzioni testuali/regex basate su versioni
precedenti dell'engine. Alcuni reintrodurrebbero bug già corretti, inclusi layout
VRAM errati, vecchie variabili globali e logica nemici non più compatibile.

Le modifiche utili devono essere reimplementate nei sorgenti correnti, validate
e applicate con patch revisionabili.
