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
        print 'Reading saved links...'
        for link in api.get_saved_links(10):
            queue.append(link)
            save_count += 1
    except:
        raise
        print '\nSomething went wrong... Sorry'
        return 1

    # write saved links to a file
    try:
        print 'Writing links to file...'
        write_queue(queue)
    except:
        raise
        print '\nSomething went wrong... Sorry'
        return 2
    finally:
        print 'Recognized and wrote %d links.' % save_count

    # analyse links
    l_by_sites = { 'imgur': 0, 'youtube': 0, 'unknown': 0,}
    site_of = {}
    for link in queue:
        site_of[link.url] = 'unknown'
        for site in l_by_sites:
            if site in link.url:
                site_of[link.url] = site

    for site in site_of.values():
       l_by_sites[site] += 1

    print 'I found',
    for site, nl in l_by_sites.items():
        print '%d %s links' % (nl, site),
    print

    return 0

if __name__ == '__main__':
    sys.exit(main())
