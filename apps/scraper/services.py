import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import json
from urllib.parse import urlparse, urljoin

def scrape_web_link(url, user_agent=None):
    """
    Universal web scraper that extracts structured data from ANY web link.
    Supports:
    1. Direct CSV / TSV file URLs
    2. Direct JSON endpoints / files
    3. Web page HTML <table> elements
    4. Web page repeating cards / list elements
    5. Fallback general web content (headings, text snippets, and URLs)
    """
    url = url.strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    headers = {
        'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,text/csv;q=0.8,*/*;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        res = requests.get(url, headers=headers, timeout=12, verify=False)
        res.raise_for_status()
    except Exception as err:
        # Retry with simpler headers if error occurs
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=12)
        res.raise_for_status()

    content_type = res.headers.get('Content-Type', '').lower()
    text = res.text
    extracted_dfs = []

    # 1. Direct CSV/TSV handling
    if 'csv' in content_type or 'tsv' in content_type or url.lower().endswith('.csv') or url.lower().endswith('.tsv'):
        try:
            sep = '\t' if ('tsv' in content_type or url.lower().endswith('.tsv')) else ','
            df = pd.read_csv(io.StringIO(text), sep=sep)
            if not df.empty and len(df.columns) >= 1:
                extracted_dfs.append(_format_extracted_df(df, "Direct CSV Dataset", 1))
                return extracted_dfs
        except Exception:
            pass

    # 2. Direct JSON handling
    if 'json' in content_type or url.lower().endswith('.json') or text.strip().startswith('[') or text.strip().startswith('{'):
        try:
            data = res.json()
            df = _json_to_dataframe(data)
            if not df.empty and len(df.columns) >= 1:
                extracted_dfs.append(_format_extracted_df(df, "JSON Data Feed", 1))
                return extracted_dfs
        except Exception:
            pass

    # 3. HTML Page Parsing
    soup = BeautifulSoup(text, 'html.parser')

    # Remove script, style, and iframe tags
    for tag in soup(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()

    # Strategy A: HTML <table> tags
    tables = soup.find_all('table')
    for table in tables:
        try:
            df_list = pd.read_html(io.StringIO(str(table)))
            if df_list:
                df = df_list[0]
                # Flatten multi-level columns if any
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(map(str, col)).strip() for col in df.columns]
                
                # Drop all-NA columns and rows
                df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
                
                if len(df) >= 1 and len(df.columns) >= 1:
                    index_num = len(extracted_dfs) + 1
                    extracted_dfs.append(_format_extracted_df(df, f"HTML Table #{index_num}", index_num))
        except Exception:
            pass

    if extracted_dfs:
        return extracted_dfs

    # Strategy B: Card/List item extraction
    repeating_items = []
    # Search for cards, list items, or repeating containers
    card_elements = soup.find_all(['div', 'li', 'article'], class_=lambda c: c and any(kw in str(c).lower() for kw in ['card', 'item', 'row', 'product', 'post', 'entry', 'result', 'list-group-item']))
    
    if len(card_elements) >= 3:
        for idx, el in enumerate(card_elements[:50]): # limit to 50 items
            title_el = el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'a'])
            title_text = title_el.get_text(strip=True) if title_el else f"Item #{idx+1}"
            
            link_el = el.find('a', href=True)
            link_href = urljoin(url, link_el['href']) if link_el else ""
            
            body_text = el.get_text(separator=" ", strip=True)
            # Remove title_text from body_text if redundant
            if title_text and title_text in body_text:
                body_text = body_text.replace(title_text, "", 1).strip()
            
            repeating_items.append({
                'Index': idx + 1,
                'Title / Header': title_text[:120],
                'Description / Content': body_text[:250],
                'Link URL': link_href
            })

    if len(repeating_items) >= 2:
        df = pd.DataFrame(repeating_items)
        extracted_dfs.append(_format_extracted_df(df, "Extracted Web Card List", 1))
        return extracted_dfs

    # Strategy C: Universal Web Content & Hyperlink Extractor (Guaranteed Fallback)
    page_records = []
    
    # Extract Headings and Paragraphs
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'a'])
    for idx, el in enumerate(elements[:100]):
        el_type = el.name.upper()
        el_text = el.get_text(strip=True)
        if not el_text or len(el_text) < 3:
            continue
        
        el_link = ""
        if el.name == 'a' and el.has_attr('href'):
            el_link = urljoin(url, el['href'])

        page_records.append({
            'Item ID': len(page_records) + 1,
            'Element Type': el_type,
            'Content Text': el_text[:300],
            'Associated Link': el_link
        })

    if page_records:
        df = pd.DataFrame(page_records)
        extracted_dfs.append(_format_extracted_df(df, "Structured Web Page Content", 1))
        return extracted_dfs

    # Last resort fallback if page has minimal HTML content
    df_fallback = pd.DataFrame([{
        'URL': url,
        'Page Title': soup.title.string.strip() if soup.title else "Web Page",
        'Scraped Content': soup.get_text(separator=" ", strip=True)[:500] or "No text content found"
    }])
    extracted_dfs.append(_format_extracted_df(df_fallback, "Web Page Metadata", 1))
    return extracted_dfs


def _json_to_dataframe(data):
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                return pd.DataFrame(val)
        return pd.DataFrame([data])
    return pd.DataFrame()


def _format_extracted_df(df, title, index):
    df = df.copy()
    # Clean column names
    df.columns = [str(col).strip() if str(col).strip() else f"Col_{i+1}" for i, col in enumerate(df.columns)]
    
    # Clean data values for JSON/HTML rendering
    df_clean = df.fillna("N/A").astype(str)
    
    records = df_clean.head(25).to_dict(orient='records')
    
    return {
        'index': index,
        'title': title,
        'rows': len(df),
        'cols': len(df.columns),
        'headers': list(df.columns),
        'preview': records,
        'df': df
    }
