"""
Browser-based token extraction for Spond authentication.

Opens a browser window to the Spond login page, waits for the user to
complete login (including any 2FA), then extracts the bearer token
from the browser session.

Falls back to manual instructions if selenium is not installed.
"""

import json
import time
import webbrowser

SPOND_LOGIN_URL = "https://club.spond.com/"


def _detect_default_browser() -> str:
    """
    Detect the user's default browser on Windows, macOS, or Linux.

    Returns:
        str: 'edge', 'chrome', 'firefox', or 'unknown'
    """
    import subprocess
    import sys

    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice",
            ) as key:
                prog_id = winreg.QueryValueEx(key, "ProgId")[0].lower()
                if "edge" in prog_id:
                    return "edge"
                if "chrome" in prog_id:
                    return "chrome"
                if "firefox" in prog_id:
                    return "firefox"
        except Exception:
            pass

    elif sys.platform == "darwin":
        # macOS: read the LaunchServices plist for the https handler
        try:
            import os
            import plistlib
            plist_path = os.path.expanduser(
                "~/Library/Preferences/com.apple.LaunchServices/"
                "com.apple.launchservices.secure.plist"
            )
            result = subprocess.run(
                ["plutil", "-convert", "xml1", "-o", "-", plist_path],
                capture_output=True, timeout=5,
            )
            if result.returncode == 0:
                data = plistlib.loads(result.stdout)
                for handler in data.get("LSHandlers", []):
                    if handler.get("LSHandlerURLScheme") == "https":
                        bundle_id = handler.get("LSHandlerRoleAll", "").lower()
                        if "edge" in bundle_id:
                            return "edge"
                        if "chrome" in bundle_id:
                            return "chrome"
                        if "firefox" in bundle_id:
                            return "firefox"
        except Exception:
            pass

    else:
        # Linux: use xdg-settings
        try:
            result = subprocess.run(
                ["xdg-settings", "get", "default-web-browser"],
                capture_output=True, text=True, timeout=5,
            )
            browser = result.stdout.strip().lower()
            if "edge" in browser:
                return "edge"
            if "chrome" in browser or "chromium" in browser:
                return "chrome"
            if "firefox" in browser:
                return "firefox"
        except Exception:
            pass

    return "unknown"


def _try_chrome(webdriver):
    """Try to create a Chrome WebDriver with network interception."""
    import tempfile
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService

    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # Use a temp profile so we don't collide with an already-running browser
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp(prefix='spond_chrome_')}")
    # Enable performance logging to capture network requests (Authorization headers)
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception:
        return webdriver.Chrome(options=options)


def _try_edge(webdriver, inprivate=False):
    """Try to create an Edge WebDriver with network interception."""
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService

    options = EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    if inprivate:
        options.add_argument("--inprivate")
    # Enable performance logging to capture network requests (Authorization headers)
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    try:
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    except Exception:
        return webdriver.Edge(options=options)


def _try_firefox(webdriver):
    """Try to create a Firefox WebDriver."""
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService

    options = FirefoxOptions()

    try:
        from webdriver_manager.firefox import GeckoDriverManager
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    except Exception:
        return webdriver.Firefox(options=options)


def _has_browser_windows(name: str) -> bool:
    """Check if a browser has visible windows open (ignores background processes)."""
    import subprocess
    import sys

    if sys.platform != "win32":
        return False

    process_names = {
        "edge": "msedge.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
    }
    proc = process_names.get(name)
    if not proc:
        return False

    try:
        # Use tasklist /V to get window titles — real windows have a title,
        # background processes show "N/A"
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {proc}", "/V", "/NH", "/FO", "CSV"],
            capture_output=True, text=True, timeout=10,
        )
        # Internal process titles to ignore
        ignore_titles = {"N/A", "OleMainThreadWndName", ""}
        for line in result.stdout.strip().splitlines():
            if proc.lower() not in line.lower():
                continue
            # CSV format: last field is the window title (quoted)
            parts = line.split('","')
            if parts:
                title = parts[-1].strip().strip('"')
                if title not in ignore_titles:
                    return True
        return False
    except Exception:
        return False


