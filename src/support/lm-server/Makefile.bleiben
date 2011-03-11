SRILM_LIBS=/home/lefterav/tools/srilm/lib/i686
SRILM_INC=/home/lefterav/tools/srilm/include
PYTHON_INC=/usr/include/python2.6

all: clean _srilm.so

_srilm.so: srilm.o srilm_python_wrap.o
	g++ -shared $^ -loolm -ldstruct -lmisc -L$(SRILM_LIBS) -o $@

srilm_python_wrap.o: srilm_python_wrap.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) -I$(PYTHON_INC)

srilm_python_wrap.c: srilm_python.i
	swig -python $<

srilm.o: srilm.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) -I$(PYTHON_INC)

clean:
	\rm -fr srilm.o srilm_*_wrap.* *.so srilm.py* srilm.pm
