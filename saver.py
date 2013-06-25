import os
import sys
import time
import reddit
from urllib2 import urlopen, URLError, HTTPError

def write_queue(queue):
    output_file = open('links', 'w')
    for link in queue:
        output_file.write(link.__unicode__() + '\n')
        output_file.write(link.url + '\n')
        output_file.write('-'*79 + '\n')
    output_file.close()

def retrieve(do, queue):
    if not os.path.exists('downloads'):
        print 'Downloads directory doesn\'t exists, creating it...'
        os.makedirs('downloads')

    if do == 'imgur':
        retrieving = [link for link in queue if 'imgur' in link.url]
        c_link = 1
        for link in retrieving:
            print 'Get:%d' % (c_link),
            # case 1 - link already points to the image
            if 'i.imgur.com' in link.url:
                print '%s [%s]' % (link.url, link.title)
                # find out extension - right now I have no idea on how to do it
                # for all possible cases
                if 'gif' in link.url:
                    ext = '.gif'
                else:
                    ext = '.jpg'
                # download
                download_file(link.url, 'downloads/%s%s' % (link.title, ext))
            # case 2 - link points to an album
            elif '/a/' in link.url:
                print '%s [%s] (album)' % (link.url, link.title)
                # transform the link to point at the zip
                try:
                    i = link.url.index(':') + 3
                    link.url = 'http://s.%s/zip' % link.url[i:]
                except:
                    print 'Error: %s probably is an invalid link' % link.url
                # download zip
                download_file(link.url, 'downloads/%s.zip' % link.title)
            else:
                print '\rError:%d' % (c_link),
                print '%s [%s]' % (link.url, link.title)
            c_link += 1

def download_file(url, name):
    try:
        f = urlopen(url)
        # write to local file
        with open(name, 'wb') as local_f:
            local_f.write(f.read())
    except HTTPError, e:
        print 'HTTPError:', e.code, url
    except URLError, e:
        print 'URLError:', e.reason, url

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

    print 'I\'ve found',
    for site, nl in l_by_sites.items():
        print '%d %s links' % (nl, site),
    print

    # ask user what to do
    what_to_do = raw_input('\
Type the sites you want me to retrieve from, \
i for all retrievable images or \
v for all retrievable videos: ').split()
    for do in what_to_do:
        retrieve(do, queue)

    return 0

if __name__ == '__main__':
    sys.exit(main())
