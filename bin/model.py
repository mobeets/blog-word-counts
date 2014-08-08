import re
import sys
import urllib2
from xml.dom import minidom
from datetime import datetime

BLOGGER_RSS_FORMAT = '{0}/feeds/posts/default'
OTHER_RSS_FORMAT = '{0}/rss'
OTHER_RSS_FORMAT_2 = '{0}/feed'
def get_feed(base_url):
    if 'http' not in base_url:
        base_url = 'http://' + base_url
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    try:
        url = BLOGGER_RSS_FORMAT.format(base_url)
        return get_feed_from(url)
    except:
        try:
            url = OTHER_RSS_FORMAT.format(base_url)
            return get_feed_from(url)
        except:
            url = OTHER_RSS_FORMAT_2.format(base_url)
            return get_feed_from(url)
    return get_feed_from(base_url)

def get_feed_from(url):
    file_request = urllib2.Request(url)
    file_opener = urllib2.build_opener()
    file_feed = file_opener.open(file_request).read()
    file_xml = minidom.parseString(file_feed)
    return file_xml

def get_data_using_tag(T, post):
    data = ''
    try:
        data = post.getElementsByTagName(T)[0].firstChild.data
    except:
        pass
    return data

def get_next_page(xml):
    xml = xml.getElementsByTagName('feed')
    links = xml[0].getElementsByTagName('link')
    links = [link.getAttribute('href') for link in links if link.hasAttributes() and link.getAttribute('rel')=='next']
    if links:
        return links[0]
    else:
        return ''
    
def parse_blogger_feed(xml):
    parsed_posts = []
    P = read_page(xml)
    for x in P:
        parsed_posts.append(x)
        
    next_page_url = get_next_page(xml)
    while next_page_url:
        xml = get_feed_from(next_page_url)
        P = read_page(xml)
        for x in P:
            parsed_posts.append(x)
        next_page_url = get_next_page(xml)    
        #print 'Found next page: ' + next_page_url
    return parsed_posts

def parse_tumblr_feed(xml):
    try:
        posts = xml.getElementsByTagName("item")
        parsed_posts = []
        for post in posts:
            out = get_data_using_tag("pubDate", post)
            published = reformat_tumblr_date(out)
            title = get_data_using_tag("title", post)
            content = get_data_using_tag("description", post)  
            parsed_posts.append((published , title.encode('utf-8') , content.encode('utf-8') ))
        return parsed_posts
    except:
        return []
            
def read_page(xml):
    try:
    #if True:
        xml = xml.getElementsByTagName("feed")
        posts = xml[0].getElementsByTagName("entry")
        parsed_posts = []
        for post in posts:
            published = reformat_date_string(get_data_using_tag("published", post)) 
            title = get_data_using_tag("title", post)
            content = get_data_using_tag("content", post)    
            parsed_posts.append((published , title.encode('utf-8') , content.encode('utf-8') ))
        return parsed_posts
    except:
        return [] #print 'The feed could not read properly.'

def reformat_tumblr_date(date):
    tmp = date.split(' ')
    dd = int(tmp[1])
    mm = get_month_from_name(tmp[2])
    yy = int(tmp[3])
    return datetime(yy,mm,dd) #str(datetime(yy,mm,dd)).split(' ')[0]

def reformat_date_string(date):
    d = date.split('T')[0]
    yy,mm,dd = d.split('-')
    yy = int(yy)
    mm = int(mm)
    dd = int(dd)
    return datetime(yy,mm,dd) # date.split('T')[0]

def remove_html_tags(data):
     p = re.compile(r'<.*?>')
     return p.sub('', data)

def count_words_in(data):
    post_words = re.sub('[^ a-zA-Z]+','',data) # only save letters and spaces
    wc = len(post_words.split())
    return wc

def get_word_counts_of_posts_in(base_url):
    xml = get_feed(base_url)
    items = []
    try:
        items = parse_blogger_feed(xml)
    except:
        items = parse_tumblr_feed(xml)
    word_counts = {}
    for item in items:
        (dt, title, content) = item
        content = remove_html_tags(content)
        wc = count_words_in(content)
        word_counts[dt] = (wc, title)
    return word_counts

def get_month_from_name(mm):
    month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sept':9,'Oct':10,'Nov':11,'Dec':12}
    for a in month_map:
        if mm in a:
            return month_map[a]

def get_sorted_word_counts_of_posts_in(base_url):
    wcs = get_word_counts_of_posts_in(base_url)
    if wcs is None:
        return []
    data = []
    for dt in wcs:
        data.append((dt, wcs[dt][0], wcs[dt][1]))
    return data
          
def main():
    base_url = sys.argv[1] #'focusedconsumers'
    wcs = get_word_counts_of_posts_in(base_url)
    if wcs != None:
        print base_url + ' has made ' + str(len(wcs)) + ' posts: '
        print '++++++++' 
        for date in wcs: #sorted_dates:
            wc = wcs[date][0]
            title = wcs[date][1]
            print title + ' : ' + str(date) + ' : ' + str(wc)

if __name__ == "__main__":
     main()     
