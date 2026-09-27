import os
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_EXEC = "/Users/apple/Library/Caches/ms-playwright/chromium-1234/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
FFMPEG_EXEC = "/Users/apple/Library/Caches/ms-playwright/ffmpeg-1011/ffmpeg-mac"
OUTPUT_DIR = Path("/Users/apple/.gemini/antigravity-ide/scratch/permission-aware-rag/recordings")
ARTIFACT_DIR = Path("/Users/apple/.gemini/antigravity-ide/brain/c6e83f86-2b98-48f9-a3ee-2744e734a434")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("[1/5] Starting Playwright browser session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_EXEC,
            headless=True
        )
        context = browser.new_context(
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 800},
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print("[2/5] Navigating to http://localhost:8000/...")
        page.goto("http://localhost:8000/", wait_until="networkidle")
        time.sleep(2)
        
        # 1. System Architecture Modal
        print("[3/5] Demonstrating Architecture Modal...")
        arch_btn = page.locator("button:has-text('System Architecture')")
        if arch_btn.count() > 0:
            arch_btn.click()
            time.sleep(3)
            # Close button
            close_btn = page.locator("button:has-text('Close')")
            if close_btn.count() > 0:
                close_btn.click()
            time.sleep(1)
            
        # 2. Documents Tab
        print("[4/5] Touring Documents & Permissions Tab...")
        docs_tab = page.locator("button:has-text('Documents & Permissions')")
        if docs_tab.count() > 0:
            docs_tab.click()
            time.sleep(2)
            page.mouse.wheel(0, 300)
            time.sleep(2)
            page.mouse.wheel(0, -300)
            time.sleep(1)
            
        # 3. Switch back to RAG Chat
        print("[5/5] Demonstrating Permission-Aware RAG Chat...")
        chat_tab = page.locator("button:has-text('RAG Chat')")
        if chat_tab.count() > 0:
            chat_tab.click()
            time.sleep(1)
            
        # Run Query 1 as Alice Chen (Tenant Admin)
        sample_btn = page.locator("button:has-text(\"What was Acme Corp's total revenue in Q3 2024?\")")
        if sample_btn.count() > 0:
            sample_btn.click()
            time.sleep(1)
            send_btn = page.locator("button:has-text('Send Query')")
            if send_btn.count() > 0:
                send_btn.click()
            time.sleep(4)  # Wait for grounded response
            
        # Switch Persona to Bob Smith (Employee)
        print("  -> Switching Persona to Bob Smith (Employee)...")
        persona_select = page.locator("select").first
        if persona_select.count() > 0:
            persona_select.select_option(label="Bob Smith (Acme Employee)")
            time.sleep(2)
            
        # Run Query 2 as Bob (Forbidden doc)
        input_box = page.locator("input[placeholder*='Ask a question']")
        if input_box.count() > 0:
            input_box.fill("What are the quarterly financial results for Q3?")
            time.sleep(1)
            send_btn = page.locator("button:has-text('Send Query')")
            if send_btn.count() > 0:
                send_btn.click()
            time.sleep(3)
            
        # Demonstrate Standout Feature: Mid-Flight Revocation
        print("  -> Simulating Mid-Flight Revocation Checkpoint 2...")
        revocation_chk = page.locator("input[type='checkbox']")
        if revocation_chk.count() > 0:
            revocation_chk.check(force=True)
            time.sleep(1)
            
        if input_box.count() > 0:
            input_box.fill("What are the engineering best practices and handbook guidelines?")
            time.sleep(1)
            send_btn = page.locator("button:has-text('Send Query')")
            if send_btn.count() > 0:
                send_btn.click()
            time.sleep(3)
            
        # 4. Audit Logs Tab
        print("  -> Viewing Append-Only Tamper-Evident Audit Trail...")
        audit_tab = page.locator("button:has-text('Audit Logs')")
        if audit_tab.count() > 0:
            audit_tab.click()
            time.sleep(2)
            page.mouse.wheel(0, 300)
            time.sleep(2)
            page.mouse.wheel(0, -300)
            time.sleep(2)
            
        print("Closing browser context to finalize video recording...", flush=True)
        page.close()
        context.close()
        browser.close()
        
    # Find the recorded video file
    video_files = [f for f in OUTPUT_DIR.glob("*.webm") if "demo" not in f.name]
    if video_files:
        latest_video = max(video_files, key=os.path.getmtime)
        final_video_name = "permission_aware_rag_demo.webm"
        final_video_path = OUTPUT_DIR / final_video_name
        shutil.copy(latest_video, final_video_path)
        shutil.copy(latest_video, ARTIFACT_DIR / final_video_name)
        print(f"SUCCESS: Recording saved at:\n  - {final_video_path}\n  - {ARTIFACT_DIR / final_video_name}", flush=True)
    else:
        print("No raw video file found in output dir.", flush=True)

if __name__ == "__main__":
    main()
