"""
PetFinder API State-Based Data Collection Script

This script provides a comprehensive solution for collecting animal data from the PetFinder API 
across all US states and Washington DC. It is designed to handle the API's daily rate limit of 
1000 requests by implementing robust session management and progress tracking capabilities.

Key Features:
- Collects data for any animal type (cats, dogs, rabbits, etc.) and status (adoptable, adopted)
- State-based collection across all US states plus Washington DC
- Progress tracking and resumption capability to handle API rate limits
- Automatic retry logic with exponential backoff for failed requests
- Data deduplication and file combining functionality
- Comprehensive logging for monitoring collection progress

The script handles Nevada state specially due to a PetFinder API bug, using ZIP codes instead 
of state abbreviation. All collected data includes timestamps and state identifiers for 
tracking purposes.

Usage:
1. Configure ANIMAL_TYPE (e.g., 'cat', 'dog') and ANIMAL_STATUS parameters ('adopted', 'adoptable')
2. Set API credentials in .env file
3. Run script - it will automatically resume from where it left off if interrupted
4. Combined data files are saved with deduplication applied

Rate Limit Management:
- Implements 2-second delays between requests
- Tracks partial completion when hitting daily limits
- Saves progress after each state to enable resumption
- Provides detailed status summaries for monitoring progress

Petfinder API Documentation:
    - https://www.petfinder.com/developers/v2/docs/#get-animals
"""

import requests
import pandas as pd
import numpy as np
import json
from datetime import date, datetime
import time
import logging
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('petfinder_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global configurations
ANIMAL_TYPE: str = 'cat'  # Change this to 'dog', 'rabbit', etc.
ADOPTION_STATUS: str = 'adopted' # Change this to 'adoptable' to collect currently available pets for adoption
PUBLISHED_AFTER_DATE: str = '2019-12-31T23:59:59+00:00'  # published date cut off for adopted set - after 2019

# Due to a bug in the PetFinder API, I was encouraged to use zipcodes for the state of Nevada
# All other states and DC simply used their state abbreviation
NV_POSTCODES: List[str] = ["89009", "89011", "89014", '89015', '89019', '89024', '89027','89032', '89048', '89052', '89074', '89101','89103', '89104','89107','89113','89117','89118','89119','89120','89121','89122','89123','89128','89129','89130','89131','89134','89135','89136','89139','89143','89145','89146','89147','89148','89149','89183','89193','89406','89408','89410','89415','89423','89429','89431','89434','89436','89445','89447','89450','89451','89460','89502','89506','89511','89512','89523','89701', '89704','89703','89702','89706','89801']
DEFAULT_US_STATES: List[str] = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'LA', 'ME', 'MD', 'KY', 
    'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'MA', 'RI',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'SC', 'NJ',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 
    'DC'
]
US_STATES: List[str] = NV_POSTCODES + DEFAULT_US_STATES


