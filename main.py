import asyncio
from pyppeteer import launch
import urllib3
from bs4 import BeautifulSoup
import requests
from progress.bar import IncrementalBar
import os
from absl import flags

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FLAGS = flags.FLAGS
flags.DEFINE_bool('artist', 'vincent-van-gogh', 'Artist name, as recorded in WikiArt')

async def extract_total(page):
	element = (await page.xpath('//span[contains(string(@class), "count")]'))[0]
	count_string = (await page.evaluate('(element) => element.textContent', element))
	total_count = int(count_string.split(' ')[-1])
	current_count = int(count_string.split(' ')[0].split('-')[-1])
	while(current_count < total_count):
		await page.click('a.masonry-load-more-button')
		await page.waitFor(500)
		element = (await page.xpath('//span[contains(string(@class), "count")]'))[0]
		count_string = (await page.evaluate('(element) => element.textContent', element))
		total_count = int(count_string.split(' ')[-1])
		current_count = int(count_string.split(' ')[0].split('-')[-1])

async def extract_urls(page):
	elements = await page.xpath('//ul[contains(string(@class),"painting-list-text")]/li/a')
	urls = []
	for element in elements:
		url = await page.evaluate('(element) => element.href', element)
		if url.startswith('https://www.wikiart.org'):
			urls.append(url)
	return urls

async def main(artist):
	browser = await launch({'headless': False})
	page = await browser.newPage()
	await page.goto('https://www.wikiart.org/en/{}/all-works#!#filterName:all-paintings-chronologically,resultType:text'.format(artist))
	await page.waitForSelector('ul.painting-list-text')
	await extract_total(page)
	urls = await extract_urls(page)
	print('{} URLs extracted...'.format(len(urls)))
	await browser.close()
	img_urls = []
	bar = IncrementalBar('Extracting image URLs...', max=len(urls))
	with open('{}.txt'.format(artist), 'w') as file:
		file.write('')
	for i, url in enumerate(urls):
		http = urllib3.PoolManager()
		response = http.request('GET', url)
		soup = BeautifulSoup(response.data, 'html.parser')
		img_url = soup.find('img', attrs={'class': 'ms-zoom-cursor'})['src'].split('!')[0]
		img_urls.append(img_url)
		with open('{}.txt'.format(artist), 'a') as file:
			file.write(img_url + '\n')
		bar.next()
	bar.finish()
	bar = IncrementalBar('Downloading images...', max=len(img_urls))
	if not os.path.isdir(artist):
		os.mkdir(artist)
	for i, img_url in enumerate(img_urls):
		img_data = requests.get(img_url).content
		with open('{}/'.format(artist) + img_url.split('/')[-1], 'wb') as handler:
			handler.write(img_data)
		bar.next()
	bar.finish()

def resume(artist):
	img_urls = []
	with open(artist + '.txt', 'r') as file:
		for line in file:
			img_urls.append(line.strip('\n'))
	completed = os.listdir('./' + artist)
	bar = IncrementalBar('Downloading images...', max=len(img_urls) - len(completed))
	quit()
	for i, img_url in enumerate(img_urls):
		if img_url.split('/')[-1] not in completed:
			img_data = requests.get(img_url).content
			with open('{}/'.format(artist) + img_url.split('/')[-1], 'wb') as handler:
				handler.write(img_data)
			bar.next()
	bar.finish()

asyncio.get_event_loop().run_until_complete(main(FLAGS.artist))