def _create_driver(inprivate=False):
    """
    Create a Selenium WebDriver, trying the user's default browser first
    then falling back to others.

    If the default browser has visible windows open, exits with a message
    asking the user to close it first.

    Args:
        inprivate: If True, use InPrivate/Incognito mode

    Returns:
        WebDriver instance

    Raises:
        RuntimeError: If no supported browser can be found
        SystemExit: If the default browser has windows open
    """
    from selenium import webdriver

    default = _detect_default_browser()
    browser_labels = {"edge": "Edge", "chrome": "Chrome", "firefox": "Firefox"}

    # Check if the default browser has visible windows open
    if default != "unknown" and _has_browser_windows(default):
        label = browser_labels.get(default, default)
        print(f"\nError: {label} is currently open.")
        print(f"Please close all {label} windows and try again.")
        print("\nTip: Check the system tray — {label} may be running in the background.")
        print(f"     Right-click the {label} icon in the system tray and choose 'Close'.")
        raise SystemExit(1)

    # Map browser names to their factory functions
    browsers = {
        "edge": ("Edge", lambda wd: _try_edge(wd, inprivate=inprivate)),
        "chrome": ("Chrome", _try_chrome),
        "firefox": ("Firefox", _try_firefox),
    }

    # Build ordered list: default browser first, then the rest
    order = []
    if default in browsers:
        order.append(default)
    for name in browsers:
        if name not in order:
            order.append(name)

    errors = []
    for name in order:
        label, factory = browsers[name]
        try:
            driver = factory(webdriver)
            suffix = " (InPrivate)" if (name == "edge" and inprivate) else ""
            if name == default:
                print(f"Using {label}{suffix} (your default browser)...")
            else:
                print(f"Using {label}{suffix}...")
            return driver
        except Exception as e:
            errors.append(f"{label}: {e}")

    raise RuntimeError(
        "Could not find a supported browser (Chrome, Edge, or Firefox).\n"
        "Please install one of them, or use --bearer-token instead.\n"
        + "\n".join(errors)
    )


def _extract_token_selenium(force_private=False) -> str:
    """
    Open a Selenium-controlled browser, let the user log in to Spond,
    and extract the bearer token from network traffic, storage, or cookies.

    Args:
        force_private: If True, use InPrivate/Incognito from the start

    Returns:
        str: Bearer token

    Raises:
        RuntimeError: If token extraction fails
    """
    driver = _create_driver(inprivate=force_private)

    try:
        token = _setup_and_extract(driver)
        if token:
            return token
        raise RuntimeError("Could not find authentication token after login")
    finally:
        driver.quit()


def _setup_and_extract(driver) -> str:
    """
    Set up CDP monitoring, navigate to Spond, and extract the token.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        str: Bearer token, or empty string if not found
    """
    # Enable CDP network monitoring to capture Authorization headers
    try:
        driver.execute_cdp_cmd("Network.enable", {})
    except Exception:
        pass

    # CRITICAL: Inject interceptor script to run BEFORE any page JS,
    # including after login redirects. This ensures we capture the
    # Authorization header even on the first API call after login.
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": _INTERCEPTOR_JS},
        )
    except Exception:
        pass  # Non-Chromium browsers won't support this

    # Navigate to Spond login page
    driver.get(SPOND_LOGIN_URL)
    time.sleep(2)

    if "spond" not in driver.current_url.lower():
        raise RuntimeError(
            "Could not navigate browser to Spond login page. "
            "Try closing all browser windows first, or use --private."
        )

    # Inject script to intercept fetch/XHR Authorization headers
    _inject_token_interceptor(driver)

    print("\nA browser window has opened to the Spond login page.")
    print("Please log in (including any 2FA verification).")
    print("The token will be extracted automatically once you're logged in.\n")

    token = _poll_for_token(driver, timeout=300)
    if token:
        print("\nToken extracted successfully!")
    return token


