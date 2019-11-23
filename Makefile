.PHONY: docs po mo

help:
	@echo "test - run the test py.test suite"
	@echo "coverage - generate a coverage report and open it"
	@echo "docs - generate Sphinx HTML documentation and open it"
	@echo "apk - build an android apk with buildozer"
	@echo "deploy - deploy the app to your android device"
	@echo "po - create i18n message file"
	@echo "mo - create i18n locales files"

test:
	pytest

coverage:
	coverage run -m pytest
	coverage html
	xdg-open htmlcov/index.html

docs:
	$(MAKE) -C docs html
	xdg-open docs/build/html/index.html

apk:
	buildozer -v android debug

deploy:
	buildozer android deploy logcat

po:
	xgettext -Lpython --output=messages.pot src/waclient/*.py src/waclient/*/*.py src/waclient/*.kv
	msgmerge --update --no-fuzzy-matching --backup=off po/en.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/de.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/es.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/fr.po messages.pot

mo:
	mkdir -p data/locales/en/LC_MESSAGES
	mkdir -p data/locales/de/LC_MESSAGES
	mkdir -p data/locales/es/LC_MESSAGES
	mkdir -p data/locales/fr/LC_MESSAGES
	msgfmt -c -o data/locales/en/LC_MESSAGES/witness-angel-client.mo po/en.po
	msgfmt -c -o data/locales/de/LC_MESSAGES/witness-angel-client.mo po/de.po
	msgfmt -c -o data/locales/es/LC_MESSAGES/witness-angel-client.mo po/es.po
	msgfmt -c -o data/locales/fr/LC_MESSAGES/witness-angel-client.mo po/fr.po
