##Appunto lineups

Per costruire i dati sulle lineups, chiamo prima l'endpoint per ricevere l'elenco delle partite che si giocheranno in una certa giornata (giornata "N"):

<a>https://api.dunkest.com/api/rounds/N/games</a>

N.B.
Per ottenere il numero della giornata corrente, chiamare l'endpoint:

<a>https://api.dunkest.com/api/rounds/current?league_id=1&fanta_league_id=1</a>

<br>
Poi per ogni id partita, chiamo l'endpoint per la lineup di una certa squadra con id = "ID" e gameID = "gameID":

<a>https://api.dunkest.com/api/league/1/lineups?team_id=1257&game_id=1801</a>

Riceverò quindi l'elenco dei giocatori della squadra, divisi per:

- Regular
- Bench Player
- Injured

