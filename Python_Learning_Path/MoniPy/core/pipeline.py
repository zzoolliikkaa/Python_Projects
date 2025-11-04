from monipy.io.fetch import smart_fetch

html = smart_fetch(url)
print(html[:5000])
