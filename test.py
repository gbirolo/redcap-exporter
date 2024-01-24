from redcap_exporter.convert import convert

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        import os

        testdir = 'redcap_exporter/tests'
        for input_csv in os.listdir(testdir):
            print('TEST:', input_csv)
            convert(testdir + '/' + input_csv, 'last-test.xlsx')
    else:
        convert(sys.argv[1], sys.argv[2])