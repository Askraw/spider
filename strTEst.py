def filenToId(filename):
    index=filename.index('_')
    index2=filename.index('.')
    print(filename[0:index])
    print(filename[index+1:index2])
 
filenToId('lalala_123.txt')