SRILM_LIBS=/fs/clip2/Programs/SRI-LM/Linux/current/lib/i686/
SRILM_INC=/fs/clip2/Programs/SRI-LM/Linux/current/include
PYTHON_INC=/usr/local/stow/Python-2.4/include/python2.4
PERL_INC=/usr/lib/perl5/5.8.0/i386-linux-thread-multi/CORE

python: clean _srilm.so

_srilm.so: srilm.o srilm_python_wrap.o
	g++ -shared $^ -loolm -ldstruct -lmisc -L$(SRILM_LIBS) -o $@

srilm_python_wrap.o: srilm_python_wrap.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) -I$(PYTHON_INC)

srilm_python_wrap.c: srilm_python.i
	swig -python $<

perl: clean srilm.so

srilm.so: srilm.o srilm_perl_wrap.o
	g++ -shared $^ -loolm -ldstruct -lmisc -L$(SRILM_LIBS) -o $@

srilm_perl_wrap.o: srilm_perl_wrap.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) -I$(PERL_INC)

srilm_perl_wrap.c: srilm_perl.i
	swig -perl $<

srilm.o: srilm.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) -I$(PYTHON_INC)

clean:
	\rm -fr srilm.o srilm_*_wrap.* *.so srilm.py* srilm.pm
