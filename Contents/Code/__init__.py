from BeautifulSoup import BeautifulStoneSoup as BSS

RSS_FEED = 'http://blog.catspawimages.com/feed'
PHOTO_NS = {'c':'http://purl.org/rss/1.0/modules/content/'}

TITLE = "Cat's Paw Images"
ICON  = "icon-default.png"
ART   = "art-default.jpg"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler("/photos/catspawimages", PhotoMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("Images", viewMode="Pictures", mediaType="items")

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  HTTP.SetCacheTime(3600 * 3)

####################################################################################################
def PhotoMenu():
  oc = ObjectContainer(title2 = "Photos")

  for item in XML.ElementFromURL(RSS_FEED).xpath('//item'):

    url = item.find('link').text
    title = item.find('title').text
    date = Datetime.ParseDate(item.find('pubDate').text)

    thumb = R(ICON)
    try: thumb = FindPhotos(item.xpath('c:encoded', namespaces=PHOTO_NS)[0].text)[0]
    except: continue

    summary = item.xpath('description')[0].text.replace('<p>','').replace('</p>','').replace('<br />',"\n").replace(' [...]', '...')
    soup = BSS(summary, convertEntities=BSS.HTML_ENTITIES) 
    summary = soup.contents[0]

    # Technically, I should use the url parameter of the PhotoAlbumObject to perform a service lookup.
    # However, this currently introduces a 
    oc.add(PhotoAlbumObject(
      key = Callback(PhotoList, url = url, title = title), 
      rating_key = url,
      title = title, 
      thumb = thumb,
      originally_available_at = date))
    
  return oc
  
####################################################################################################
def PhotoList(url, title):
  oc = ObjectContainer(title2=title)

  for item in HTML.ElementFromURL(url).xpath('//img'):
    if item.get('src').find('static.flickr.com') != -1:
      
      url = item.get('src')
      title = item.get('alt')
      oc.add(PhotoObject(
        key = Callback(GetPhotoDetails, url = url, title = title),
        rating_key = url,
        title = title,
        summary = title,
        thumb = url,
        items = [ MediaObject(parts = [ PartObject(key = url) ]) ]))

  return oc

####################################################################################################
def GetPhotoDetails(url, title):
  oc = ObjectContainer()
  oc.add(PhotoObject(
    key = Callback(GetPhotoDetails, url = url, title = title),
    rating_key = url,
    url = url,
    title = title,
    summary = title,
    thumb = url,
    items = [ MediaObject(parts = [ PartObject(key = url) ]) ]))
  return oc

####################################################################################################
def FindPhotos(html):
  code = HTML.ElementFromString(html)
  return [i.get('src') for i in code.xpath('//img')]