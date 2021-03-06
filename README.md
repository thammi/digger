# About

This project fetches various data sources and generates graphs from them.

Sources are usually fetched into Json files. These Json files are read in by
another program which generates graphs based on the timestamps. This workflow is
effective for small data sets and development. If you want to process large data
sets (in realtime) use another approach!

Feel free to extend the data sources and graphs.

# Dependencies

* Python 2.6, 2.7
* Python Imaging Library (for roll graphs)
* MatPlotLib (for line graphs)
* cjson (optional, faster Json processing)

# Bugs and TODOs

* the line graphs are not drawn correct at points with the value 0
* ...

# Example Workflow

## Microblogging (Identica, Twitter)

Fetch some data from identica or twitter

	./microblogging.py identica thammi
	./microblogging.py twitter chaossource

You can add as many users as you want to the parameter list. The command fetches
the data from the microblogging apis for each user and adds the data to the Json
file.

Create the graphs from the Json files with

	./test.py plot identica twitter

This command plots the graphs for each service specified to the ./out directory.
There will be graphs for each user and the hashtags used by users you fetched.

## Github

You can fetch specific branches from repositories

	./github.py thammi digger master

or all repositories a user has

	./github.py thammi

As soon as you have all repositories you want use

	./test plot github

To build the graphs. There will be graphs for each branch and for the users
which committet to these branches.

## Version Control

The DVCS module supports git and mercurial. You can specify a path to a
repository or a path containing multiple repositories. It will recurse if the
specified directory is not a repository.

	./dvcs.py ~/code/repo

And finally the graph creation

	./test plot dvcs

## Last.fm

You have to own an API key to access the last.fm service. lastfm.py expects your
last.fm API key in the environment variable LASTFM\_KEY. To set it in a posix
compatible shell use

	export LASTFM_KEY your_api_key

Now you can continue with the usual workflow

	./lastfm.py username another_name
	./test.py plot lastfm

This data source generates graphs for users and artists scrobbled by the users.

# Building search graphs from Microblogging

## Plotting searched messages

The following command will search for the given query and build graphs about the
found messages in ./search

	./search_graph.py "#ds2010"

## Plotting users sending messages

The following command will search for the specified **tags** and build graphs about
the users sending these messages in ./auto

	./auto_fetch.py identica ds2010 nackt

