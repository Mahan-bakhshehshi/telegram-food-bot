def reserve_food(username, password, college="دانشگاه گیلان"):
    import time
    import os
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains

    LOGIN_URL = "https://samad.app/login"
    COLLEGE = "دانشگاه گیلان"
    
    # Configure Chrome for cloud deployment
    chrome_options = Options()
    
    # Essential options for Railway/cloud deployment
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Reduce resource usage
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        print("🚀 Initializing Chrome driver...")
        
        # Try to use system Chrome first (better for Railway)
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        except Exception as e:
            print(f"ChromeDriverManager failed: {e}")
            # Fallback to system chromedriver
            service = Service('/usr/bin/chromedriver')  # Common path on Linux
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(60)
        
        wait = WebDriverWait(driver, 20)  # Increased timeout
        actions = ActionChains(driver)

        print(f"🚀 Starting reservation for user: {username}")
        driver.get(LOGIN_URL)
        
        # Wait for page to load
        time.sleep(3)

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
                print(f"✅ Found college input using: {selector}")
                break
            except Exception:
                continue

        if not college_input:
            return "❌ نتوانست فیلد دانشگاه را پیدا کند"

        college_input.click()
        time.sleep(1)
        college_input.clear()
        college_input.send_keys(COLLEGE)
        print(f"✅ Typed: {COLLEGE}")
        time.sleep(2)

        # Select دانشگاه گیلان
        select_script = """
        var allItems = document.querySelectorAll('li, div[role="option"]');
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
            print("✅ دانشگاه گیلان selected")
        else:
            college_input.send_keys(Keys.ARROW_DOWN)
            college_input.send_keys(Keys.ENTER)
            print("✅ Selected using keyboard navigation")
        
        time.sleep(2)

        # Username & Password
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
                print(f"✅ Found username input")
                break
            except Exception:
                continue

        if username_input:
            username_input.clear()
            username_input.send_keys(username)
            print("✅ Username entered")
        else:
            return "❌ نتوانست فیلد نام کاربری را پیدا کند"

        try:
            password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            password_input.clear()
            password_input.send_keys(password)
            print("✅ Password entered")
        except Exception:
            return "❌ نتوانست فیلد رمز عبور را پیدا کند"

        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']")))
            submit_btn.click()
            print("✅ Login button clicked")
            time.sleep(3)
        except Exception:
            return "❌ نتوانست دکمه ورود را پیدا کند"

        # Check for login success
        try:
            # Student interface
            print("🔍 Looking for student interface button...")
            student_interface_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button//span[contains(text(), 'ورود به رابط کاربری دانشجویی')]")
            ))
            student_interface_btn.click()
            print("✅ Clicked on student interface button")
            time.sleep(3)
        except Exception:
            return "❌ ورود ناموفق - لطفاً نام کاربری و رمز عبور را بررسی کنید"

        # Check wallet balance
        print("💰 Checking wallet balance...")
        balance_script = """
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
        """
        
        wallet_balance = None
        try:
            wallet_balance = driver.execute_script(balance_script)
        except Exception as e:
            print(f"Error getting balance: {e}")

        result_message = ""
        
        if wallet_balance is not None:
            result_message += f"💳 موجودی کیف پول: {wallet_balance:,} تومان\n"
            print(f"💳 Current wallet balance: {wallet_balance:,} تومان")

            if wallet_balance > -60000:
                print("✅ Wallet balance is sufficient")
                result_message += "✅ موجودی کافی است\n"

                try:
                    # Food reservation
                    print("🔍 Looking for food reservation button...")
                    food_reservation_btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//span[contains(text(), 'رزرو غذا')]")
                    ))
                    food_reservation_btn.click()
                    print("✅ Clicked on food reservation button")
                    time.sleep(4)

                    # سلف مرکزی
                    print("🔍 Trying to click on سلف مرکزی...")
                    self_markazi = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@class='self-list-item'][span[text()='سلف مرکزی']]")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", self_markazi)
                    driver.execute_script("arguments[0].click();", self_markazi)
                    print("✅ سلف مرکزی clicked")
                    time.sleep(3)

                    # Close any modal that might appear
                    try:
                        modal_close_script = """
                        var modals = document.querySelectorAll('.ant-modal');
                        var closedAny = false;
                        for (var i = 0; i < modals.length; i++) {
                            if (modals[i].offsetWidth > 0 && modals[i].offsetHeight > 0) {
                                var closeBtn = modals[i].querySelector('.ant-modal-close, .ant-modal-close-x');
                                if (closeBtn) {
                                    closeBtn.click();
                                    closedAny = true;
                                }
                            }
                        }
                        return closedAny;
                        """
                        driver.execute_script(modal_close_script)
                        time.sleep(1)
                    except Exception:
                        pass

                    # Reserve all meals
                    print("🔍 Looking for reservation buttons...")
                    time.sleep(2)  # Wait for page to load
                    
                    reserve_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'رزرو')]]")
                    
                    if reserve_buttons:
                        reserved_count = 0
                        print(f"✅ Found {len(reserve_buttons)} reservation buttons")
                        
                        for i, btn in enumerate(reserve_buttons, start=1):
                            try:
                                # Check if button is still clickable
                                if btn.is_enabled() and btn.is_displayed():
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                    time.sleep(0.5)
                                    driver.execute_script("arguments[0].click();", btn)
                                    print(f"✅ Clicked reservation button #{i}")
                                    reserved_count += 1
                                    time.sleep(1)  # Wait between clicks
                            except Exception as e:
                                print(f"❌ Failed to click button #{i}: {e}")
                        
                        if reserved_count > 0:
                            result_message += f"🍽️ تعداد {reserved_count} وعده غذایی رزرو شد!"
                        else:
                            result_message += "⚠️ هیچ وعده غذایی برای رزرو یافت نشد"
                    else:
                        result_message += "⚠️ هیچ دکمه رزرو فعالی یافت نشد"
                        print("⚠️ No reservation buttons found")
                        
                except Exception as e:
                    print(f"❌ Error in food reservation: {e}")
                    result_message += f"❌ خطا در رزرو غذا: {str(e)}"

            else:
                result_message += f"❌ موجودی ناکافی ({wallet_balance:,} تومان)\nحداقل موجودی مورد نیاز: -60,000 تومان"
                print(f"❌ Insufficient balance: {wallet_balance:,} تومان")
        else:
            result_message += "⚠️ نتوانست موجودی کیف پول را بررسی کند - ممکن است ورود ناموفق بوده باشد"
            print("❌ Could not find wallet balance - possibly login failed")

        return result_message

    except Exception as e:
        error_msg = f"خطا در سیستم رزرو: {str(e)}"
        print(f"❌ Main Error: {e}")
        return error_msg

    finally:
        if driver:
            try:
                driver.quit()
                print("🔒 Browser closed")
            except Exception:
                pass
