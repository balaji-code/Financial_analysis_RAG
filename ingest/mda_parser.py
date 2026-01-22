def extract_mda_pages(pages, start_page: int, end_page: int):
    """
    pages: list of (page_no, text)
    returns list of (page_no, text) for MD&A only
    """
    mda_pages = []

    for page_no, text in pages:
        if start_page <= page_no <= end_page:
            mda_pages.append((page_no, text))

    return mda_pages