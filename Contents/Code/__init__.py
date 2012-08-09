from BeautifulSoup import BeautifulStoneSoup as BSS

RSS_FEED = 'http://blog.catspawimages.com/feed'
PHOTO_NS = {'c':'http://purl.org/rss/1.0/modules/content/'}

####################################################################################################
def Start():
  Plugin.AddPrefixHandler("/photos/catspawimages", PhotoMenu, "Cat's Paw Images", 'icon-default.png', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("Images", viewMode="Pictures", mediaType="items")
  ObjectContainer.title1 = "Cat's Paw Images"
  ObjectContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(3600*3)

####################################################################################################
def UpdateCache():
  HTTP.Request(RSS_FEED)

####################################################################################################
def PhotoMenu():
  oc = ObjectContainer(title2="Photos")
  for item in XML.ElementFromURL(RSS_FEED).xpath('//item'):
    title = item.find('title').text
    summary = item.xpath('description')[0].text.replace('<p>','').replace('</p>','').replace('<br />',"\n").replace(' [...]', '...')
    soup = BSS(summary, convertEntities=BSS.HTML_ENTITIES) 
    summary = soup.contents[0]
    date = Datetime.ParseDate(item.find('pubDate').text).strftime('%a %b %d, %Y')
    try: thumb = FindPhotos(item.xpath('c:encoded', namespaces=PHOTO_NS)[0].text)[0]
    except: continue
    key = item.find('link').text
    oc.add(PhotoAlbumObject(key=Callback(PhotoList, key=item.find('link').text, title=title), title = title, thumb = thumb, url = key))
    
  return oc
  
####################################################################################################
def PhotoList(key, title):
  oc = ObjectContainer(title2=title)
  image = 1
  for item in HTML.ElementFromURL(key).xpath('//img'):
    if item.get('src').find('static.flickr.com') != -1:
      oc.add(PhotoObject(url = item.get('src'), title=item.get('alt'), summary=item.get('alt'), thumb=item.get('src'),
              items = [
                MediaObject(parts = [ PartObject(key=item.get('src')) ])
              ]))
      image += 1
  return oc

####################################################################################################
def FindPhotos(html):
  code = HTML.ElementFromString(html)
  return [i.get('src') for i in code.xpath('//img')]