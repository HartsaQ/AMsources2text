import click
import pymupdf
import glob
import os

from book_data import book_settings

def clean_block(block: str):
    one_line = " ".join([line.strip() for line in block.split('\n')])
    cleaned_line = one_line.replace('- ', '')
    return cleaned_line.strip()


# Marks text inside images as sidebar text
# returns list of lists ["block text", block number, text_type, outline_type, page_number]
# where text_type is 0 for normal text and 1 for sidebar text
# outline_type is reserved for headings
def separate_page(page, ignore_images):
    page_contents = []
    images = page.get_images(full=True)
    sidebar_images = [page.get_image_rects(img[0])[0] for img in images if img[0] not in ignore_images]
    # (x0, y0, x1, y1, "lines in the block", block_no, block_type)
    # no images, no sidebar texts
    if len(sidebar_images) == 0:
        page_contents = [[clean_block(block[4]), block[5], 0, 0, page.number] for block in page.get_text("blocks") if block[6] == 0]
        return page_contents
    else:
        page_blocks = [block for block in page.get_text("blocks") if block[6] == 0]
        for block_index, block in enumerate(page_blocks):
            text_block = True
            # Is text inside an image? Is it a sidebar text?
            for sidebar_image in sidebar_images:
                if (sidebar_image[0] <= block[0] <= sidebar_image[2] and
                        sidebar_image[0] <= block[2] <= sidebar_image[2] and
                        sidebar_image[1] <= block[1] <= sidebar_image[3] and
                        sidebar_image[1] <= block[3] <= sidebar_image[3]
                ):
                    text_block = False
                    page_contents.append([clean_block(block[4]), block[5], 1, 0, page.number])
                    break
            if text_block:
                page_contents.append([clean_block(block[4]), block[5], 0, 0, page.number])
        return page_contents

def drop_headers_and_page_numbers(blocks, headers):
    results_list = []
    # There are no headers on pages starting a new Chapter
    # Helps at least to get "The Rhine Tribunal" heading to page 4
    chapter_page = any([block[0].strip().startswith('Chapter') for block in blocks])
    for block in blocks:
        if not chapter_page and block[0] in headers:
            continue
        elif block[0].isnumeric():
            continue
        else:
            results_list.append(block)
    return results_list

def get_text_from_block(block):
    text = ""
    for line in block['lines']:
        text += " " + "".join([span['text'] for span in line['spans']])

    cleaned_line = text.replace('-\n', '').replace('\n', ' ')
    return cleaned_line

def find_headings(page):
    page_dict = page.get_text("dict")
    types = []
    # 1 Chapter heading
    # 2 main heading
    # 3 medium heading
    # 4 minor heading
    for bindex, block in enumerate(page_dict['blocks']):
        if block['type'] == 0:
            #try:
                line = block['lines'][0]
                span = line['spans'][0]
                text = get_text_from_block(block)
                if span['size'] > 30:
                    types.append((text, 1))
                # drop chapter headings
                elif span['font'] in ['GoudyTextMT-LombardicCap'] and "Chapter" in span['text']:
                    types.append((text, 2))
                elif span['font'] in ['GoudyTextMT-LombardicCap']:
                    types.append((text, 3))
                elif all([span['font'] == "Weiss-Bold" for line in block['lines'] for span in line['spans']]):
                    types.append((text, 4))
                else:
                    continue
            #except:
            #    print(f"A failure at page {page.number}")
        else:
            continue
    return types

@click.group()
def text():
    pass

def get_blocks_for_character_extraction(data):
    sidebar_blocks = []
    main_blocks = []
    for page_data in data:
        for block in page_data['blocks']:
            # ignore Chapter and main headings
            if block[3] in [1, 2]:
                main_blocks.append(block)
            else:
                if block[2] == 0:
                    main_blocks.append(block)
                elif block[2] == 1:
                    sidebar_blocks.append(block)
                else:
                    print("Something went wrong in block separation")

    return main_blocks, sidebar_blocks

