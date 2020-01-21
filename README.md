# Far Cry: Online Platform

## Project Description

Far Cry is a first-person shooter (FPS) video game with amazing graphics, developed by Crytek and published by Ubisoft. The game was released in 2004 for Microsoft Windows. The game was a huge commercial success. Ubisoft closed the online servers almost 12 years later.

Far Cry features a single player in which the player impersonates Jack Carver, an ex special forces soldier stranded on a mysterious archipelago. Far Cry also features several multiplayer modes in which players basically score points by killing other players.

Even if Ubisoft closed the online servers in October 2015, players can still play multiplayer matches by setting up LAN parties.

We need to design and to implement an online service composed of several softwares that allows to:

- Authenticate players;
- Load and store players settings;
- Store the frags of game sessions.

## Project Goal

Create Software Applications:

- Far Cry Launcher: a desktop application that runs on each Far Cry gaming machine that allows a player to login against the Far Cry RESTful API server, to launch Far Cry (the game), and to automatically load/save the settings of the player;
- Far Cry Match Watchdog: a command-line interface (CLI) application that runs on the Far Cry dedicated server and that submits frags of game sessions to the Far Cry RESTful API server;
- Far Cry RESTful API Server: an application server that surfaces a RESTful API to login, to load and save player settings, to submit frags of game sessions.

## Technology

- RESTful API
- Framework: Electron, Nodejs, Bootstrap, Django
- HTML, CSS, Python, jQuery

## Project Team

- Dinh Vinh Khang Vu
- Thanh Luan Nguyen
- Anh Vu Le
- Lam Khang Tran

## Feature

### Far Cry Launcher

Far Cry Launcher is a desktop application to be installed and to be ran on a Far Cry gaming computer. It has a graphical user interface (GUI) that allows a player:

- To login to the Far Cry online platform;
- To automatically load the player's settings previously saved to the Far Cry online platform;
- To launch Far Cry (the game);
- To save the player's settings to the Far Cry online platform, when the player quits Far Cry;
- To logout the player.

Far Cry Launcher connects to the Far Cry RESTful API Server that surfaces a RESTful API to support all these actions.

The player doesn't directly run Far Cry, the video game, but instead the player runs Far Cry Launcher that will launch Far Cry.

### Far Cry Match Watchdog

Far Cry Match Watchdog is a Command Line Interface (CLI) application that runs on the machine that is used to launch Far Cry multiplayer game sessions. You can use whatever language you want. As of 2019, Python is probably one of the best options.

This application extracts data from Far Cry's log file to detect when a match starts and ends, when a player kills another or commits suicide.

You, as a developer, can choose to support one or both of the following two modes:

- The application simply submits match activities once the game session has ended (easier);
- The application monitors and submits match activities in real-time while a game session is going on (harder).

This application calls the RESTful API to submit data.

### Far Cry RESTful API

Implement the RESTful API of the Far Cry online platform with Django REST framework. Document the logical data model of your Far Cry online platform, such as an Entity Relationship Diagram (ERD). Document RESTful API either in a static document using a Swagger.
