from time import sleep


def print_progress_bar (iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    if iteration == total:
        print()


for i in range(1, 31):
    sleep(0.1)
    print_progress_bar(i, 30)
