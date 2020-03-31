#dependencies

ffmpeg should be installed and in $PATH

requests,pyaudio libraries, run "pip install -r requirements.txt" to install them

# issues/TODOs

find a way to share the same database connection throughout the whole project

hide functions and variable that shouldn't be used outside the classes,
do that to every class in the code

the code is a mess, needs refactoring

liking songs and adding songs and stuff is currently done through communicating directly with the remote database with other scripts, the daemon should have the functionality to do all of that

the program doesnt close the database connections when its terminated, dunno if this matters when using sqlite

when listing songs, sort them by last listened to

the process of finding music and adding it to the database could be much much faster if we first load all music data into memory and then saving it to the sqlite database instead of executing many database queries in a loop

i have to check what happens when the file of a song gets moved while it is being played

when there is multiple files of a song for an album and the file that was picked to be the one for the album in the database get removed the daemon wont load the other files for the song
