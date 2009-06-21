tasks:
	echo "\n\n`egrep -o '^[[:alnum:]]+' Makefile`"

clean:
	find . -iname '*.pyc' -or -iname '.*.pickle' | xargs rm

upload:
	./setup.py bdist_egg upload