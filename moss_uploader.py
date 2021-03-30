import subprocess
import os
import re
import requests
from bs4 import BeautifulSoup
import pdfkit


def pull_page(original_url, url):
	similarity_page = requests.get(url)
	soup = BeautifulSoup(similarity_page.content, "html.parser")
	frames = soup.find_all("frame")
	print(frames)
	for frame in frames:
		subprocess.call(["wget", "--recursive", "-P",  "./documents", original_url +'/'+ frame.attrs['src']])

input_text = input("Enter 1 to enter a project name, or 2 to enter a canvas link: ")
if(input_text == '1'):
	##language = input("Enter a language: ")
	files = input("Enter the project name: ") ## add functionality for setting filepath

	##call(["extract.py", ])
	current_directory = os.getcwd()
	files = current_directory + '/' + files + '/*.py' ## alias this in the future for various languages

	string = subprocess.check_output(["bash", "caller.sh", files])
	string = string.split()
	url = str(string[len(string)-1])
	url = url[2:len(url)-1]
	print(url)

	moss_url = url
	moss_page = requests.get(moss_url)

	##print(moss_page.status_code, moss_page.headers)

	soup = BeautifulSoup(moss_page.content, "html.parser")
	links = soup.find_all("a")
	file_num = int(0)
	existing_links = []
	for link in links:										##this pulls each link from the landing page
		if "moss" in link.text:		##this is how we'll take only a certain percent as well
			split_link = re.split('\(|%', str(link.text))
			sim_percent = split_link[1]
			print(sim_percent)
			if(sim_percent > 50):
				pull_page(moss_url, link.attrs['href'])


elif(input_text == '2'):
	url = "https://elearning.mines.edu/courses/29030/assignments/194158"
	canvas_page = requests.get(url)
	soup = BeautifulSoup(canvas_page.content, "html.parser")
	links = soup.find_all("a")
	print(soup)
	#with open("assignments.zip", "wb") as file:
	#	file.write(canvas_page.content)
