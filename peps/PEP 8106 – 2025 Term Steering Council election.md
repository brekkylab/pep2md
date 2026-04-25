---
pep: 8106
title: 2025 Term Steering Council election
author:
- Ee Durbin <ee@python.org>
sponsor: Thomas Wouters <thomas@python.org>
status: Final
type: Informational
topic: Governance
created: 21-Oct-2024
python_status: Final
url: https://peps.python.org/pep-8106/
source_path: https://github.com/python/peps/blob/main/peps/pep-8106.rst
source_commit: b167bc87fdcb0d316ed4b4af1e32d30cba9e07f7
generated_at: '2026-04-25T02:55:53+00:00'
---

# Abstract

This document describes the schedule and other details of the 2024
election for the Python steering council, as specified in
`13`{.interpreted-text role="pep"}. This is the steering council
election for the 2025 term (i.e. Python 3.14).

# Election Administration

The steering council appointed the [Python Software
Foundation](https://www.python.org/psf-landing/) Director of
Infrastructure, Ee Durbin, to administer the election.

# Schedule

There was a two-week nomination period, followed by a two-week vote.

The nomination period was: November 7, 2024 through [November 21, 2024
AoE](https://www.timeanddate.com/worldclock/fixedtime.html?msg=Python+Steering+Council+nominations+close&iso=20241122T00&p1=3399)[^1].

The voting period was: November 25, 2024 through [December 9, 2024
AoE](https://www.timeanddate.com/worldclock/fixedtime.html?msg=Python+Steering+Council+voting+closes&iso=20241210T00&p1=3399)[^2].

# Candidates

Candidates must be nominated by a core team member. If the candidate is
a core team member, they may nominate themselves.

Nominees (in alphabetical order by first name):

- [Barry
  Warsaw](https://discuss.python.org/t/steering-council-nominations-barry-warsaw-2025-term/71732/)
- [Donghee
  Na](https://discuss.python.org/t/steering-council-nomination-donghee-na-2025-term/71731)
- [Emily
  Morehouse](https://discuss.python.org/t/steering-council-nomination-emily-morehouse-2025-term/71824)
- [Ethan
  Furman](https://discuss.python.org/t/steering-council-nomination-ethan-furman-2025-term/71899)
- [Gregory P.
  Smith](https://discuss.python.org/t/steering-council-nomination-gregory-p-smith-2025-term/71947)
- [Mariatta](https://discuss.python.org/t/steering-council-nomination-mariatta-2025-term/71950)
- [Pablo Galindo
  Salgado](https://discuss.python.org/t/steering-council-nomination-pablo-galindo-salgado-2025-term/71915)
- [Thomas
  Wouters](https://discuss.python.org/t/steering-council-nomination-thomas-wouters-2025-term/71792)

Withdrawn nominations:

- None

# Voter Roll

All active Python core team members are eligible to vote. Active status
is determined as `described in PEP 13 <13#membership>`{.interpreted-text
role="pep"} and implemented via the software at
[python/voters](https://github.com/python/voters) [^3].

Ballots were distributed based on the the [Python Voter
Roll](https://github.com/python/voters/blob/master/voter-files/)[^4] for
this election.

While this file is not public as it contains private email addresses,
the [Complete Voter Roll](#complete-voter-roll) is available with a list
of all eligible voters by name.

# Election Implementation

The election was conducted using the [Helios Voting
Service](https://heliosvoting.org).

## Configuration

Short name: `2025-python-steering-council`

Name: `2025 Python Steering Council Election`

Description:
`Election for the Python steering council, as specified in PEP 13. This is steering council election for the 2025 term.`

type: `Election`

Use voter aliases: `[X]`

Randomize answer order: `[X]`

Private: `[X]`

Help Email Address: `psf-election@python.org`

Voting starts at: `November 25, 2024 12:00 UTC`

Voting ends at: `December 10, 2024 12:00 UTC`

This will create an election in which:

- Voting is not open to the public, only those on the [Voter
  Roll](#voter-roll) may participate. Ballots will be emailed when
  voting starts.
- Candidates are presented in random order, to help avoid bias.
- Voter identities and ballots are protected against cryptographic
  advances.

## Questions

### Question 1

Select between `0` and `- (approval)` answers. Result Type: `absolute`

Question: `Select candidates for the Python Steering Council`

Answer #1 - #N: `Candidates from Candidates_ Section`

# Results

Of 100 eligible voters, 76 cast ballots.

The top five vote-getters are:

- Barry Warsaw
- Donghee Na
- Emily Morehouse
- Gregory P. Smith
- Pablo Galindo Salgado

No conflict of interest as defined in `13`{.interpreted-text role="pep"}
were observed.

The full vote counts are as follows:

  ----------------------------------------
  Candidate               Votes Received
  ----------------------- ----------------
  Barry Warsaw            58

  Donghee Na              48

  Emily Morehouse         52

  Ethan Furman            31

  Gregory P. Smith        50

  Mariatta                23

  Pablo Galindo Salgado   63

  Thomas Wouters          38
  ----------------------------------------

# Copyright

This document has been placed in the public domain.

# Complete Voter Roll

## Active Python core developers

``` text
Adam Turner
Alex Gaynor
Alex Waygood
Alexander Belopolsky
Alyssa Coghlan
Ammar Askar
Andrew Svetlov
Antoine Pitrou
Barney Gale
Barry Warsaw
Batuhan Taskaya
Benjamin Peterson
Berker Peksağ
Brandt Bucher
Brett Cannon
Brian Curtin
C.A.M. Gerlach
CF Bolz-Tereick
Carl Meyer
Carol Willing
Cheryl Sabella
Chris Withers
Christian Heimes
Dennis Sweeney
Dino Viehland
Donghee Na
Emily Morehouse
Éric Araujo
Eric Snow
Eric V. Smith
Erlend Egeberg Aasland
Ethan Furman
Ezio Melotti
Facundo Batista
Filipe Laíns
Fred Drake
Georg Brandl
Giampaolo Rodolà
Gregory P. Smith
Guido van Rossum
Hugo van Kemenade
Hynek Schlawack
Inada Naoki
Irit Katriel
Ivan Levkivskyi
Jack Jansen
Jason R. Coombs
Jelle Zijlstra
Jeremy Hylton
Jeremy Kloth
Jesús Cea
Joannah Nanjekye
Julien Palard
Karthikeyan Singaravelan
Ken Jin
Kirill Podoprigora
Kumar Aditya
Kurt B. Kaiser
Kushal Das
Kyle Stanley
Larry Hastings
Łukasz Langa
Lysandros Nikolaou
Marc-André Lemburg
Mariatta
Mark Shannon
Matt Page
Michael Droettboom
Nathaniel J. Smith
Ned Batchelder
Ned Deily
Neil Schemenauer
Nikita Sobolev
Pablo Galindo
Paul Ganssle
Paul Moore
Petr Viktorin
Pradyun Gedam
R. David Murray
Raymond Hettinger
Ronald Oussoren
Russell Keith-Magee
Sam Gross
Savannah Ostrowski
Senthil Kumaran
Serhiy Storchaka
Shantanu Jain
Stefan Behnel
Steve Dower
Stéphane Wirtel
Tal Einat
Terry Jan Reedy
Thomas Wouters
Tian Gao
Tim Golden
Tim Peters
Victor Stinner
Vinay Sajip
Yury Selivanov
Zachary Ware
```

[^1]: AoE: [Anywhere on Earth](https://www.ieee802.org/16/aoe.html).

[^2]: AoE: [Anywhere on Earth](https://www.ieee802.org/16/aoe.html).

[^3]: This repository is private and accessible only to Python Core
    Developers, administrators, and Python Software Foundation Staff as
    it contains personal email addresses.

[^4]: This repository is private and accessible only to Python Core
    Developers, administrators, and Python Software Foundation Staff as
    it contains personal email addresses.
