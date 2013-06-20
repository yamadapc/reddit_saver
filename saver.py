import sys
import time
import reddit
from reddit.objects import Redditor, Submission

def write_queue(queue):
    output_file = open('links', 'w')
    for link in queue:
        output_file.write(link.__unicode__() + '\n')
        output_file.write(link.url + '\n')
        output_file.write('-'*79 + '\n')
    output_file.close()

def main():
    # api setup
    api = reddit.Reddit(user_agent='saver')
    api.login()
    # saved links and num of saved links
    queue = []
    save_count = 0

    # read saved links from reddit
    try:
        print 'Reading saved links...',
        for link in api.get_saved_links(10):
            queue.append(link)
            save_count += 1
    except:
        print '\nSomething went wrong... Sorry'
        raise
        return 1

    # write saved links to a file
    try:
        print 'Writing links to file...',
        write_queue(queue)
    except:
        print '\nSomething went wrong... Sorry'
        raise
        return 2

    # analyse file and prompt user for download selections [TODO]

    return 0

if __name__ == '__main__':
    sys.exit(main())