# JavaScript that monkey-patches fetch() and XMLHttpRequest to capture
# any Authorization: Bearer header sent to api.spond.com
_INTERCEPTOR_JS = """
(function() {
    if (window.__spond_token_captured) return;
    window.__spond_token_captured = '';

    // Intercept fetch()
    var origFetch = window.fetch;
    window.fetch = function() {
        var url = (arguments[0] instanceof Request)
            ? arguments[0].url
            : String(arguments[0]);
        var opts = arguments[1] || {};
        if (url.indexOf('api.spond.com') !== -1 && opts.headers) {
            var hdrs = opts.headers;
            // Headers can be a plain object, Headers instance, or array
            if (hdrs instanceof Headers) {
                var auth = hdrs.get('Authorization') || hdrs.get('authorization');
                if (auth) window.__spond_token_captured = auth;
            } else if (typeof hdrs === 'object') {
                for (var k in hdrs) {
                    if (k.toLowerCase() === 'authorization') {
                        window.__spond_token_captured = hdrs[k];
                        break;
                    }
                }
            }
        }
        // Also check Request objects
        if (arguments[0] instanceof Request && url.indexOf('api.spond.com') !== -1) {
            try {
                var auth = arguments[0].headers.get('Authorization')
                    || arguments[0].headers.get('authorization');
                if (auth) window.__spond_token_captured = auth;
            } catch(e) {}
        }
        return origFetch.apply(this, arguments);
    };

    // Intercept XMLHttpRequest
    var origOpen = XMLHttpRequest.prototype.open;
    var origSetHeader = XMLHttpRequest.prototype.setRequestHeader;
    XMLHttpRequest.prototype.open = function(method, url) {
        this._spond_url = url;
        return origOpen.apply(this, arguments);
    };
    XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
        if (this._spond_url && this._spond_url.indexOf('api.spond.com') !== -1
            && name.toLowerCase() === 'authorization') {
            window.__spond_token_captured = value;
        }
        return origSetHeader.apply(this, arguments);
    };
})();
"""


def _inject_token_interceptor(driver):
    """Inject JS that captures Authorization headers from API calls."""
    try:
        driver.execute_script(_INTERCEPTOR_JS)
    except Exception:
        pass  # Page might not be ready yet; we'll retry in the poll loop


def _poll_for_token(driver, timeout: int = 300) -> str:
    """
    Poll the browser for an auth token via multiple strategies.

    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum seconds to wait

    Returns:
        str: The bearer token, or empty string if not found
    """
    start = time.time()
    poll_count = 0
    logged_in = False

    while time.time() - start < timeout:
        time.sleep(2)
        poll_count += 1

        # Re-inject interceptor in case page navigated (login redirect)
        _inject_token_interceptor(driver)

        # Detect login by checking if URL has changed from login page
        try:
            url = driver.current_url.lower()
            if not logged_in and "spond.com" in url and "/login" not in url and "landing" not in url:
                if url != SPOND_LOGIN_URL.lower().rstrip("/") + "/" and url != SPOND_LOGIN_URL.lower():
                    logged_in = True
                    print("Login detected! Extracting token...")
                    # Wait for initial API calls to complete, then check
                    time.sleep(3)
        except Exception:
            pass

        # --- Strategy 1: JS interceptor (set before page load via CDP) ---
        try:
            captured = driver.execute_script(
                "return window.__spond_token_captured || '';"
            )
            if captured:
                token = _extract_bearer(captured)
                if token:
                    return token
        except Exception:
            pass

        # --- Strategy 2: Performance logs (CDP Network events) ---
        token = _check_performance_logs(driver)
        if token:
            return token

        # --- Strategy 3: localStorage ---
        try:
            token = _scan_storage(driver, "localStorage")
            if token:
                return token
        except Exception:
            pass

        # --- Strategy 4: sessionStorage ---
        try:
            token = _scan_storage(driver, "sessionStorage")
            if token:
                return token
        except Exception:
            pass

        # --- Strategy 5: Cookies (including HttpOnly via CDP) ---
        try:
            token = _check_cookies(driver)
            if token:
                return token
        except Exception:
            pass

        # --- Strategy 6: IndexedDB (common SPA storage) ---
        try:
            token = _check_indexed_db(driver)
            if token:
                return token
        except Exception:
            pass

        # --- Strategy 7: Trigger an API call to force token capture ---
        # After login, force a fetch through the browser's auth context.
        # Our interceptor (injected via addScriptToEvaluateOnNewDocument)
        # should see the Authorization header on this call.
        if logged_in and poll_count % 3 == 0:
            try:
                driver.execute_script("""
                    fetch('https://api.spond.com/club/v1/clubs',
                          {credentials: 'include'})
                        .then(function(r) {
                            window.__spond_api_status = r.status;
                        })
                        .catch(function() {});
                """)
            except Exception:
                pass

        # Print progress every ~10 seconds
        if poll_count % 5 == 0:
            elapsed = int(time.time() - start)
            print(f"  Still waiting... ({elapsed}s elapsed)", flush=True)

    return ""


def _extract_bearer(value: str) -> str:
    """Extract a token from a value, stripping any 'Bearer ' prefix."""
    if not value or not isinstance(value, str):
        return ""
    if value.lower().startswith("bearer "):
        value = value[7:]
    value = value.strip()
    # Accept both base64-encoded JWTs (ZXlK...) and raw JWTs (eyJ...)
    if (value.startswith("eyJ") or value.startswith("ZXlK")) and len(value) > 50:
        return value
    return ""


