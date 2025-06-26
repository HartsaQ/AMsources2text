# AMsources2text
Code to extract text with some structure from Ars Magica sourcebooks

It started as a project to get character (monsters, magi, creatures etc.) statistics from sourcebooks to be added to a compendium for [Ars Magica module for Foundry VTT](https://github.com/Xzotl42/arm5e). But parsing the PDFs was not that simple. So I dug deeper into PDFs to get more useful information about the text. At some point I realized that code could also be used to get the text with headers (titles) and contents of sidebar boxes separated from main text.
It's not perfect. Sometimes Headers in sidebars go in wrong order and some headers are not recognized, but main structure of the text is close to perfect. Lots of details like tables, bold or italics text, indentation etc. is ignored. I don't need it with character statistics and getting them would be a even deeper dive in into PDFs.

Text structure is simple. Parts of text are marked in HTML like fashion
There are four levels of headers h1-h4 marked with <h1>HTML-tags</h1>
<div>Text is marked with div-tags</div> and <sidebar>contents of sidebars are inside sedebar-tags</sidebar>
That's it
Text is put to file page by page. Main text is first and then sidebar section if there is one. There are no page endings or startings. Regular text is split in divs as pymupdf-library gives it. Extra white space is removed and words split to two lines with hyphen has been combined. I cannot promise that words that naturally have hyphen are treated right. 