class StateBasedPetfinderClient:
    """
    A client for collecting PetFinder API data across US states with session management.
    
    This class provides functionality to authenticate with the PetFinder API, collect animal
    data across all US states, handle API rate limits through progress tracking, and manage
    data persistence with resumption capabilities.
    
    Attributes:
        api_key (str): PetFinder API key for authentication
        secret (str): PetFinder API secret for authentication
        base_url (str): Base URL for PetFinder API v2
        access_token (Optional[str]): Current OAuth2 access token
        token_expires_at (Optional[float]): Unix timestamp when token expires
        session (requests.Session): HTTP session for connection pooling
    """
    
    def __init__(self, api_key: str, secret: str) -> None:
        """
        Initialize the PetFinder API client with credentials.
        
        Args:
            api_key (str): PetFinder API key
            secret (str): PetFinder API secret key
            
        Raises:
            requests.exceptions.RequestException: If initial authentication fails
        """
        self.api_key = api_key
        self.secret = secret
        self.base_url = "https://api.petfinder.com/v2"
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        self.session = requests.Session()
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with PetFinder API using OAuth2 client credentials flow.
        
        Updates the instance's access_token and token_expires_at attributes.
        
        Raises:
            requests.exceptions.RequestException: If authentication request fails
            KeyError: If response doesn't contain expected token data
        """
        auth_url = f"{self.base_url}/oauth2/token"
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret
        }
        
        response = requests.post(auth_url, data=auth_data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expires_at = time.time() + token_data.get('expires_in', 3600)
        logger.info("Successfully authenticated with Petfinder API")
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make authenticated HTTP request with automatic retry and token refresh.
        
        Implements exponential backoff for rate limiting and automatic token refresh
        when tokens are near expiration.
        
        Args:
            url (str): Full URL to make request to
            params (Optional[Dict[str, Any]]): Query parameters for the request
            
        Returns:
            requests.Response: Successful HTTP response object
            
        Raises:
            Exception: If all retry attempts fail
            requests.exceptions.RequestException: For various HTTP errors
        """
        # Check token expiry
        if time.time() > (self.token_expires_at - 300):
            logger.info("Refreshing token...")
            self._authenticate()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        for attempt in range(3):
            try:
                time.sleep(2)  # Simple rate limiting
                
                response = self.session.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    wait_time = 10 * (attempt + 1)
                    logger.warning(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 401:
                    logger.warning("Auth failed, refreshing token...")
                    self._authenticate()
                    continue
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    if attempt < 2:
                        time.sleep(5 * (attempt + 1))
                        continue
                    response.raise_for_status()
                    
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise
        
        raise Exception("All retry attempts failed")
    
    def _flatten_animal_data(self, animal_data: Dict[str, Any], location: str) -> Dict[str, Any]:
        """
        Flatten nested animal data structure from PetFinder API into a flat dictionary.
        
        Extracts and flattens all relevant animal information including breeds, colors,
        attributes, environment preferences, contact information, and photos into a
        single-level dictionary suitable for DataFrame creation.
        
        Args:
            animal_data (Dict[str, Any]): Raw animal data from PetFinder API
            location (str): State or ZIP code where animal was queried
            
        Returns:
            Dict[str, Any]: Flattened animal data with all nested fields extracted
        """
        
        # Pre-fetch nested objects once to avoid repeated lookups
        breeds = animal_data.get('breeds', {})
        colors = animal_data.get('colors', {})
        attributes = animal_data.get('attributes', {})
        environment = animal_data.get('environment', {})
        contact = animal_data.get('contact', {})
        address = contact.get('address', {})
        photos = animal_data.get('photos', [])
        tags = animal_data.get('tags', [])
        primary_photo = animal_data.get('primary_photo_cropped', {})
        
        # Build flattened dict in one operation
        flattened = {
            # Basic info
            'id': animal_data.get('id', None),
            'org_id': animal_data.get('organization_id', None),
            'url': animal_data.get('url', None),
            'type': animal_data.get('type', None),
            'species': animal_data.get('species', None),
            'age': animal_data.get('age', None),
            'gender': animal_data.get('gender', None),
            'size': animal_data.get('size', None),
            'coat': animal_data.get('coat', None),
            'name': animal_data.get('name', None),
            'description': animal_data.get('description', None),
            'status': animal_data.get('status', None),
            'status_changed_at': animal_data.get('status_changed_at', None),
            'published_at': animal_data.get('published_at', None),
            'distance': animal_data.get('distance', None),
            
            # Breeds
            'breeds_primary': breeds.get('primary', None),
            'breeds_secondary': breeds.get('secondary', None),
            'breeds_mixed': breeds.get('mixed', None),
            'breeds_unknown': breeds.get('unknown', None),
            
            # Colors
            'colors_primary': colors.get('primary', None),
            'colors_secondary': colors.get('secondary', None),
            'colors_tertiary': colors.get('tertiary', None),
            
            # Attributes
            'spayed_neutered': attributes.get('spayed_neutered', None),
            'house_trained': attributes.get('house_trained', None),
            'declawed': attributes.get('declawed', None),
            'special_needs': attributes.get('special_needs', None),
            'shots_current': attributes.get('shots_current', None),
            
            # Environment
            'env_children': environment.get('children', None),
            'env_dogs': environment.get('dogs', None),
            'env_cats': environment.get('cats', None),
            
            # Contact
            'contact_email': contact.get('email', None),
            'contact_phone': contact.get('phone', None),
            'contact_address1': address.get('address1', None),
            'contact_address2': address.get('address2', None),
            'contact_city': address.get('city', None),
            'contact_state': address.get('state', None),
            'contact_postcode': address.get('postcode', None),
            'contact_country': address.get('country', None),
            
            # Photos
            'photo_count': len(photos),
            'photo': photos[0].get('full') if photos else None,
            'primary_photo_cropped': primary_photo.get('full') if primary_photo else None,
            
            # Tags
            'tags': '|'.join(tags) if tags else '',
            
            # Metadata
            'stateQ': location,
            'accessed': pd.Timestamp.now('UTC')  # UTC time
        }
        
        return flattened
    
    def create_directory_structure(self, animal_type: str, status: str) -> str:
        """
        Create hierarchical directory structure for organizing data files.
        
        Creates directory structure in format: animal_type/YYYY-MM-DD/status/
        If directories already exist, no error is raised.
        
        Args:
            animal_type (str): Type of animal (e.g., 'cat', 'dog')
            status (str): Animal status (e.g., 'adoptable', 'adopted')
            
        Returns:
            str: Path to created directory
        """
        date_str = date.today().isoformat()
        directory = os.path.join(animal_type, date_str, status)
        os.makedirs(directory, exist_ok=True)
        return directory
    
    def get_progress_file(self, animal_type: str, status: str) -> str:
        """
        Get file path for progress tracking JSON file.
        
        Args:
            animal_type (str): Type of animal being collected
            status (str): Status of animals being collected
            
        Returns:
            str: Full path to progress tracking file
        """
        date_str = date.today().isoformat()
        return os.path.join(animal_type, date_str, f"progress_{status}.json")
    
    def load_progress(self, animal_type: str, status: str) -> Dict[str, Any]:
        """
        Load collection progress from previous session.
        
        Reads progress tracking file to determine which states have been completed,
        which failed, and which were partially completed.
        
        Args:
            animal_type (str): Type of animal being collected
            status (str): Status of animals being collected
            
        Returns:
            Dict[str, Any]: Progress information containing:
                - completed_states: List of fully completed states
                - failed_states: List of states that failed collection
                - partial_states: Dict of partially completed states with page info
                - session_start_time: ISO timestamp of session start
        """
        progress_file = self.get_progress_file(animal_type, status)
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
        return {
            'completed_states': [], 
            'failed_states': [],
            'partial_states': {},
            'session_start_time': datetime.now().isoformat()
        }
    
    def save_progress(self, animal_type: str, status: str, progress: Dict[str, Any]) -> None:
        """
        Save collection progress for resuming later.
        
        Persists current progress state to JSON file for resumption capability
        when hitting API rate limits or encountering errors.
        
        Args:
            animal_type (str): Type of animal being collected
            status (str): Status of animals being collected  
            progress (Dict[str, Any]): Progress data to save
        """
        progress_file = self.get_progress_file(animal_type, status)
        with open(progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def collect_state_data(self, animal_type: str, status: str, location: str, 
                          after_date: Optional[str] = None, start_page: int = 1) -> Dict[str, Any]:
        """
        Collect animal data for a single state with resumption capability.
        
        Fetches all animals of specified type and status from a given location,
        handling pagination and saving data incrementally. Supports resumption
        from a specific page if collection was previously interrupted.
        
        Args:
            animal_type (str): Type of animal to collect (e.g., 'cat', 'dog')
            status (str): Status of animals (e.g., 'adoptable', 'adopted')
            location (str): State abbreviation or ZIP code for Nevada
            after_date (Optional[str]): ISO datetime string for filtering by publish date
            start_page (int): Page number to start collection from (for resumption)
            
        Returns:
            Dict[str, Any]: Collection results containing:
                - completed: Boolean indicating if collection finished
                - last_page: Last page number processed
                - animals_collected_this_session: Count of animals collected this session
                - total_animals: Total count including existing animals
                - error: Error message if collection failed (optional)
                
        Raises:
            Exception: For API request failures after all retries exhausted
        """
        logger.info(f"Collecting {status} {animal_type}s from {location} (published after {after_date or 'all time'}) starting from page {start_page}")
        
        directory = self.create_directory_structure(animal_type, status)
        filename = os.path.join(directory, f"{location}_{animal_type}s.csv")
        
        params = {
            'type': animal_type,
            'status': status,
            'location': location,
            'limit': 100,
            'page': start_page,
            'sort': 'recent'
        }
        
        # Add the after parameter if specified
        if after_date:
            params['after'] = after_date
        
        all_animals = []
        total_existing_animals = 0
        
        # Count existing animals if resuming
        if start_page > 1 and os.path.exists(filename):
            try:
                existing_df = pd.read_csv(filename)
                total_existing_animals = len(existing_df)
                logger.info(f"Resuming: {total_existing_animals} existing animals in {filename}")
            except Exception as e:
                logger.warning(f"Could not read existing data: {e}")
        
        page = start_page
        animals_collected_this_session = 0
        
        while True:
            params['page'] = page
            
            try:
                response = self._make_request(f"{self.base_url}/animals", params)
                data = response.json()
                animals = data.get('animals', [])
                
                if not animals:
                    logger.info(f"No more animals found for {location} on page {page}")
                    break
                
                # Process and flatten animals
                page_animals = []
                for animal in animals:
                    flattened = self._flatten_animal_data(animal, location)
                    page_animals.append(flattened)
                
                all_animals.extend(page_animals)
                animals_collected_this_session += len(page_animals)
                
                pagination = data.get('pagination', {})
                total_pages = pagination.get('total_pages', 1)
                
                logger.info(f"{location} - Page {page}/{total_pages} - "
                        f"Collected {len(page_animals)} animals this page, "
                        f"{total_existing_animals + len(all_animals)} total")
                
                if page >= total_pages:
                    break
                    
                page += 1
                
            except Exception as e:
                # Save whatever data we have collected so far before failing
                logger.warning(f"Request failed on page {page}: {e}")
                logger.info(f"Saving {len(all_animals)} animals collected before failure")
                
                if all_animals:
                    df = pd.DataFrame(all_animals)
                    
                    # Determine write mode
                    if start_page == 1 or not os.path.exists(filename):
                        # New file - write with header
                        df.to_csv(filename, index=False)
                        logger.info(f"Saved {len(df)} animals to new file {filename}")
                    else:
                        # Append to existing file - no header
                        df.to_csv(filename, mode='a', header=False, index=False)
                        logger.info(f"Appended {len(df)} animals to {filename}")
                
                # Return partial completion status
                return {
                    'completed': False,
                    'last_page': page,
                    'animals_collected_this_session': animals_collected_this_session,
                    'total_animals': total_existing_animals + len(all_animals),
                    'error': str(e)
                }
        
        # Save data using append mode
        if all_animals:
            df = pd.DataFrame(all_animals)
            
            # Determine write mode
            if start_page == 1 or not os.path.exists(filename):
                # New file - write with header
                df.to_csv(filename, index=False)
                logger.info(f"Saved {len(df)} animals to new file {filename}")
            else:
                # Append to existing file - no header
                df.to_csv(filename, mode='a', header=False, index=False)
                logger.info(f"Appended {len(df)} animals to {filename}")
        else:
            logger.info(f"No animals collected for {location}")
        
        return {
            'completed': True,
            'last_page': page,
            'animals_collected_this_session': animals_collected_this_session,
            'total_animals': total_existing_animals + len(all_animals)
        }
    
    def collect_all_states(self, animal_type: str, status: str, resume: bool = True, 
                          after_date: Optional[str] = None) -> None:
        """
        Collect animal data across all US states with resume capability.
        
        Orchestrates data collection across all US states and DC, managing progress
        tracking and resumption when hitting API rate limits. Automatically skips
        completed states and resumes partial collections.
        
        Args:
            animal_type (str): Type of animal to collect
            status (str): Status of animals to collect
            resume (bool): Whether to resume from previous progress
            after_date (Optional[str]): Filter animals published after this date
            
        Side Effects:
            - Creates CSV files for each state's data
            - Updates progress tracking files
            - Logs collection progress and status
        """
        logger.info(f"Starting collection: {status} {animal_type}s across all US states (published after {after_date or 'all time'})")
        
        # Load progress
        progress = self.load_progress(animal_type, status) if resume else {
            'completed_states': [], 
            'failed_states': [],
            'partial_states': {},
            'session_start_time': datetime.now().isoformat()
        }
        
        states_to_process = [state for state in US_STATES if state not in progress['completed_states']]
        
        if not states_to_process:
            logger.info("All states already completed!")
            return
        
        logger.info(f"Processing {len(states_to_process)} states (skipping {len(progress['completed_states'])} already completed)")
        if progress['partial_states']:
            logger.info(f"Will resume {len(progress['partial_states'])} partially completed states")
        
        for state in states_to_process:
            try:
                # Check if this state was partially completed
                start_page = 1
                if state in progress['partial_states']:
                    start_page = progress['partial_states'][state]['last_page']
                    logger.info(f"Resuming {state} from page {start_page}")
                
                result = self.collect_state_data(animal_type, status, state, after_date, start_page)
                
                if result['completed']:
                    # State fully completed
                    progress['completed_states'].append(state)
                    
                    # Remove from failed/partial if it was there
                    if state in progress['failed_states']:
                        progress['failed_states'].remove(state)
                    if state in progress['partial_states']:
                        del progress['partial_states'][state]
                    
                    logger.info(f"✓ Completed {state} ({len(progress['completed_states'])}/{len(US_STATES)}) - "
                              f"Collected {result['animals_collected_this_session']} animals this session")
                else:
                    # State partially completed due to API limit
                    progress['partial_states'][state] = {
                        'last_page': result['last_page'],
                        'animals_collected': result['total_animals']
                    }
                    logger.info(f"⏸ Partially completed {state} - stopped at page {result['last_page']} "
                              f"with {result['total_animals']} animals due to API limit")
                    
                    self.save_progress(animal_type, status, progress)
                    logger.info(f"Resume later to continue from where you left off.")
                    return
                
                self.save_progress(animal_type, status, progress)
                
            except Exception as e:
                logger.error(f"✗ Failed to collect {state}: {e}")
                if state not in progress['failed_states']:
                    progress['failed_states'].append(state)
                self.save_progress(animal_type, status, progress)
                continue
        
        logger.info(f"Collection complete! Completed: {len(progress['completed_states'])}, "
                   f"Partial: {len(progress['partial_states'])}, "
                   f"Failed: {len(progress['failed_states'])}")
    
    def get_status_summary(self, animal_type: str, status: str) -> None:
        """
        Display a comprehensive summary of collection status.
        
        Logs detailed information about collection progress including completed,
        partial, failed, and remaining states. Shows specific details for partial
        collections including last page processed and animal counts.
        
        Args:
            animal_type (str): Type of animal being collected
            status (str): Status of animals being collected
            
        Side Effects:
            Logs formatted status information to stdout
        """
        progress = self.load_progress(animal_type, status)
        
        completed = len(progress['completed_states'])
        partial = len(progress['partial_states'])
        failed = len(progress['failed_states'])
        remaining = len(US_STATES) - completed - partial - failed
        
        logger.info(f"\n=== Collection Status for {status} {animal_type}s ===")
        logger.info(f"Completed states: {completed}/{len(US_STATES)}")
        logger.info(f"Partially completed: {partial}")
        logger.info(f"Failed states: {failed}")
        logger.info(f"Remaining states: {remaining}")
        
        if progress['partial_states']:
            logger(f"\nPartial states:")
            for state, info in progress['partial_states'].items():
                logger.info(f"  {state}: stopped at page {info['last_page']}, {info['animals_collected']} animals")
        
        if progress['failed_states']:
            logger.info(f"\nFailed states: {', '.join(progress['failed_states'])}")
        
    
    def combine_state_files(self, animal_type: str, status: str) -> Optional[str]:
        """
        Combine individual state CSV files into a single master file with deduplication.
        
        Reads all individual state CSV files, combines them into a single DataFrame,
        removes duplicate records based on animal ID, and maps Nevada ZIP codes to
        'NV' state designation. Saves the combined file with standardized naming.
        
        Args:
            animal_type (str): Type of animal files to combine
            status (str): Status of animal files to combine
            
        Returns:
            Optional[str]: Path to combined output file if successful, None if failed
            
        Side Effects:
            - Creates combined CSV file in the same directory
            - Logs information about records processed and duplicates removed
        """
        logger.info(f"Combining {status} {animal_type} files...")
        
        date_str = date.today().isoformat()
        directory = os.path.join(animal_type, date_str, status)
        
        if not os.path.exists(directory):
            logger.error(f"Directory {directory} doesn't exist")
            return
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and not f.startswith('all_')]
        
        if not csv_files:
            logger.warning(f"No CSV files found in {directory}")
            return
        
        all_dfs = []
        for file in csv_files:
            file_path = os.path.join(directory, file)
            try:
                df = pd.read_csv(file_path)
                all_dfs.append(df)
                logger.info(f"Loaded {len(df)} records from {file}")
            except Exception as e:
                logger.error(f"Error reading {file}: {e}")
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Remove duplicates
            initial_count = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=['id'], keep='first')
            final_count = len(combined_df)

            # Map the NV postcodes into 'NV'
            combined_df['stateQ'] = combined_df['stateQ'].astype(str)
            combined_df['stateQ_grouped'] = np.where(combined_df['stateQ'].isin(NV_POSTCODES), 'NV', combined_df['stateQ'])
            
            duplicates_removed = initial_count - final_count
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate records")
            
            # Save combined file
            output_file = os.path.join(directory, f"all_{status}_{animal_type}s.csv")
            combined_df.to_csv(output_file, index=False)
            
            logger.info(f"Combined file saved: {output_file} ({final_count} unique records)")
            return output_file
        else:
            logger.error("No data to combine")