def _check_cookies(driver) -> str:
    """
    Scan browser cookies for JWT tokens.
    Uses both Selenium cookies and CDP (which includes HttpOnly cookies).
    """
    # Selenium cookies (non-HttpOnly only)
    try:
        for cookie in driver.get_cookies():
            value = cookie.get("value", "")
            token = _extract_jwt_from_value(value)
            if token:
                return token
    except Exception:
        pass

    # CDP cookies (includes HttpOnly)
    try:
        result = driver.execute_cdp_cmd("Network.getAllCookies", {})
        for cookie in result.get("cookies", []):
            value = cookie.get("value", "")
            token = _extract_jwt_from_value(value)
            if token:
                return token
    except Exception:
        pass

    return ""


def _check_indexed_db(driver) -> str:
    """
    Scan IndexedDB databases for JWT tokens.
    Uses async JS via execute_async_script.
    """
    js = """
    var callback = arguments[arguments.length - 1];
    try {
        if (!window.indexedDB || !indexedDB.databases) {
            callback('');
            return;
        }
        indexedDB.databases().then(function(dbs) {
            var found = '';
            var checked = 0;
            if (dbs.length === 0) { callback(''); return; }
            dbs.forEach(function(dbInfo) {
                var req = indexedDB.open(dbInfo.name);
                req.onsuccess = function(e) {
                    var db = e.target.result;
                    var storeNames = Array.from(db.objectStoreNames);
                    if (storeNames.length === 0) {
                        checked++;
                        if (checked >= dbs.length) callback(found);
                        db.close();
                        return;
                    }
                    try {
                        var tx = db.transaction(storeNames, 'readonly');
                        var storesChecked = 0;
                        storeNames.forEach(function(storeName) {
                            var store = tx.objectStore(storeName);
                            var getAll = store.getAll();
                            getAll.onsuccess = function() {
                                var values = getAll.result || [];
                                values.forEach(function(val) {
                                    var str = (typeof val === 'string')
                                        ? val
                                        : JSON.stringify(val);
                                    var match = str.match(/eyJ[A-Za-z0-9_-]{50,}/);
                                    if (match && !found) found = match[0];
                                });
                                storesChecked++;
                                if (storesChecked >= storeNames.length) {
                                    checked++;
                                    if (checked >= dbs.length) callback(found);
                                    db.close();
                                }
                            };
                            getAll.onerror = function() {
                                storesChecked++;
                                if (storesChecked >= storeNames.length) {
                                    checked++;
                                    if (checked >= dbs.length) callback(found);
                                    db.close();
                                }
                            };
                        });
                    } catch(ex) {
                        checked++;
                        if (checked >= dbs.length) callback(found);
                        db.close();
                    }
                };
                req.onerror = function() {
                    checked++;
                    if (checked >= dbs.length) callback(found);
                };
            });
        }).catch(function() { callback(''); });
    } catch(e) { callback(''); }
    """
    try:
        # Set a script timeout for async execution
        driver.set_script_timeout(10)
        result = driver.execute_async_script(js)
        if result and isinstance(result, str) and result.startswith("eyJ"):
            return result
    except Exception:
        pass
    return ""


def _check_performance_logs(driver) -> str:
    """
    Scan browser performance logs for Authorization headers in network
    requests to api.spond.com.
    """
    try:
        logs = driver.get_log("performance")
    except Exception:
        return ""

    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
            if message.get("method") != "Network.requestWillBeSent":
                continue
            params = message.get("params", {})
            request = params.get("request", {})
            url = request.get("url", "")
            if "api.spond.com" not in url:
                continue
            headers = request.get("headers", {})
            # Headers may be keyed as "Authorization" or "authorization"
            for key, value in headers.items():
                if key.lower() == "authorization" and value.lower().startswith("bearer "):
                    return value[7:].strip()
        except Exception:
            continue

    return ""


