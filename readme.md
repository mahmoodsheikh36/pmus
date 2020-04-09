#dependencies

ffmpeg,ffprobe should be installed and in $PATH

sounddevice library, run "pip install sounddevice" to get it

# issues/TODOs

when finding new music, an artist could get added multiple times, this bug is driving me crazy i thought i had fixed it multiple times before but it keeps coming back lol its so weird i always think that i have fixed it and them move on but later come back and see multiple entries for the same artist in the database, i gotta fix it ASAP

hide functions and variable that shouldn't be used outside the classes,
do that to every class in the code

the program doesnt close the database connections when its terminated, dunno if this matters when using sqlite

when listing songs, sort them by last listened to

the process of finding music and adding it to the database could be much much faster if we first load all music data into memory and then saving it to the sqlite database instead of executing many database queries in a loop

i have to check what happens when the file of a song gets moved while it is being played

there is no documentation or a guide on how to use the music player/deamon, i should work on that
