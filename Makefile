tasks:
	echo "\n\n`egrep -o '^[[:alnum:]]+' Makefile`"

clean:
	find . -iname '*.pyc' -or -iname '.*.pickle' | xargs rm

0:
	mkzero-gfxmonk -v `cat VERSION` autonose.xml

upload:
	./setup.py bdist_egg upload
