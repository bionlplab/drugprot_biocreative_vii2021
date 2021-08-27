import tempfile

if __name__ == '__main__':
    tempdir = tempfile.gettempdir()
    print(tempdir)