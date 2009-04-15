tasks:
	echo "\n\n`egrep -o '^[[:alnum:]]+' Makefile`"

clean:
	find . -iname '*.pyc' -or -iname '.*.pickle' | xargs echo
