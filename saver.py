import os
import sys
import time
import reddit
from urllib import urlretrieve, urlopen

def write_queue(queue):
    output_file = open('links.markdown', 'w')
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
            # case 1 - link already points to the image
            if 'i.imgur.com' in link.url:
                print '%s %s' % (link.url, link.title)
                # find out extension
                ext = url_extension(link.url)
                # if the file exists, skip it
                if os.path.isfile('downloads/%s.%s' % (link.title, ext)):
                    continue
                # download
                urlretrieve(link.url, 'downloads/%s.%s' % (link.title, ext),
                            reporthook = dl_progress)
            # case 2 - link points to an album
            elif '/a/' in link.url:
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
            # case 3 - link points to imgur page
            elif 'imgur.com/' in link.url:
                print '%s %s' % (link.url, link.title)
                # transform the link to point at the image
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
    sys.stdout.write('\r%2d%% [%d/%d]' % (percent, count*blockSize, totalSize))
    sys.stdout.flush()

def url_extension(url):
    f = urlopen(url)
    ext = f.info().type
    ext = ext[ext.index('/') + 1:]
    return ext

def main():
    # api setup
    api = reddit.Reddit(user_agent='saver')
    api.login()
    # saved links and num of saved links
    queue = []

    # read saved links from reddit
    try:
        print 'Reading saved links...'
        for link in api.get_saved_links(None):
            link.title = '[%s]' % link.title
            queue.append(link)
    except:
        raise
        print '\nSomething went wrong... Sorry'
        return 1

    # write saved links to a file
    print 'Writing links to file...'
    write_queue(queue)
    print 'Recognized and wrote %d links.' % len(queue)

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
