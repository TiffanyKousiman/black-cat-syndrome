# PetFinder API State-Based Data Collection Tool

A robust Python-based data collection system for gathering animal shelter data across all US states using the PetFinder API v2. This tool is designed to handle API rate limits gracefully while providing detailed progress tracking and resumption capabilities.

## Overview

This script provides a comprehensive solution for collecting animal data from the PetFinder API across all US states and Washington DC. It builds upon methodologies similar to those used in [The Pudding's "Finding Forever Homes" analysis](https://pudding.cool/2019/10/shelters), but with enhanced session management and scalability for large-scale data collection. Specifically, it collects two datasets: **adoptable cats** (as at 3 Aug 2025) & **adopted cats** since Jan 2020 collected over a week period from 4-11 Aug 2025.

### Key Features

- **State-based collection** across all US states plus Washington DC
- **Rate limit management** with automatic resumption after hitting daily API limits
- **Progress tracking** with detailed session state persistence
- **Automatic retry logic** with exponential backoff for failed requests
- **Data deduplication** and file combining functionality
- **Comprehensive logging** for monitoring collection progress
- **Special handling** for Nevada state due to PetFinder API limitations

## PetFinder API Details

### API Version and Authentication
- **API Version**: PetFinder API v2
- **Authentication**: OAuth2 client credentials flow
- **Base URL**: `https://api.petfinder.com/v2`
- **Rate Limit**: 1,000 requests per day per API key
- **Token Expiry**: Access tokens expire after 1 hour

### API Endpoints Used
- **Authentication**: `POST /oauth2/token`
- **Animal Data**: `GET /animals`

### Request Parameters
The script uses the following key parameters for animal data requests:

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `type` | Animal species | `cat`, `dog`, `rabbit`, `bird` |
| `status` | Animal availability status | `adoptable`, `adopted` |
| `location` | Geographic location | State codes (`CA`, `NY`) or ZIP codes (Nevada) |
| `limit` | Records per page (max 100) | `100` |
| `page` | Page number for pagination | `1`, `2`, `3`... |
| `sort` | Sort order | `recent`, `distance` |
| `after` | Published date filter | `2019-12-31T23:59:59+00:00` |

## Collection Methodology

### Geographic Coverage
The script collects data for all 50 US states plus Washington DC:

**Standard States**: Use two-letter state abbreviations (e.g., `CA`, `NY`, `TX`)

**Nevada Special Case**: Due to a documented PetFinder API bug, Nevada queries use specific ZIP codes instead of the state abbreviation:
```
89009, 89011, 89014, 89015, 89019, 89024, 89027, 89032, 89048, 89052, 89074, 
89101, 89103, 89104, 89107, 89113, 89117, 89118, 89119, 89120, 89121, 89122, 
89123, 89128, 89129, 89130, 89131, 89134, 89135, 89136, 89139, 89143, 89145, 
89146, 89147, 89148, 89149, 89183, 89193, 89406, 89408, 89410, 89415, 89423, 
89429, 89431, 89434, 89436, 89445, 89447, 89450, 89451, 89460, 89502, 89506, 
89511, 89512, 89523, 89701, 89704, 89703, 89702, 89706, 89801
```

### Data Collection Process

1. **Authentication**: Obtain OAuth2 access token using client credentials
2. **State Iteration**: Process each state/location sequentially
3. **Pagination Handling**: Fetch all pages of results for each location
4. **Data Flattening**: Convert nested JSON responses to flat CSV structure
5. **Progress Tracking**: Save completion status after each state
6. **Error Recovery**: Handle API failures with exponential backoff retry
7. **Rate Limit Management**: Save progress for resumption upon hitting API rate limit.

### Rate Limit Handling Strategy

The script implements several strategies to manage the 1,000 requests/day limit:

- **Request Spacing**: 2-second delays between requests
- **Progress Persistence**: Save completion status after each state
- **Resumption Capability**: Continue from last completed page when restarting
- **Partial State Tracking**: Track incomplete states with specific page numbers
- **Graceful Degradation**: Save collected data before hitting limits

## Data Structure and Features

The collected data follows a comprehensive schema based on PetFinder API v2 responses, with additional processing for analytical use.

### Core Animal Information

| Field | Description | Data Type | Example Values |
|-------|-------------|-----------|----------------|
| `id` | Unique PetFinder animal ID | integer | `12345678` |
| `org_id` | Organization/shelter ID | string | `CA123` |
| `url` | PetFinder listing URL | string | `https://www.petfinder.com/...` |
| `type` | Animal species | string | `Cat`, `Dog`, `Rabbit` |
| `species` | Specific species | string | `Dog`, `Cat` |
| `name` | Animal's given name | string | `Buddy`, `Luna` |
| `status` | Current status | string | `adoptable`, `adopted` |

### Physical Characteristics

| Field | Description | Data Type | Possible Values |
|-------|-------------|-----------|-----------------|
| `age` | Age category | string | `Baby`, `Young`, `Adult`, `Senior` |
| `gender` | Animal gender | string | `Female`, `Male`, `Unknown` |
| `size` | Size category | string | `Small`, `Medium`, `Large`, `Extra Large` |
| `coat` | Coat type/length | string | `Short`, `Medium`, `Long`, `Wire`, `Hairless`, `Curly` |

### Breed Information

| Field | Description | Data Type | Notes |
|-------|-------------|-----------|-------|
| `breeds_primary` | Primary breed | string | As reported by shelter |
| `breeds_secondary` | Secondary breed (if mixed) | string | May be null |
| `breeds_mixed` | Mixed breed indicator | boolean | `True`/`False` |
| `breeds_unknown` | Unknown breed indicator | boolean | `True`/`False` |

### Color Information

| Field | Description | Data Type | Examples |
|-------|-------------|-----------|----------|
| `colors_primary` | Primary color | string | `Black`, `Brown`, `White` |
| `colors_secondary` | Secondary color | string | May be null |
| `colors_tertiary` | Tertiary color | string | May be null |

### Medical and Behavioral Attributes

| Field | Description | Data Type | Values |
|-------|-------------|-----------|--------|
| `spayed_neutered` | Spay/neuter status | boolean | `True`/`False`/`null` |
| `house_trained` | House training status | boolean | `True`/`False`/`null` |
| `declawed` | Declawed status | boolean | `True`/`False`/`null` |
| `special_needs` | Special needs indicator | boolean | `True`/`False`/`null` |
| `shots_current` | Current vaccination status | boolean | `True`/`False`/`null` |

### Environment Compatibility

| Field | Description | Data Type | Values |
|-------|-------------|-----------|--------|
| `env_children` | Good with children | boolean | `True`/`False`/`null` |
| `env_dogs` | Good with dogs | boolean | `True`/`False`/`null` |
| `env_cats` | Good with cats | boolean | `True`/`False`/`null` |

### Contact and Location Information

| Field | Description | Data Type | Notes |
|-------|-------------|-----------|-------|
| `contact_email` | Shelter email | string | May be null |
| `contact_phone` | Shelter phone | string | May be null |
| `contact_address1` | Shelter address line 1 | string | |
| `contact_address2` | Shelter address line 2 | string | May be null |
| `contact_city` | Shelter city | string | |
| `contact_state` | Shelter state | string | |
| `contact_postcode` | Shelter ZIP code | string | |
| `contact_country` | Shelter country | string | Usually `US` |

### Media Information

| Field | Description | Data Type | Notes |
|-------|-------------|-----------|-------|
| `photo_count` | Number of photos | integer | Count of available photos |
| `photo` | Primary photo URL | string | Full-size image URL |
| `primary_photo_cropped` | Cropped photo URL | string | Cropped version URL |

### Additional Metadata

| Field | Description | Data Type | Notes |
|-------|-------------|-----------|-------|
| `tags` | Descriptive tags | string | Pipe-separated values |
| `description` | Full description | string | *Not available in v2 API* |
| `published_at` | Publish date | string | ISO datetime |
| `status_changed_at` | Status change date | string | ISO datetime |
| `distance` | Distance from query location | float | Miles |
| `stateQ` | Queried state/location | string | State code or ZIP |
| `stateQ_grouped` | Grouped state | string | Nevada ZIPs → 'NV' |
| `accessed` | Data collection timestamp | string | UTC timestamp |

### Data Quality Notes

**Missing Values**: The PetFinder API may return `null` values for many optional fields. Shelters are not required to provide complete information for all attributes.

**Inconsistent Reporting**: Since shelters self-report animal characteristics, there may be inconsistencies in breed identification, age estimation, and behavioral assessments.

**Nevada Data**: Due to the API bug requiring ZIP code queries for Nevada, the `stateQ_grouped` field maps all Nevada ZIP codes to 'NV' for consistent analysis.

**Photo Availability**: Not all animals have photos. The `photo_count` field indicates the number of available images.

## Configuration

### Environment Variables
Create a `.env` file with your PetFinder API credentials:

```bash
PETFINDER_API_KEY=your_api_key_here
PETFINDER_SECRET_KEY=your_secret_key_here
```

### Script Configuration
Edit the global configuration variables at the top of the script:

```python
ANIMAL_TYPE = 'cat'  # Options: 'cat', 'dog', 'rabbit', 'bird', etc.
PUBLISHED_AFTER_DATE = '2019-12-31T23:59:59+00:00'  # Filter by publish date
```

## Usage

### Basic Usage
```bash
python petfinder_collector.py
```

### File Organization
The script creates a hierarchical directory structure:
```
data/
├── {animal_type}/
│   └── {YYYY-MM-DD}/
│       └── {status}/
│           ├── AL_cats.csv                 # State-specific data
│           ├── CA_cats.csv
│           ├── ...
│           └── all_adopted_cats.csv        # aggregated data after deduplication
├── progress_adopted.json                   # progress tracking
└── progress_adoptable.json                 # progress tracking
```

### Progress Tracking
The script automatically tracks progress and can resume interrupted collections:
- **Completed states**: Fully processed states (skipped on restart)
- **Partial states**: States that were interrupted mid-collection
- **Failed states**: States that encountered errors

### Resumption
If the script stops due to rate limits or errors, simply restart it. The script will:
1. Load previous progress from JSON files
2. Skip already completed states
3. Resume partial states from the last processed page
4. Continue with remaining states

## Output Files

### Individual State Files
- **Format**: CSV with headers
- **Naming**: `{state}_{animal_type}s.csv`
- **Content**: All animals found for that state/location

### Combined Files
- **Format**: CSV with headers
- **Naming**: `all_{status}_{animal_type}s.csv`
- **Content**: Deduplicated data from all states
- **Features**: Nevada ZIP codes mapped to 'NV' state

### Progress Files
- **Format**: JSON
- **Naming**: `progress_{status}.json`
- **Content**: Tracking information for resumption

## Error Handling and Logging

### Logging Configuration
The script provides comprehensive logging to both file and console:
- **File**: `petfinder_collection.log`
- **Level**: INFO
- **Format**: Timestamp, level, message

### Common Error Scenarios
1. **Rate Limit Exceeded**: Script saves progress and exits gracefully
2. **Authentication Failure**: Automatic token refresh
3. **Network Timeouts**: Exponential backoff retry (3 attempts)
4. **Invalid State/Location**: Logged and skipped
5. **API Response Errors**: Logged with details

### Retry Logic
- **Initial delay**: 2 seconds between requests
- **Rate limit delay**: 10, 20, 30 seconds (progressive)
- **Error retry delay**: 5, 10 seconds
- **Maximum attempts**: 3 per request

## Troubleshooting

### Common Issues

**Authentication Errors**
```
ERROR - Missing API credentials in .env file
```
*Solution*: Verify `.env` file exists with correct variable names

**Rate Limit Reached**
```
INFO - Rate limited. Waiting 10s...
INFO - Partially completed TX - stopped at page 15
```
*Solution*: Wait until the next day and restart the script

**Network Connectivity**
```
ERROR - Request failed (attempt 3): Connection timeout
```
*Solution*: Check internet connection and restart script

### Monitoring Progress
Use the built-in status summary to check progress:
```python
client.get_status_summary(ANIMAL_TYPE, 'adopted')
```

## API Key Management

### Obtaining API Keys
1. Register at [PetFinder Developers](https://www.petfinder.com/developers/)
2. Create a new application
3. Note your API Key and Secret

### Security Best Practices
- Store credentials in `.env` file (never commit to version control)
- Use different API keys for different projects
- Monitor API usage through PetFinder developer dashboard
- Rotate keys periodically


For questions about the underlying data structure or methodology comparisons with The Pudding's work, refer to their [original documentation](https://pudding.cool/2019/10/shelters) and [data repository](https://github.com/the-pudding/data/tree/master/dog-shelters).
