.PHONY: example clean

example:
	python main.py "nom: act"

clean:
	rm *.pyc
	rm Output/*.html