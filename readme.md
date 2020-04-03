#dependencies

ffmpeg,ffprobe should be installed and in $PATH

sounddevice library, run "pip install sounddevice" to get it

# issues/TODOs

find a way to share the same database connection throughout the whole project

hide functions and variable that shouldn't be used outside the classes,
do that to every class in the code

the program doesnt close the database connections when its terminated, dunno if this matters when using sqlite

when listing songs, sort them by last listened to

the process of finding music and adding it to the database could be much much faster if we first load all music data into memory and then saving it to the sqlite database instead of executing many database queries in a loop

i have to check what happens when the file of a song gets moved while it is being played

when there is multiple files of a song for an album and the file that was picked to be the one for the album in the database get removed the daemon wont load the other files for the song
