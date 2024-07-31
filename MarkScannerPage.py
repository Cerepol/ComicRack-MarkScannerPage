# MarkScannerPage.py
#
# Marks scanner page as deleted pagetype
#
# You are free to modify and distribute this file
##########################################################################
from __future__ import print_function
from System.IO import Path


import clr
clr.AddReferenceByPartialName('ComicRack.Engine')
from cYo.Projects.ComicRack.Engine import ComicPageType

markScannerAs = ComicPageType.Deleted

# routine copied from https://gist.github.com/mxu007/4209efa6d6e79e3bce17ab6ce5679fb9#file-lcp_1-py
def longestCommonPrefix(strs):
    longest_pre = ""
    if not strs: return longest_pre
    shortest_str = min(strs, key=len)
    for i in range(len(shortest_str)):
        if all([x.startswith(shortest_str[:i+1]) for x in strs]):
            longest_pre = shortest_str[:i+1]
        else:
            break
    return longest_pre

def getPageNameList(pages, imgProvider):
	pageNameList = []
	
	#print "PageInfos: " + str(pages.Count)
	#imgProvider = book.OpenProvider(book.Pages.Count)
#	for page in book.Pages:
	for page in pages:
		imgInfo = imgProvider.GetImageInfo(page.ImageIndex)
		#print imgInfo
		filename = Path.GetFileName(imgInfo.Name)
		pageNameList.append(filename)
	
	print(pageNameList)
	return pageNameList

# this routine copied from 
# https://github.com/mylar3/mylar3/blob/python3-dev/lib/comictaggerlib/comicapi/comicarchive.py#L733 and
# https://github.com/comictagger/comictagger/blob/develop/comicapi/comicarchive.py#L749 
# and then modified
def getScannerPage(book):
	scanner_page_index = None

	#Get the comicbook navigator to retrieve live archive info
	nav = book.CreateNavigator()
	pages = nav.GetPageInfos()
	
	# make a guess at the scanner page
	#count = book.Pages.Count #BAD asking the books ComicInfo for pages can return non-updated info
	count = pages.Count
	imgProvider = book.OpenProvider(count)
	print("PageCount: " + str(count))
	
	if count <= 0:
		print('{0} returned zero page count. Marking not run.'.format(book.Caption))

	# too few pages to really know
	if count < 5:
		print('{0} returned fewer than 5 pages ({1} pages reported). Not enough to find scanner page reliably.'.format(book.Caption, count))
		return None

	name_list = getPageNameList(pages, imgProvider)

	# count the length of every filename, and count occurences
	length_buckets = dict()
	for name in name_list:
		length = len(name)
		if length in length_buckets:
			length_buckets[length] += 1
		else:
			length_buckets[length] = 1

	# sort by most common
	sorted_buckets = sorted(
		iter(length_buckets.items()),
		key=lambda k_v: (
			k_v[1],
			k_v[0]),
		reverse=True)

	# statistical mode occurence is first
	mode_length = sorted_buckets[0][0]

	# we are only going to consider the final image file:
	print("NameList length: " + str(len(name_list)))
	print("Count-1 " + str(count-1))
	final_name = name_list[count - 1]
	print("FinalName: " + final_name)
	
	common_length_list = list()
	for name in name_list:
		if len(name) == mode_length:
			common_length_list.append(name)

	prefix = longestCommonPrefix(common_length_list)

	if mode_length <= 7 and prefix == "":
		# probably all numbers
		if len(final_name) > mode_length:
			scanner_page_index = count - 1

	# see if the last page doesn't start with the same prefix as most
	# others
	elif not final_name.startswith(prefix):
		scanner_page_index = count - 1

	print(scanner_page_index)
	if scanner_page_index:
		return pages, pages[scanner_page_index]
		#return book.Pages[scanner_page_index]
	else:
		return pages, None

#@Name	Mark scanner page
#@Hook	Books
#@Description Mark scanner page as deleted
#@Image scan-icon.png
def MarkScannerPage(books):
	for book in books:

		pages, scanner_page = getScannerPage(book)
		#Since the comic might have bad ComicInfo (especially if unopened)
		#Get the books info, update the pages and save it back before marking the deleted page
		ci = book.GetInfo()
		#print(ci)
		ci.SetPages(pages)
		book.SetInfo(ci)
		if scanner_page and scanner_page.PageType != markScannerAs:
			print('unmarked scanner page found in {0}. Setting to {1}'.format(book.Caption, markScannerAs))
			book.UpdatePageType(scanner_page, markScannerAs)

