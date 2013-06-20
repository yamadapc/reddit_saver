import sys
import time
import reddit
from reddit.objects import Redditor, Submission

sites = ('imgur', 'youtube',)

class saved():
    def __init__(self, title = '', url = ''):
        self.title = title
        self.url = url
        for s in sites:
            if s in self.url:
                self.site = s
                return
        self.site = 'unknown'

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
        print 'Reading saved links...'
        for link in api.get_saved_links(10):
            queue.append(link)
            save_count += 1
    except:
        print '\nSomething went wrong... Sorry'
        raise
        return 1

    # write saved links to a file
    try:
        print 'Writing links to file...'
        write_queue(queue)
    except:
        print '\nSomething went wrong... Sorry'
        raise
        return 2
    finally:
        print 'Recognized and wrote %d links.' % save_count

    # analyse file and prompt user for download selections
    l_by_sites = { 'imgur': 0, 'youtube': 0, 'unknown': 0,}
    links_file = open('links', 'r')
    lines = links_file.readlines()

    for i in range(0, len(lines), 3):
        link = saved(lines[i], lines[i+1])
        l_by_sites[link.site] += 1

    print 'I found',
    for site, nl in l_by_sites.items():
        print '%d %s links' % (nl, site),
    links_file.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
