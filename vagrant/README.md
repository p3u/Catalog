# Swiss System Tournament DB
Python and PostgreSQL code to help coordinating and tracking results for Swiss System tournaments.
A set up for Virtual Machine with Vagrant + VM VirtualBox is included in this repo.
This project is connected to the [Intro to Relational Databases](https://classroom.udacity.com/courses/ud197) course


## Requirements
Python 2
**Running on your own**
PostgreSQL
**Using the set up Virtual Machine**
Vagrant
VirtualBox

## Initialization
Download this repo to your machine
If using Vagrant VM, navigate to the Vgrant folder and start your VM
```
vagrant up
```
Wait for it to start and log in via SSH (On Windows, using Git Bash terminal ensures SSH is included)
```
vagrant ssh
```

To initialize the required tables, navigate to Tournament folder and run:

```
$ psql
```
```
$ \i tournament.sql
```

This only has to be done once. You may close the terminal after this command.

To test everything is working, navigate to Tournament and run :

```
$ python tournament_test.py
```

## Tables available

**players**
Fields:
 -id
 -player_name

**matches**

Fields:
 -id
 -winner
 -loser

## Using the code

Just call the Python Functions below to achieve what you want:

METHOD | ACCEPTS | PURPOSE
--- | --- | ---
registerPlayer(name) | _name as string_ | Adds a player to the database
countPlayers() | _(no input)_ | Returns # of players
swissPairings() | _(no input)_ | Returns a list of tuples with the pairings for the next match in the format (id1, name1, id2, name2)
reportMatch(winner, loser) | _winner as string_, _loser as string_ | Adds the result of a match.
playerStandings() | _(no input)_ | Returns a list of tuples with the players and their win records. The list is sorted by wins and the tuples are in the format (id, name, wins, matches)