def main() -> None:
    """
    Main execution function that orchestrates the data collection process.
    
    Loads environment variables, initializes the PetFinder client, displays current
    collection status, performs data collection with resumption capability, and
    combines individual state files into a master dataset.
    
    Environment Variables Required:
        - PETFINDER_API_KEY: PetFinder API key
        - PETFINDER_SECRET_KEY: PetFinder API secret
        
    Side Effects:
        - Creates directory structure for data organization
        - Downloads and saves animal data from PetFinder API
        - Creates progress tracking files for resumption
        - Generates combined dataset with deduplication
        - Writes comprehensive logs to file and console
        
    Raises:
        SystemExit: If required environment variables are missing
        Exception: For API authentication or data collection failures
    """
    load_dotenv()
    API_KEY = os.getenv("PETFINDER_API_KEY")
    SECRET = os.getenv("PETFINDER_SECRET_KEY")
    
    if not API_KEY or not SECRET:
        logger.error("Missing API credentials in .env file")
        return
    
    client = StateBasedPetfinderClient(API_KEY, SECRET)
    
    logger.info(f"<------------------------ Starting {ANIMAL_TYPE.upper()} Data Collection ------------------------>")
    
    # Check current status before starting
    client.get_status_summary(ANIMAL_TYPE, ADOPTION_STATUS)
    
    # Collect animals of a specific status after a certain published date
    try:
        client.collect_all_states(ANIMAL_TYPE, ADOPTION_STATUS, resume=True, after_date=PUBLISHED_AFTER_DATE)
        client.combine_state_files(ANIMAL_TYPE, ADOPTION_STATUS)
    except Exception as e:
        logger.error(f"Error collecting {ADOPTION_STATUS} {ANIMAL_TYPE}s: {e}")
    
    logger.info("<------------------------ Data Collection Complete ------------------------>")


if __name__ == "__main__":
    main()