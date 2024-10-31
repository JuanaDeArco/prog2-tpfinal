PIP_CMD := $(shell command -v pip3 2>/dev/null)
ifeq ($(PIP_CMD),)
  PIP_CMD := pip
endif



.PHONY: install
install: activate
	$(PIP_CMD) install -r req.txt

.PHONY: clean
clean:
	rm -rf venv

env:
	python3 -m venv venv

activate:
	. venv/bin/activate

deactivate:
	deactivate

.PHONY: play
play:
	python3 App.py