# yt-transcript-search

A Python tool that searches through YouTube transcripts from your Chrome browsing history. Useful for finding a specific quote or phrase from a creator you've been watching without having to manually scrub through videos.

## How it works

1. Reads your exported Chrome browsing history JSON
2. Filters YouTube links down to a specific creator
3. Fetches auto-generated transcripts for each video
4. Searches through all transcripts for keywords and returns the video title and a timestamp range of the line


## Requirements

- Python 3.10+
- A Google Takeout export of your Chrome history

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Export your Chrome history via [Google Takeout](https://takeout.google.com). Make sure to select **Chrome** and download the export.

2. Create a `.env` file in the project root:

```
HISTORY_JSON_PATH=/path/to/your/Takeout/Chrome/History.json
```

3. In `make_json()`, change the author name to the YouTube creator you want to search:

```python
if youtube.author == "Creator Name Here":
```
You can change the filename of the generate JSON file by changing the `VIDEO_INFO_JSON_FILENAME` variable up top.

4. In `search()`, update the regex patterns to the words or phrases you're looking for:

```python
if re.search(r'\byourword\b', line):
```

## Usage

```bash
python main.py
```

On the first run the script will:
- Build a JSON file of the creator's videos from your history
- Fetch and save transcripts to a `transcripts/` folder (this takes a while due to rate limit throttling)
- Search through the transcripts and print any matching lines with timestamps

On subsequent runs it skips already-downloaded transcripts and goes straight to the search.

## Output

Matches print in the format:
```
video_title.txt
    123.45 - 128.60: the matching line of transcript text
```

## Notes

- Transcript fetching sleeps 60-120 seconds between requests to avoid rate limiting. For a large history this can take several hours.
- Videos that are private, deleted, or have no auto-generated captions, or otherwise return as bad requests, will be skipped and logged to `links_with_errors.txt`.
- The timestamps overlapping are a known thing, this is from the youtube_transcript_api. [See this issue for more information.](https://github.com/jdepoix/youtube-transcript-api/issues/21#issuecomment-520043638)
