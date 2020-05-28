
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))
DESTDIR := $(abspath $(current_dir)../bin)

all:
	@echo "Run 'make install'"

gsaraman:
	cd .. && pip install --upgrade -t ${DESTDIR} .

install:
	. /etc/environ.sh; use -e -r anaconda3-5.1; $(MAKE) gsaraman

clean:
	rm -rf ${DESTDIR}/*.dist-info

distclean: clean
	rm -rf ${DESTDIR}/bin
	rm -rf ${DESTDIR}/gsaraman*

.PHONY: all gsaraman install clean distclean
