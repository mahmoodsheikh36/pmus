#dependencies

ffmpeg should be installed and in $PATH

requests,pyaudio libraries, run "pip install -r requirements.txt" to install them

# issues/TODOs

find a way to share the same database connection throughout the whole project

hide functions and variable that shouldn't be used outside the classes,
do that to every class in the code

the code is a mess, needs refactoring

liking songs and adding songs and stuff is currently done through communicating directly with the remote database with other scripts, the daemon should have the functionality to do all of that
