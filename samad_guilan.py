def reserve_food(username , password , college="دانشگاه گیلان"):
    import time
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains

    LOGIN_URL = "https://samad.app/login"

    COLLEGE = "دانشگاه گیلان"
    USERNAME = username
    PASSWORD = password

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 2)  # Adjust wait time if needed
    actions = ActionChains(driver)

    try:
        driver.get(LOGIN_URL)
        driver.maximize_window()

        # --- College selection ---
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
            except:
                continue

        if not college_input:
            print("❌ Could not find college input")
            driver.save_screenshot("college_input_debug.png")
            raise Exception("College input not found")

        college_input.click()
        time.sleep(1)
        college_input.clear()
        college_input.send_keys(COLLEGE)
        print(f"✅ Typed: {COLLEGE}")
        time.sleep(1)

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

        # --- Username & Password ---
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
                print(f"✅ Found username input using: {selector}")
                break
            except:
                continue

        if username_input:
            username_input.send_keys(USERNAME)
            print("✅ Username entered")

        password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password_input.send_keys(PASSWORD)
        print("✅ Password entered")

        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']")))
        submit_btn.click()
        print("✅ Login button clicked")
        time.sleep(1)

        # --- Student interface ---
        print("🔍 Looking for 'ورود به رابط کاربری دانشجویی' button...")
        student_interface_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button//span[contains(text(), 'ورود به رابط کاربری دانشجویی')]")
        ))
        student_interface_btn.click()
        print("✅ Clicked on 'ورود به رابط کاربری دانشجویی' button")
        time.sleep(1)

        # --- Wallet balance ---
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
        wallet_balance = driver.execute_script(balance_script)

        if wallet_balance is not None:
            print(f"💳 Current wallet balance: {wallet_balance:,} تومان")

            if wallet_balance > -60000:
                print("✅ Wallet balance is more than -60,000 تومان")

                # --- رزرو غذا ---
                print("🔍 Looking for 'رزرو غذا' button...")
                food_reservation_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'رزرو غذا')]")
                ))
                food_reservation_btn.click()
                print("✅ Clicked on 'رزرو غذا' button")
                time.sleep(2)

                # --- سلف مرکزی ---
                print("🔍 Trying to click on 'سلف مرکزی'...")
                try:
                    self_markazi = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='self-list-item'][span[text()='سلف مرکزی']]")
                    ))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", self_markazi)
                    driver.execute_script("arguments[0].click();", self_markazi)
                    print("✅ سلف مرکزی clicked via JavaScript")
                    time.sleep(2)

                    # --- Improved modal closing logic ---
                    print("🔍 Checking for 'به غذاها امتیاز دهید' modal...")
                    try:
                        modal_header = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'ant-modal')]//*[contains(text(), 'به غذاها امتیاز دهید')]")
                        ))
                        print("✅ Found modal with header 'به غذاها امتیاز دهید'")
                        close_selectors = [
                            "button.ant-modal-close",
                            ".ant-modal-close",
                            "button[aria-label='Close']",
                            "span.ant-modal-close-x"
                        ]
                        close_button = None
                        for selector in close_selectors:
                            try:
                                close_button = driver.find_element(By.CSS_SELECTOR, selector)
                                if close_button.is_displayed():
                                    print(f"✅ Found close button with selector: {selector}")
                                    break
                            except:
                                continue
                        if close_button:
                            driver.execute_script("arguments[0].click();", close_button)
                            print("✅ Modal closed successfully")
                        else:
                            print("❌ Could not find close button")
                    except Exception as modal_error:
                        print(f"⚠️ Modal not found or already closed: {modal_error}")

                    modal_check_script = """
                    var modals = document.querySelectorAll('.ant-modal');
                    for (var i = 0; i < modals.length; i++) {
                        if (modals[i].offsetWidth > 0 && modals[i].offsetHeight > 0) {
                            var closeBtn = modals[i].querySelector('.ant-modal-close');
                            if (closeBtn) {
                                closeBtn.click();
                                return 'Modal closed';
                            }
                        }
                    }
                    return 'No visible modal found';
                    """
                    modal_result = driver.execute_script(modal_check_script)
                    print(f"📋 Modal check result: {modal_result}")

                    # --- رزرو همه غذاها ---
                    print("🔍 Looking for رزرو buttons...")
                    reserve_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'رزرو')]]")
                    if reserve_buttons:
                        print(f"✅ Found {len(reserve_buttons)} رزرو buttons")
                        for i, btn in enumerate(reserve_buttons, start=1):
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                driver.execute_script("arguments[0].click();", btn)
                                print(f"✅ Clicked رزرو button #{i}")
                                time.sleep(0.5)
                            except Exception as e:
                                print(f"❌ Failed to click رزرو button #{i}: {e}")
                    else:
                        print("⚠️ No رزرو buttons found")

                except Exception as e1:
                    print(f"⚠️ JS click failed: {e1}")
                    try:
                        actions.move_to_element(self_markazi).click().perform()
                        print("✅ سلف مرکزی clicked via ActionChains")
                    except Exception as e2:
                        print(f"❌ Could not click سلف مرکزی: {e2}")

            else:
                print(f"❌ Wallet balance is {wallet_balance:,} تومان (less than or equal to -60,000 تومان)")
                print("⏭️ Skipping the click actions")
        else:
            print("❌ Could not find wallet balance on the page")

        # --- Final check ---
        print("📄 Current URL:", driver.current_url)
        print("🎉 Script execution completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("error_debug.png")
        print("📸 Screenshot saved as 'error_debug.png'")

    finally:
        print("⏳ Keeping browser open for 30 seconds for inspection...")
        time.sleep(30)
        driver.quit()
