# AMsources2text
Code to extract text with some structure from Ars Magica sourcebooks

It started as a project to get character (monsters, magi, creatures etc.) statistics from sourcebooks to be added to a compendium for [Ars Magica module for Foundry VTT](https://github.com/Xzotl42/arm5e). But parsing the PDFs was not that simple. So I dug deeper into PDFs to get more useful information about the text. At some point I realized that code could also be used to get the text with headings and contents of sidebar boxes separated from main text.
It's not perfect. Sometimes headings in sidebars go in wrong order and some headings in the text are not recognized, but main structure of the text is pretty good. Lots of details like tables, bold or italics text, indentation etc. is ignored. I don't need it with character statistics and getting them would require lots of work and a even deeper dive in into PDFs structure.

Text structure is simple. Parts of text are marked in HTML like fashion
There are four levels of headings h1-h4 marked with `<h1>HTML-tags</h1>`
`<div>Text is marked with div-tags</div>` and `<sidebar>contents of sidebars are inside sidebar-tags</sidebar>`
That's it

Text is put to file page by page. Main text is first and then sidebar section if there is one. There are no page endings or startings. Regular text is split in divs as pymupdf-library gives it. Extra white space is removed and words split to two lines with hyphen are combined. I cannot promise that words that naturally have hyphen are treated right. 

PDF's are read from a folder (`--filepath`) and written to a folder (`--outpath`), both given as command line parameter. Command to run the scripts is something like
`python parse_pdf.py --filepath="collection\of\pdfs" --outpath="where\to\put\text\files"`

Script goes through all pdf files on given --filepath. Opens them one by one, parses text from them and writes text to files in --outpath folder. Filename is taken from source file by replasing .pdf or .PDF with .txt, so Ars_sourcebook.pdf becomes Ars_sourcebook.txt. If there is already a file with same name in the --output folder it is overwritten.

Datastructure book_settings in book_data.py file is used with text parsing. Official filename of sourcebook is used as key. If your files have different names the you need to edit those names in book_settings. headers contain list of header texts used in the sourcebook. Headers are in top middle of most of pages. Limist.start is the first page to read text from. Note: As usual numbering of a list (of pages in pdf) starts from zero, so add one to it to get corresponding page in the sourcebook. It is set to drop front cover, credits and table of content. Ignore_images list contains large or whole page background images in the file. When parsing a page of a sourcebook, script collects images on the page, but images on the ignore_images list are dropped out. Rest is illustrations and images for sidebar texts. Actually bounding boxes for images are collected and texts inside sidebars are then texts that are inside a bounding box of an image. Rest of the values are for extracting character statistics. So for text extraction you need name of the file (key), ignore_images and headers. Optionally you can set limits.start to drop pages from the start. NOTE: Credits should be okish, front cover is an image and there is no text and table of contents will look pretty ugly, but without page numbers on the text it is quite useless.
PLEASE don't add information of sourcebooks that are not under open licence to book_settings and use filenames of the original source.

NOTE this is not a generic PDF reader. It is fitted to parse official Ars Magica sourcebooks. It relies on commonalities among those sourcebooks. Commonalities the script relies on are:
* fonts used in headings of the books
* how different fonts are used
* Sidebar texts are set on top of an image
* Usage of headers
