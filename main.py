from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import argparse

def scraping(spotify_playlist_url, output_csv):
    # Path to your chromedriver
    CHROME_DRIVER_PATH = '/Users/eyap/Downloads/chromedriver-mac-x64/chromedriver'

    # Setting up Chrome options for headless mode
    options = Options()
    options.headless = True

    # Initialize the driver within the function
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.implicitly_wait(10)  # Set implicit wait immediately after initializing the driver

    try:
        driver.get(spotify_playlist_url)
        time.sleep(3)  # Extra wait to ensure the page loads completely
        
        # Scroll to the bottom to load all elements
        last_height = driver.execute_script("return document.querySelector('main').parentElement.parentElement.scrollTop")
        
        while True: 
            driver.execute_script("document.querySelector('main').parentElement.parentElement.scrollBy(0, document.querySelector('main').parentElement.parentElement.clientHeight)")
            time.sleep(2)
            
            new_height = driver.execute_script("return document.querySelector('main').parentElement.parentElement.scrollTop")
            print(f"Last height: {last_height}, New height: {new_height}")
            if new_height == last_height:
                break
            
            last_height = new_height

        # Now that all data is loaded, scrape it
        titles = driver.find_elements(By.XPATH, '//main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[1]/a[1]')
        artists = driver.find_elements(By.XPATH, '//main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div[1]/span[last()]')
        albums = driver.find_elements(By.XPATH, '//main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[3]')
        durations = driver.find_elements(By.XPATH, '//main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[5]')
        songs_img = driver.find_elements(By.XPATH, '//main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]/div/div[1]/div[2]/img')
      
        # Debugging: print lengths of elements found
        print(f"Titles found: {len(titles)}")
        print(f"Artists found: {len(artists)}")
        print(f"Albums found: {len(albums)}")
        print(f"Durations found: {len(durations)}")
        print(f"Images found: {len(songs_img)}")

        all_data = []

        for index in range(min(len(titles), len(artists), len(albums), len(durations), len(songs_img))):
            all_data.append({
                "title": titles[index].text,
                "artist": artists[index].text,
                "album": albums[index].text,
                "duration": durations[index].text,
                "album_image": songs_img[index].get_attribute('src')
            })
            
        df = pd.DataFrame(data=all_data)
        df.to_csv(output_csv, index=False)

        return f"Data has been saved in {output_csv}"
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser(description="Scrape Spotify playlist data to CSV")
    
    # Adding arguments
    parser.add_argument("-u", "--url", help="Spotify playlist URL", required=True)
    parser.add_argument("-o", "--output", help="Output CSV file path", default="playlist.csv")
    
    # Read arguments from command line
    args = parser.parse_args()

    print(scraping(args.url, args.output))
