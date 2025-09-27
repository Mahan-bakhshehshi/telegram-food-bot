def reserve_food(username, password, college="دانشگاه گیلان"):
    import time
    import os
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains

    LOGIN_URL = "https://samad.app/login"
    COLLEGE = "دانشگاه گیلان"
    
    # Configure Chrome for Render cloud deployment
    chrome_options = Options()
    
    # Essential options for Render/cloud deployment
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # Additional stability options for cloud
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--force-fieldtrials=*BackgroundTracing/default/")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--no-first-run")
    
    # Reduce resource usage
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        print("Starting Chrome driver for food reservation...")
        
        # Initialize Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.implicitly_wait(15)
        driver.set_page_load_timeout(60)
        
        wait = WebDriverWait(driver, 25)
        actions = ActionChains(driver)

        print(f"Starting reservation process for user: {username}")
        driver.get(LOGIN_URL)
        
        # Wait for page to load completely
        time.sleep(4)

        # College selection
        college_selectors = [
            "input[placeholder*='دانشگاه']",
            "input[placeholder*='جستجو']",
            "input[type='text']:first-of-type",
            "#root input[type='text']"
        ]

        college_input = None
        for selector in college_selectors:
            try:
                college_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"Found college input field")
                break
            except Exception:
                continue

        if not college_input:
            return "❌ نتوانست فیلد انتخاب دانشگاه را پیدا کند"

        # Click and enter college name
        college_input.click()
        time.sleep(1)
        college_input.clear()
        college_input.send_keys(COLLEGE)
        print(f"College name entered: {COLLEGE}")
        time.sleep(2)

        # Select دانشگاه گیلان from dropdown
        select_script = """
        var allItems = document.querySelectorAll('li, div[role="option"], .ant-select-item');
        for (var i = 0; i < allItems.length; i++) {
            var text = allItems[i].textContent || allItems[i].innerText;
            if (text.includes('گیلان')) {
                allItems[i].click();
                return true;
            }
        }
        return false;
        """
        result = driver.execute_script(select_script)
        if result:
            print("دانشگاه گیلان selected successfully")
        else:
            # Fallback keyboard navigation
            college_input.send_keys(Keys.ARROW_DOWN)
            college_input.send_keys(Keys.ENTER)
            print("College selected using keyboard navigation")
        
        time.sleep(2)

        # Find and fill username field
        username_selectors = [
            "input[type='text']:nth-of-type(2)",
            "input[placeholder*='نام کاربری']", 
            "input[placeholder*='Username']",
            "#root input[type='text']:nth-of-type(2)"
        ]

        username_input = None
        for selector in username_selectors:
            try:
                username_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                print("Found username input field")
                break
            except Exception:
                continue

        if username_input:
            username_input.clear()
            username_input.send_keys(username)
            print("Username entered successfully")
        else:
            return "❌ نتوانست فیلد نام کاربری را پیدا کند"

        # Find and fill password field
        try:
            password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            password_input.clear()
            password_input.send_keys(password)
            print("Password entered successfully")
        except Exception:
            return "❌ نتوانست فیلد رمز عبور را پیدا کند"

        # Click login button
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']")))
            submit_btn.click()
            print("Login button clicked")
            time.sleep(4)
        except Exception:
            return "❌ نتوانست دکمه ورود را پیدا کند"

        # Check for successful login and navigate to student interface
        try:
            print("Looking for student interface button...")
            student_interface_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button//span[contains(text(), 'ورود به رابط کاربری دانشجویی')]")
            ))
            student_interface_btn.click()
            print("Student interface accessed successfully")
            time.sleep(4)
        except Exception:
            return "❌ ورود ناموفق - لطفاً نام کاربری و رمز عبور را بررسی کنید"

        # Check wallet balance
        print("Checking wallet balance...")
        balance_script = """
        try {
            var walletLink = document.querySelector('a[href="/user/wallet"]');
            if (walletLink) {
                var balanceDivs = walletLink.querySelectorAll('div');
                for (var i = 0; i < balanceDivs.length; i++) {
                    var style = balanceDivs[i].getAttribute('style');
                    if (style && style.includes('direction: ltr')) {
                        var balanceText = balanceDivs[i].textContent || balanceDivs[i].innerText;
                        var balanceMatch = balanceText.match(/-?[\\d,]+/);
                        if (balanceMatch) {
                            var balance = parseInt(balanceMatch[0].replace(/,/g, ''));
                            return balance;
                        }
                    }
                }
            }
            return null;
        } catch(e) {
            return null;
        }
        """
        
        wallet_balance = None
        try:
            wallet_balance = driver.execute_script(balance_script)
        except Exception as e:
            print(f"Error getting balance: {e}")

        result_message = ""
        
        if wallet_balance is not None:
            result_message += f"💳 موجودی کیف پول: {wallet_balance:,} تومان\n"
            print(f"Wallet balance: {wallet_balance:,} تومان")

            if wallet_balance > -60000:
                print("Wallet balance is sufficient for reservation")
                result_message += "✅ موجودی کافی است\n"

                try:
                    # Navigate to food reservation
                    print("Navigating to food reservation...")
                    food_reservation_btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//span[contains(text(), 'رزرو غذا')]")
                    ))
                    food_reservation_btn.click()
                    print("Food reservation section accessed")
                    time.sleep(5)

                    # Click on سلف مرکزی
                    print("Selecting سلف مرکزی...")
                    self_markazi = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@class='self-list-item'][span[text()='سلف مرکزی']]")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", self_markazi)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", self_markazi)
                    print("سلف مرکزی selected successfully")
                    time.sleep(4)

                    # Close any modal dialogs
                    try:
                        modal_close_script = """
                        try {
                            var modals = document.querySelectorAll('.ant-modal');
                            var closedAny = false;
                            for (var i = 0; i < modals.length; i++) {
                                if (modals[i].style.display !== 'none' && modals[i].offsetWidth > 0) {
                                    var closeBtn = modals[i].querySelector('.ant-modal-close, .ant-modal-close-x');
                                    if (closeBtn && closeBtn.offsetWidth > 0) {
                                        closeBtn.click();
                                        closedAny = true;
                                    }
                                }
                            }
                            return closedAny;
                        } catch(e) {
                            return false;
                        }
                        """
                        driver.execute_script(modal_close_script)
                        time.sleep(2)
                    except Exception:
                        pass

                    # Find and click all reservation buttons
                    print("Looking for meal reservation buttons...")
                    time.sleep(3)
                    
                    reserve_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'رزرو')]]")
                    
                    if reserve_buttons:
                        reserved_count = 0
                        total_buttons = len(reserve_buttons)
                        print(f"Found {total_buttons} reservation buttons")
                        
                        for i, btn in enumerate(reserve_buttons, start=1):
                            try:
                                # Check if button is still available and clickable
                                if btn.is_enabled() and btn.is_displayed():
                                    # Scroll to button
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                    time.sleep(0.8)
                                    
                                    # Click the button
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(f"Reserved meal #{i}")
                                    reserved_count += 1
                                    time.sleep(1.2)  # Wait between reservations
                                else:
                                    print(f"Button #{i} not available for reservation")
                            except Exception as e:
                                print(f"Failed to reserve meal #{i}: {e}")
                        
                        if reserved_count > 0:
                            result_message += f"🍽️ تعداد {reserved_count} وعده غذایی از {total_buttons} با موفقیت رزرو شد!"
                            print(f"Successfully reserved {reserved_count} out of {total_buttons} meals")
                        else:
                            result_message += "⚠️ هیچ وعده غذایی قابل رزرو یافت نشد"
                    else:
                        result_message += "⚠️ در حال حاضر وعده غذایی برای رزرو موجود نیست"
                        print("No reservation buttons found")
                        
                except Exception as e:
                    print(f"Error during food reservation process: {e}")
                    result_message += f"❌ خطا در فرآیند رزرو غذا: مشکل در دسترسی به صفحه رزرو"

            else:
                result_message += f"❌ موجودی ناکافی ({wallet_balance:,} تومان)\nحداقل موجودی مورد نیاز: -60,000 تومان"
                print(f"Insufficient balance: {wallet_balance:,} تومان")
        else:
            result_message += "⚠️ نتوانست موجودی کیف پول را بررسی کند\nممکن است اطلاعات ورود اشتباه باشد"
            print("Could not retrieve wallet balance - possible login failure")

        return result_message

    except Exception as e:
        error_msg = f"خطای سیستمی در رزرو غذا: {str(e)}"
        print(f"System error during reservation: {e}")
        return error_msg

    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed successfully")
            except Exception:
                pass
