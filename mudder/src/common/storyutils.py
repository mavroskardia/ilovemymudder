def remove_articles(words):	
	a = list(words)
	for art in ('a', 'an', 'the'):
		if art in a:
			a.remove(art)
	return ' '.join(a)
	

if __name__ == '__main__':
	new = remove_articles(['order', 'a', 'whisky'])
	print(new)