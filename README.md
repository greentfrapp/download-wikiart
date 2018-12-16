# download-wikiart

Download artworks from https://www.wikiart.org/ by artist.

## Instructions

Go to https://www.wikiart.org/ and find the desired artist, as well as how the name is represented in the URL.

The represented name in the URL is typically the artist's name in small caps and separated by dashes. For instance, Rembrandt's profile page is https://www.wikiart.org/en/rembrandt, so his name is simply `rembrandt`. Van Gogh's profile is https://www.wikiart.org/en/vincent-van-gogh, so his name is `vincent-van-gogh`.

Next, just run the following command, replacing `<artist-name>` with the represented name.

```
python3 main.py --artist=<artist-name>
```

For example:

```
python3 main.py --artist=vincent-van-gogh
```

A Chromium browser should launch and scroll through the artist's gallery to gather the artworks' URLs then proceed to download the artworks into a local folder.
