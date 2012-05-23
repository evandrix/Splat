import dis,tempfile,sys,os

def diff_funcs(f1,f2):
    file1 = tempfile.mktemp()
    file2 = tempfile.mktemp()

    svstdout = sys.stdout

    try:
        sys.stdout = open(file1, 'w')
        dis.dis(f1)

        sys.stdout = open(file2, 'w')
        dis.dis(f2)

        sys.stdout = svstdout

        os.system("diff -y %s %s"%(file1,file2))
    finally:
        sys.stdout = svstdout
        os.unlink(file1)
        os.unlink(file2)

