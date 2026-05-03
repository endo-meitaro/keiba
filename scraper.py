from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


def get_all_race_data(date, progress_callback=None):

    url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={date}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

    race_ids = set()

    for el in driver.find_elements(By.XPATH, '//a[contains(@href, "race_id=")]'):
        href = el.get_attribute("href")
        if href:
            m = re.search(r"race_id=(\d+)", href)
            if m:
                race_ids.add(m.group(1))

    race_ids = sorted(list(race_ids))

    all_data = []

    total = len(race_ids)

    for idx, rid in enumerate(race_ids):

        if progress_callback:
            progress_callback(idx + 1, total, rid)

        # =====================
        # 出馬表
        # =====================
        driver.get(f"https://race.netkeiba.com/race/shutuba.html?race_id={rid}")
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "HorseName")))

        horses = driver.find_elements(By.CLASS_NAME, "HorseName")
        jockeys = driver.find_elements(By.CLASS_NAME, "Jockey")
        weights = driver.find_elements(By.CLASS_NAME, "Weight")

        horse_names = [h.text.strip() for h in horses]
        jockey_names = [j.text.strip() for j in jockeys]
        weight_list = [w.text.strip() for w in weights]

        # =====================
        # オッズ
        # =====================
        driver.get(f"https://race.netkeiba.com/odds/index.html?race_id={rid}")
        time.sleep(2)

        odds_elements = driver.find_elements(By.XPATH, "//td[contains(@class,'Odds')]")

        odds_list = []
        for o in odds_elements:
            txt = o.text.strip()

            # 🔥 ヘッダー除外
            if not txt or "オッズ" in txt or "単勝" in txt:
                continue

            try:
                odds_list.append(float(txt))
            except:
                continue

        count = min(len(horse_names), len(jockey_names), len(weight_list))

        for i in range(count):

            all_data.append({
                "race_id": rid,
                "umaban": i + 1,
                "horse": horse_names[i],
                "jockey": jockey_names[i],
                "weight": weight_list[i],
                "odds": odds_list[i] if i < len(odds_list) else 50.0
            })

        time.sleep(0.3)

    driver.quit()
    return all_data