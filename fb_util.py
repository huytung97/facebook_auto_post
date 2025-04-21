import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class FacebookGroupPoster:
    def __init__(self, chrome_user_data_dir, profile_name, headless=False):
        """
        Initialize the Facebook Group Poster using Chrome profile
        
        Args:
            chrome_user_data_dir (str): Path to Chrome User Data directory
            profile_name (str): Name of the profile to use (e.g., 'Default', 'Profile 1')
            headless (bool): Run browser in headless mode if True
        """
        # Set up options
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={chrome_user_data_dir}")
        options.add_argument(f"profile-directory={profile_name}")
        
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        
        # Add additional options to troubleshoot profile loading
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        print(f"Loading Chrome with profile: {profile_name}")
        print(f"User data directory: {chrome_user_data_dir}")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Reduced default wait time from 20 to 10 seconds
            self.wait = WebDriverWait(self.driver, 10)
            self.short_wait = WebDriverWait(self.driver, 3)
            
            # Reduced delay from 3 to 1 second
            time.sleep(1)
            print("Chrome launched successfully")
            
        except Exception as e:
            print(f"Error initializing Chrome: {str(e)}")
            raise
    
    def post_to_group(self, group_url, post_text, image_folder):
        """
        Post to a Facebook group
        
        Args:
            group_url (str): URL of the Facebook group
            post_text (str): Text content of the post
            image_folder (str): Path to folder containing images to be uploaded
        """
        try:
            # Navigate to the group
            self.driver.get(group_url)
            # Dynamic wait for page load instead of fixed sleep
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            except:
                pass

            post_texts = [
                "Write something",
                "Write something...",
                "Create a post",
                "Viết gì đó",
                "Đăng bài",
                "Bạn viết gì đi..."
            ]

            # Find and click on the post input field - multiple selectors for different languages
            post_box_selectors = "//div[@role='button' and @tabindex='0']"

            post_box = None
            postbox_tmps = self.driver.find_elements(By.XPATH, post_box_selectors)
            for postbox in postbox_tmps:
                try:
                    if postbox.text in post_texts:
                        post_box = self.wait.until(EC.element_to_be_clickable(postbox))
                        post_box.click()
                        time.sleep(1) 
                        break
                except:
                    continue

            
            if not post_box or not self._is_post_dialog_open():
                print("Could not find the post box. Trying alternative methods...")
                return False
                    
            
            # Wait for the post dialog to appear
            try:
                post_dialog = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
            except:
                print("Post dialog not found. Trying to continue anyway...")
            
            # Type the post text - try multiple selectors for the text area
            text_area_selectors = [
                "//div[contains(@aria-label, 'Write') or contains(@aria-label, 'Viết')]",
                "//div[contains(@aria-label, 'post') or contains(@aria-label, 'bài viết')]",
                "//div[@contenteditable='true' and @role='textbox']",
                "//div[@data-contents='true']//div[@data-block='true']//div",
                "//div[@role='presentation']//div[@role='textbox']"
            ]
            
            post_text_area = None
            for selector in text_area_selectors:
                try:
                    post_text_area = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    post_text_area.click()
                    # Human-like small pause
                    time.sleep(0.3)  
                    break
                except:
                    continue
            
            if post_text_area:
                try:
                    post_text_area.click()
                    # Human-like small pause
                    time.sleep(0.3)

                    # Add randomized typing pattern to mimic human behavior
                    actions = ActionChains(self.driver)
                    actions.move_to_element(post_text_area).click()
                    
                    # Type with realistic, varying human speed
                    for char in post_text:
                        actions.send_keys(char)
                        if random.random() < 0.1:  # Random pauses while typing
                            time.sleep(random.uniform(0.05, 0.2))
                    
                    actions.perform()
                    print("Post text input successful")
                except Exception as e:
                    print(f"Failed to input post text: {str(e)}")
                    return False
            
            # Get all images from the folder
            # Upload images only if image_folder is provided
            if image_folder:
                image_paths = self._get_images_from_folder(image_folder)
                if image_paths and len(image_paths) > 0:
                    self._upload_images(image_paths)
                else:
                    print(f"No images found in folder: {image_folder}")
            else:
                print("No image folder provided. Skipping image upload.")
            
            # Add small random delay before posting to appear more human-like
            time.sleep(random.uniform(0.5, 1.5))
            
            # Find and click the Post button - multiple selectors for different languages
            post_button_selectors = [
                "//div[@role='dialog']//div[@role='button' and (contains(text(), 'Post') or contains(text(), 'Đăng'))]",
                "//div[@aria-label='Post' or @aria-label='Đăng']",
                "//button[contains(text(), 'Post') or contains(text(), 'Đăng')]",
                "//div[@role='button' and contains(@aria-label, 'Post') or contains(@aria-label, 'Đăng')]"
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    post_button.click()
                    break
                except:
                    continue
            
            if not post_button:
                print("Could not find post button")
                return False
            
            # Wait for post to complete - dynamic wait for confirmation
            try:
                # Look for indicators that post was successful
                self.wait.until(lambda d: "posted" in d.page_source.lower() or 
                               "đã đăng" in d.page_source.lower() or
                               not self._is_post_dialog_open())
                # Short cooldown after successful post
                time.sleep(2)
            except:
                # Fallback to shorter fixed wait if we can't detect success
                time.sleep(5)  # Reduced from 10 seconds
                
            print(f"Posted to group: {group_url}")
            return True
            
        except Exception as e:
            print(f"Error posting to group {group_url}: {str(e)}")
            return False
    
    def _is_post_dialog_open(self):
        """Check if the post dialog is open"""
        try:
            self.driver.find_element(By.XPATH, "//div[@role='dialog']")
            return True
        except NoSuchElementException:
            return False
    
    def _get_images_from_folder(self, folder_path):
        """Get all image files from a folder"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        image_paths = []
        
        try:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        image_paths.append(os.path.join(folder_path, file))
                
                print(f"Found {len(image_paths)} images in folder {folder_path}")
            else:
                print(f"Folder not found: {folder_path}")
        except Exception as e:
            print(f"Error reading image folder: {str(e)}")
            
        return image_paths
    
    def _upload_images(self, image_paths):
        """Upload images to the post by simulating normal user behavior"""
        try:
            # Step 1: Find and click the "Photo/Video" button
            photo_button_selectors = "//div[@role='dialog']//div[@role='button' and @tabindex='0']"
            elements = self.driver.find_elements(By.XPATH, photo_button_selectors)
            aria_labels_for_uploading_photos = [
                'Photo/video',
                'Ảnh/Video',
                'Add Photos',
                'Thêm ảnh',
                'Ảnh/video'
            ]
            
            photo_button = None
            
            for e in elements:
                if e.get_attribute('aria-label') in aria_labels_for_uploading_photos:
                    try:
                        photo_button = self.wait.until(EC.element_to_be_clickable(e))
                        photo_button.click()
                        print("Clicked on the Photo/Video button")
                        time.sleep(1)  # Reduced from 2 seconds
                        break
                    except Exception as e:
                        print(f"Error clicking Photo/Video button: {e}")
                        continue
            
            if not photo_button:
                print("Could not find Photo/Video button")
                return
            
            # Step 2: Find and click the "Add Photos" or "Upload Image" button
            add_image_button = self.driver.find_element(By.XPATH, "//div[@role='dialog']//input[@type='file']")
            if add_image_button:
                print("Found file input for image upload.")
                # Prepare all image paths
                all_paths = "\n".join([os.path.abspath(path) for path in image_paths])
                
                # Step 3: Upload the images
                add_image_button.send_keys(all_paths)
                print(f"Uploading {len(image_paths)} images...")
                
                # Dynamic wait for image upload based on number and size
                num_images = len(image_paths)
                base_wait = 3  # Base wait time
                per_image_wait = 1  # Additional time per image
                max_wait = 15  # Maximum wait time
                
                wait_time = min(base_wait + (num_images * per_image_wait), max_wait)
                
                # Wait for upload completion indicators
                try:
                    # First wait for preview thumbnails to appear
                    self.wait.until(EC.presence_of_element_located((By.XPATH, 
                                    "//div[@role='dialog']//img[contains(@alt, 'preview') or contains(@alt, 'xem trước')]")))
                    
                    # Then wait for upload progress indicators to disappear
                    self.wait.until_not(EC.presence_of_element_located((By.XPATH, 
                                       "//div[@role='dialog']//div[contains(@aria-valuetext, 'Upload') or contains(@aria-valuetext, 'Đang tải')]")))
                except:
                    # If we can't detect completion, use the calculated wait time as fallback
                    time.sleep(wait_time)
            else:
                print("Could not find the file input for image upload.")
        
        except Exception as e:
            print(f"Error in image upload process: {str(e)}")
        
    def post_to_multiple_groups(self, group_urls, post_text, image_folder, delay_between_posts=(45, 120)):
        """
        Post to multiple Facebook groups with random delays between posts
        
        Args:
            group_urls (list): List of group URLs
            post_text (str): Text content of the post
            image_folder (str): Path to folder containing images to be uploaded
            delay_between_posts (tuple): Min and max seconds to wait between posts
        """
        success_count = 0
        
        # Randomize post order to appear more natural
        if len(group_urls) > 3:
            random.shuffle(group_urls)
        
        for i, url in enumerate(group_urls):
            print(f"Posting to group {i+1}/{len(group_urls)}: {url}")
            success = self.post_to_group(url, post_text, image_folder)
            
            if success:
                success_count += 1
            
            # Add random delay between posts (except after the last post)
            if i < len(group_urls) - 1:
                # Calculate adaptive delay based on number of posts made
                # More posts made = higher risk, so increase delay gradually
                progress_factor = min((i + 1) / len(group_urls) * 0.5, 0.5)  # Up to 50% increase in delay as we progress
                
                min_delay = delay_between_posts[0] * (1 + progress_factor)
                max_delay = delay_between_posts[1] * (1 + progress_factor)
                
                delay = random.uniform(min_delay, max_delay)
                print(f"Waiting {int(delay)} seconds before next post...")
                time.sleep(delay)
        
        print(f"Posted successfully to {success_count} out of {len(group_urls)} groups")
        return success_count
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("Browser closed")