@text.command()
@click.option('--filepath', type=click.Path(exists=True, file_okay=False))
@click.option('--outpath', type=click.Path(exists=True, file_okay=False))
def to_text(filepath, outpath):
    files = glob.glob(os.path.join(filepath, "AG*"))
    for filename in files:
        file_data = []
        source_name = os.path.basename(filename)
        print(source_name)
        with pymupdf.open(filename) as doc:
            headers = book_settings[source_name]['headers']
            ignore_images = book_settings[source_name]['ignore_images']
            # use actual page numbers for start and end values
            # or -1 to set no limits
            start = book_settings[source_name]['limits']['start']
            end = book_settings[source_name]['limits']['end']
            start = start-1 if start > 0 else 0
            end = end if end > 0 else len(doc)
            for page in doc[start:end]:
                page_structure = {"page": page.number+1,
                                  "file": source_name}
                # Separate sidebar and normal text
                # ["block text", block number, text_type, heading_type]
                #  where text_type is 0 for normal text and 1 for sidebar text
                separated_page = separate_page(page, ignore_images)
                cleaned_page = drop_headers_and_page_numbers(separated_page, headers)
                # ("text", type)
                headings = find_headings(page)
                for block in cleaned_page:
                    if block[0].strip() == "":
                        continue
                    if block[0].startswith("Chapter"):
                        page_structure['chapter'] = block[0]
                        block[3] = 1
                        continue
                    for heading_text, heading_level in headings:
                        heading_length = len(heading_text)
                        block_len = len(block[0])
                        check_length = min(heading_length, 20, block_len)
                        # Note next chapter can start with same text as it's heading
                        if abs(heading_length-block_len) <2 and block[0][:check_length] == heading_text[:check_length]:
                            block[3] = heading_level
                            if heading_level == 2:
                                page_structure['main_heading'] = block[0]
                        else:
                            # Heading texts can have odd amount of space bars
                            # And capitals in odd places
                            # Note a paragraph can start with same text as it's heading
                            temp_heading = heading_text.replace(" ", "").lower()
                            temp_block = block[0].replace(" ", "").lower()
                            heading_length = len(temp_heading)
                            block_len = len(block[0])
                            check_length = min(heading_length, 20, block_len)
                            if abs(heading_length-block_len) <5 and temp_block[:check_length] == temp_heading[:check_length]:
                                block[3] = heading_level
                                if heading_level == 2:
                                    page_structure['main_heading'] = block[0]

                page_structure['blocks'] = cleaned_page
                file_data.append(page_structure)


            new_name = source_name.removesuffix(".pdf").removesuffix(".PDF")+".txt"
            write_file(file_data, new_name, outpath)



def write_file(file_data, new_name, outpath):
    with open(os.path.join(outpath, new_name), "w", encoding="utf-8") as f:
        for page_structure in file_data:
            sidebar_texts = ""
            if page_structure.get('chapter'):
                f.writelines(f"\n<h1>{page_structure['chapter']}</h1>\n\n")
            if page_structure.get('main_heading'):
                f.writelines(f"\n<h2>{page_structure['main_heading']}</h2>\n\n")
            for block in page_structure['blocks']:
                if block[3] in [1,2]:
                    continue
                elif block[3] == 3:
                    if block[2] == 0:
                        f.writelines(f"\n<h3>{block[0]}</h3>\n\n")
                    else:
                        sidebar_texts += f"\n<h3>{block[0]}</h3>\n\n"
                elif block[3] == 4:
                    if block[2] == 0:
                        f.writelines(f"\n<h4>{block[0]}</h4>\n\n")
                    else:
                        sidebar_texts += f"\n<h4>{block[0]}</h4>\n\n"
                else:
                    if block[2] == 0:
                        f.writelines(f"<div>{block[0]}</div>\n")
                    else:
                        sidebar_texts += f"<div>{block[0]}</div>\n"
            else:
                if sidebar_texts:
                    f.writelines(f"\n<div sidebars>\n")
                    f.writelines(sidebar_texts)
                    f.writelines(f"</div sidebars>\n\n")


if __name__ == '__main__':
    to_text()