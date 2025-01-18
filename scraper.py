from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
import pandas as pd # type: ignore
import time
from datetime import datetime

class SGCarMartScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = None
        
    def start_driver(self):
        """Inisialisasi WebDriver"""
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
    def close_driver(self):
        """Tutup WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def get_car_links(self, page_num):
        """Mengambil semua link mobil dari halaman tertentu"""
        url = f"https://www.sgcarmart.com/used_cars/listing.php?PAGE={page_num}"
        self.driver.get(url)
        time.sleep(2)  # Tunggu loading
        
        # Ambil semua link mobil
        car_elements = self.driver.find_elements(By.CSS_SELECTOR, "h2.link a")
        return [elem.get_attribute('href') for elem in car_elements]
    
    def get_car_details(self, car_url):
        """Mengambil detail dari halaman mobil tertentu"""
        self.driver.get(car_url)
        time.sleep(2)  # Tunggu loading
        
        try:
            car_data = {
                'url': car_url,
                'scraping_date': datetime.now().strftime('%Y-%m-%d'),
                'title': self._safe_get_text('h1'),
                'price': self._safe_get_text('.price'),
                'registration_date': self._safe_get_detail('Registration Date'),
                'depreciation': self._safe_get_detail('Depreciation'),
                'mileage': self._safe_get_detail('Mileage'),
                'transmission': self._safe_get_detail('Transmission'),
                'engine_cap': self._safe_get_detail('Engine Cap'),
                'road_tax': self._safe_get_detail('Road Tax'),
                'power': self._safe_get_detail('Power'),
                'type_of_vehicle': self._safe_get_detail('Type of Vehicle'),
                'category': self._safe_get_detail('Category'),
                'coe': self._safe_get_detail('COE'),
                'no_of_owners': self._safe_get_detail('No. of Owners'),
                'availability': self._safe_get_detail('Availability')
            }
            return car_data
        except Exception as e:
            print(f"Error scraping car details from {car_url}: {str(e)}")
            return None
    
    def _safe_get_text(self, selector):
        """Safely get text from element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return None
    
    def _safe_get_detail(self, label):
        """Safely get specific detail by label"""
        try:
            xpath = f"//td[contains(text(), '{label}')]/following-sibling::td"
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except:
            return None
    
    def scrape_cars(self, start_page=1, num_pages=1):
        """
        Scrape data mobil dari beberapa halaman
        
        Parameters:
        start_page (int): Halaman awal untuk scraping
        num_pages (int): Jumlah halaman yang akan di-scrape
        """
        all_cars_data = []
        
        try:
            self.start_driver()
            
            for page in range(start_page, start_page + num_pages):
                print(f"Scraping halaman {page}...")
                car_links = self.get_car_links(page)
                
                for link in car_links:
                    car_data = self.get_car_details(link)
                    if car_data:
                        all_cars_data.append(car_data)
                        print(f"Berhasil scrape data: {car_data['title']}")
                
                # Simpan data setiap selesai satu halaman
                df = pd.DataFrame(all_cars_data)
                df.to_csv(f'sgcarmart_data_{datetime.now().strftime("%Y%m%d")}.csv', 
                         index=False)
                
        finally:
            self.close_driver()
        
        return all_cars_data

# Contoh penggunaan
if __name__ == "__main__":
    scraper = SGCarMartScraper()
    # Scrape 2 halaman pertama sebagai contoh
    cars_data = scraper.scrape_cars(start_page=1, num_pages=10)
    
    # Tampilkan ringkasan data
    df = pd.DataFrame(cars_data)
    print("\nRingkasan data yang berhasil di-scrape:")
    print(f"Jumlah mobil: {len(df)}")
    print("\nContoh data:")
    print(df.head())