def _scan_storage(driver, storage_type: str) -> str:
    """
    Scan localStorage or sessionStorage for JWT-like tokens.

    Args:
        driver: Selenium WebDriver instance
        storage_type: 'localStorage' or 'sessionStorage'

    Returns:
        str: JWT token if found, empty string otherwise
    """
    items = driver.execute_script(
        f"var items = {{}}; "
        f"for (var i = 0; i < {storage_type}.length; i++) {{ "
        f"  var key = {storage_type}.key(i); "
        f"  items[key] = {storage_type}.getItem(key); "
        f"}} "
        f"return items;"
    )

    # Check known Spond token keys first
    for priority_key in ("user-token", "token", "authToken", "bearerToken"):
        if priority_key in items:
            token = _extract_jwt_from_value(items[priority_key])
            if token:
                return token

    # Then check all other keys
    for key, value in items.items():
        token = _extract_jwt_from_value(value)
        if token:
            return token

    return ""


def _extract_jwt_from_value(value: str) -> str:
    """
    Check if a value contains a Spond auth token, handling:
    - Raw JWTs: eyJhbGci...
    - Base64-encoded JWTs: ZXlK... (Spond stores tokens this way and the
      API expects them in this base64 form)
    - JSON-wrapped strings: "ZXlK..." or "eyJ..."
    - JSON objects with token fields

    Args:
        value: The value to check

    Returns:
        str: The token if found, empty string otherwise
    """
    import base64

    if not value or not isinstance(value, str):
        return ""

    # Strip JSON string quotes if present
    stripped = value
    if stripped.startswith('"') and stripped.endswith('"'):
        try:
            stripped = json.loads(stripped)
        except Exception:
            stripped = stripped[1:-1]

    # Base64-encoded JWT: ZXlK is base64 of "eyJ"
    # Spond's API expects the token in this base64 form, so return as-is
    if isinstance(stripped, str) and stripped.startswith("ZXlK") and len(stripped) > 50:
        try:
            padded = stripped + "=" * (-len(stripped) % 4)
            decoded = base64.b64decode(padded).decode("utf-8")
            if decoded.startswith("eyJ") and "." in decoded:
                return stripped  # Return the base64 form, not decoded
        except Exception:
            pass

    # Direct JWT (eyJ...)
    if isinstance(stripped, str) and stripped.startswith("eyJ") and len(stripped) > 50:
        return stripped

    # JSON object with known token fields
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            for key in ("token", "loginToken", "authToken", "bearerToken",
                        "jwt", "access_token", "user-token"):
                val = parsed.get(key)
                if isinstance(val, str):
                    result = _extract_jwt_from_value(val)
                    if result:
                        return result
        elif isinstance(parsed, str):
            return _extract_jwt_from_value(parsed)
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    return ""


def _extract_token_manual() -> str:
    """
    Guide the user through manually extracting the bearer token from
    their browser.

    Returns:
        str: Bearer token entered by the user

    Raises:
        RuntimeError: If no token is provided
    """
    print("\nTo get your Spond bearer token:")
    print("  1. Open https://club.spond.com/ in your browser and log in")
    print("  2. Open Developer Tools (F12)")
    print("  3. Go to the Network tab")
    print("  4. Refresh the page")
    print("  5. Click any request to api.spond.com")
    print("  6. Find the 'Authorization' header — copy the value after 'Bearer '")
    print()
    print("  Alternatively: Application tab > Local Storage > spond.com")
    print("  Look for a long token starting with 'eyJ...'")
    print()

    webbrowser.open(SPOND_LOGIN_URL)
    print("A browser window has been opened to the Spond login page.")
    print()

    token = input("Paste your bearer token here: ").strip()
    # Strip "Bearer " prefix if user copied the full header value
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token:
        raise RuntimeError("No token provided")

    return token


def get_token_from_browser(force_private: bool = False) -> str:
    """
    Get a bearer token by opening a browser for the user to log in.

    Tries selenium for automated extraction first, using the existing
    browser profile by default (so you may already be logged in).
    Falls back to manual instructions if selenium is not installed.

    Args:
        force_private: If True, use InPrivate/Incognito mode from the start

    Returns:
        str: Bearer token

    Raises:
        RuntimeError: If token extraction fails
    """
    try:
        import selenium  # noqa: F401
        print("Opening browser for Spond login...")
        return _extract_token_selenium(force_private=force_private)
    except ImportError:
        print("Note: Install 'selenium' and 'webdriver-manager' for")
        print("      automated token extraction.")
        print()
        return _extract_token_manual()
    except RuntimeError as e:
        print(f"\nAutomated browser login failed: {e}")
        print("Falling back to manual token entry.\n")
        return _extract_token_manual()
    except Exception as e:
        print(f"\nBrowser error: {e}")
        print("Falling back to manual token entry.\n")
        return _extract_token_manual()
