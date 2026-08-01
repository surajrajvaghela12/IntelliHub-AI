from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
import pandas as pd
import json

from apps.datasets.models import Dataset, DatasetVersion
from apps.datasets.utils import analyze_dataset_metadata
from .services import scrape_web_link

@login_required
def scraper_home_view(request):
    url_input = request.POST.get('url', '')
    tables = []

    if request.method == 'POST' and 'scrape_now' in request.POST and url_input:
        try:
            extracted_tables = scrape_web_link(url_input)
            if not extracted_tables:
                messages.warning(request, "Could not extract structured data from the URL. Please verify the URL and try again.")
            else:
                messages.success(request, f"Successfully extracted {len(extracted_tables)} dataset table(s) from the web link!")
                
                # Cache scraped dataframes as JSON dicts in session for ingestion
                session_tables = {}
                for tbl in extracted_tables:
                    # Convert dataframe to json dict
                    session_tables[str(tbl['index'])] = {
                        'title': tbl['title'],
                        'json_data': tbl['df'].to_json(orient='records')
                    }
                    # Attach hidden json string for template form rendering
                    tbl['json_data'] = tbl['df'].to_json(orient='records')
                    tables.append(tbl)
                
                request.session['scraped_tables'] = session_tables
                request.session['scraped_url'] = url_input
        except Exception as e:
            messages.error(request, f"Web Scraping error: {str(e)}")

    elif request.method == 'POST' and 'ingest_table' in request.POST:
        if not request.user.can_upload_dataset:
            messages.error(request, "Upload quota reached for Student role.")
            return redirect('datasets:list')
            
        dataset_name = request.POST.get('dataset_name', 'Scraped Web Dataset').strip()
        table_index = request.POST.get('table_index', '1')
        table_json_input = request.POST.get('table_json', '')
        
        df_scraped = None
        
        # 1. Try restoring from hidden form data
        if table_json_input:
            try:
                df_scraped = pd.read_json(table_json_input, orient='records')
            except Exception:
                pass

        # 2. Try restoring from session cache
        if df_scraped is None or df_scraped.empty:
            session_tables = request.session.get('scraped_tables', {})
            tbl_info = session_tables.get(str(table_index))
            if tbl_info and 'json_data' in tbl_info:
                try:
                    df_scraped = pd.read_json(tbl_info['json_data'], orient='records')
                except Exception:
                    pass

        if df_scraped is None or df_scraped.empty:
            messages.error(request, "Failed to retrieve scraped table data for ingestion. Please scrape the link again.")
            return redirect('scraper:home')

        target_url = request.session.get('scraped_url', url_input or 'Web Link')
        dataset = Dataset.objects.create(
            user=request.user,
            name=dataset_name or f"Scraped Web Dataset #{table_index}",
            description=f"Ingested from web scraping target: {target_url}",
            file_format='CSV'
        )
        
        csv_bytes = df_scraped.to_csv(index=False).encode('utf-8')
        version = DatasetVersion.objects.create(dataset=dataset, version_number=1)
        version.file.save(f"scraped_{dataset.id}.csv", ContentFile(csv_bytes))
        
        meta = analyze_dataset_metadata(version.file.path)
        version.row_count = meta['row_count']
        version.column_count = meta['column_count']
        version.memory_usage_bytes = meta['memory_usage_bytes']
        version.memory_usage_str = meta['memory_usage_str']
        version.duplicate_rows = meta['duplicate_rows']
        version.missing_values = meta['missing_values']
        version.numerical_cols = meta['numerical_cols']
        version.categorical_cols = meta['categorical_cols']
        version.save()
        
        messages.success(request, f"Scraped data imported into Dataset Manager as '{dataset.name}' ({version.row_count} rows, {version.column_count} columns)!")
        return redirect('datasets:detail', dataset_id=dataset.id)

    context = {
        'url_input': url_input,
        'tables': tables,
    }
    return render(request, 'scraper/scraper.html', context)
