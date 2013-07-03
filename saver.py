"""Reddit Saver

Usage: 
  saver.py
  saver.py -u <user> [-p <password>]
  saver.py -o <output> | [-l <links>]
  saver.py -h | --help

Fetch saved posts links or read them from a file and try to download their
content.

Arguments:
  -u --user <user>           specify username
  -p --password <password>   specify password (not recomended)
  -l --links <links>         read links from file [default: ./links.markdown]
  -o --output_file <output>  write links to file [default: ./links.markdown]

Options:
  -h --help                show this screen

"""

import os
import sys
import time
import reddit
import getpass
from re import escape
from urllib import urlretrieve, urlopen
from docopt import docopt

def get_queue(username = None, password = None):
    # api setup
    api = reddit.Reddit(user_agent='saver')
    api.login(username, password)
    # saved links and num of saved links
    queue = []

    # read saved links from reddit
    try:
        print 'Reading saved links...'
        for link in api.get_saved_links(None):
            link.title = '[%s]' % link.title
            link.title = link.title.replace('/', '-') # escapes names with '/'
            queue.append(link)
    except:
        raise
        print '\nSomething went wrong... Sorry'
        return 1

    return queue

def write_queue(queue, output_file_name):
    output_file = open(output_file_name, 'w')
    for link in queue:
        output_file.write('# %s\n' % link.__unicode__())
        output_file.write('<%s>\n' % link.url)
        output_file.write('* * *\n\n')
    output_file.close()

def retrieve(do, queue):
    if not os.path.exists('downloads'):
        print 'Downloads directory doesn\'t exists, creating it...'
        os.makedirs('downloads')

    if do == 'imgur':
        retrieving = [link for link in queue if 'imgur' in link.url]
        c_link = errors = 0
        for link in retrieving:
            c_link += 1
            print ' '*80+'\r',
            print 'Get:%d' % (c_link),

            # case 1 - link points to an album
            if '/a/' in link.url:
                print '%s %s (album)' % (link.url, link.title)
                # transform the link to point at the zip
                i = link.url.index(':') + 3
                link.url = 'http://s.%s/zip' % link.url[i:]
                # if the file exists, skip it
                if os.path.isfile('downloads/%s.zip' % link.title):
                    continue
                # download zip
                urlretrieve(link.url, 'downloads/%s.zip' % link.title,
                            reporthook = dl_progress)

            # case 2 - link points to the image
            if 'imgur.com/' in link.url:
                print '%s %s' % (link.url, link.title)
                if 'i.imgur' not in link.url:
                    #transform the linkn to point at the image
                    i = link.url[-1::-1].index('/')
                    link.url = 'http://imgur.com/download/%s' % link.url[-i:]
                # find out extension 
                ext = url_extension(link.url)
                # if the file exists, skip it
                if os.path.isfile('downloads/%s.%s' % (link.title, ext)):
                    continue
                # download
                urlretrieve(link.url, 'downloads/%s.%s' % (link.title, ext),
                            reporthook = dl_progress)
            else:
                print ' '*80+'\r',
                print 'Error:%d %s %s' % (c_link, link.url, link.title)
                errors += 1
        print ' '*80+'\r',
        print 'Fetched %d imgur links successfully.' % (c_link - errors)

def dl_progress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    totalSize /= 1000
    blockSize /= 1000
    sys.stdout.write('\r%2d%% [%d/%d]' % (percent, count*blockSize, totalSize))
    sys.stdout.flush()

def url_extension(url):
    f = urlopen(url)
    ext = f.info().type
    ext = ext[ext.index('/') + 1:]
    return ext

def main():
    # get arguments
    arguments = docopt(__doc__)
    user = arguments['<user>']
    password = arguments['<password>']
    links_file_name = arguments['<links>']
    output_file_name = arguments['<output>']

    # ask for the password if username was provided without it
    if user and not password:
        print 'Username: %s' % user
        password = getpass.getpass('Password for %s: ' % user)

    if not links_file_name: links_file_name = 'links.markdown'
    if not output_file_name: output_file_name = 'links.markdown'

    # fetch queue from reddit
    if not arguments['-l']:
        queue = get_queue(user, password)

        # write saved links to a file
        print 'Writing links to %s...' % output_file_name
        write_queue(queue, output_file_name)
        print 'Recognized and wrote %d links.' % len(queue)
    # fetch queue from file
    else:
        print 'This option is still under development, sorry...'
        return -1

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
