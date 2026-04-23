from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://urjo.com/")
        
        # Click the first challenge
        links = page.locator("a[href^='/']").all()
        for link in links:
            text = link.text_content()
            if text and ("Anon" in text or "/" in text):
                link.click()
                break
        
        page.wait_for_timeout(2000)
        
        # Get all elements that look like cells. 
        # Usually they are inside a container. Let's get the page HTML and search for 'button' or similar.
        html = page.content()
        
        # Print a snippet of the body content
        body = page.locator("body").inner_html()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(body)
            
        print("Dumped body to page_dump.html")
        browser.close()

if __name__ == "__main__":
    run()
