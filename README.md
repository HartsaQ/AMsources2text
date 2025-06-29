# AMsources2text
Code to extract text with some structure from Ars Magica sourcebooks

# LEGALESE

Based on the material for Ars Magica, ©1993–2024, licensed by Trident, Inc. d/b/a Atlas Games®, under Creative Commons Attribution-ShareAlike 4.0 International license 4.0 ("CC-BY-SA 4.0")

Ars Magica Open License Logo ©2024 Trident, Inc. The Ars Magica Open License Logo, Ars Magica, and Mythic Europe are trademarks of Trident, Inc., and are used with permission.

Order of Hermes, Tremere, Doissetep, and Grimgroth are trademarks of Paradox Interactive AB and are used with permission.

## Project description

It started as a project to get character (monsters, magi, creatures etc.) statistics from sourcebooks to be added to a compendium for [Ars Magica module for Foundry VTT](https://github.com/Xzotl42/arm5e). But parsing the PDFs was not that simple. So I dug deeper into PDFs to get more useful information about the text. At some point I realized that code could also be used to get the text with headings and contents of sidebar boxes separated from main text.
It's not perfect. Sometimes headings in sidebars go in wrong order and some headings in the text are not recognized, but main structure of the text is pretty good. Lots of details like tables, bold or italics text, indentation etc. is ignored. I don't need it with character statistics and getting them would require lots of work and a even deeper dive in into PDFs structure.

## Text structure
Text structure is simple. Parts of text are marked in HTML like fashion
There are four levels of headings h1-h4 marked with `<h1>`headings-tags`</h1>`
`<div>`Text is marked with div-tags`</div>` and `<sidebar>`contents of sidebars are inside sidebar-tags`</sidebar>`. A next line is added before `<sidebar>` and after headings and sidebar end tags.  
That's it

Text is put to file page by page. Main text is first and then sidebar section if there is one. There are no page endings or startings. Regular text is split in divs as pymupdf-library gives it. Extra white space is removed and words split to two lines with hyphen are combined. I cannot promise that words that naturally have hyphen are treated right. 

## Usage

PDF's are read from a folder (`--filepath`) and written to a folder (`--outpath`), both given as command line parameter. Command to run the scripts is something like
`python parse_pdf.py --filepath="collection\of\pdfs" --outpath="where\to\put\text\files"`

Script goes through all pdf files on given --filepath. Opens them one by one, parses text from them and writes text to files in --outpath folder. Filename is taken from source file by replasing .pdf or .PDF with .txt, so Ars_sourcebook.pdf becomes Ars_sourcebook.txt. If there is already a file with same name in the --output folder it is overwritten.

## book_settings in book_data.py

Datastructure book_settings in book_data.py file is used with text parsing. Official filename of sourcebook is used as key. If your files have different names the you need to edit those names in `book_settings`. `headers` contain list of header texts used in the sourcebook. Headers are in the middle top on most of the pages. `Limits.start` is the first page to read text from. It is set to drop front cover, credits and table of content. `Ignore_images` list contains large or whole page background images in the pdf. When parsing a page of a sourcebook, script collects images on the page, but images on the ignore_images list are dropped out. Remaining images are illustrations and images for sidebar texts. Actually bounding boxes for images are collected and texts inside sidebars are then texts that are inside a bounding box of an image. Rest of the values are for extracting character statistics. So for text extraction you need name of the file (key), ignore_images and headers. Optionally you can set `limits.start` to drop pages from the start and `limit.end` to drop pages of from the end. Use actual page numbers of PDF files for these values, script takes care on differences of indexing lists and page numbering. NOTE: If you want to extract all pages from files credits should ok, front cover is an image and there is no text and table of contents will look pretty ugly, but without page numbers on the text it is quite useless. References and sources at end of books come out nice.
PLEASE don't add information of sourcebooks that are not under open licence to book_settings and use only filenames of the original source.

### NOTE this is not a generic PDF reader
It is fitted to parse Ars Magica sourcebooks. It relies on commonalities among those sourcebooks. Commonalities the script relies on are:
* fonts used in headings of the books
* how fonts are used
* Sidebar texts are set on top of an image
* Usage of headers

### Known problems I will look into:
* Some main headings are missing (for example page 15 of Guardians Of The Forests)
* Sometimes text is erroneusly marked as sidebar text (for example page 15 of Guardians Of The Forests)
* Headings on two lines are not always recognized as headings
* Paragraphs split on two columns

### Known problems I'm ignoring:
* Tables
* bold text
* italics text
* indentations
* lists (bullets)
* tabulation

As far as I know these are difficult or very difficult to sort out and I don't have much use for them.
