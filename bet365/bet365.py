from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from time import sleep, localtime, strftime, strptime, mktime
import logging
import traceback
from lxml import html
from lxml.html.clean import Cleaner


conf_browser = "chrome --headless"
# conf_browser = "chrome"

main_site = "https://www.36597.com"
bet_url = "https://www.36597.com/hg_sports"
member_url = "https://www.36597.com/member-center"

valid_sites = [main_site, ]

games = []
windows = []

driver = None

def get_webdriver():
    if conf_browser == "ie":
        logging.info("initializing IE browser...")
        driver = webdriver.Ie()
    elif conf_browser == "firefox":
        logging.info("initializing Firefox browser...")
        driver = webdriver.Firefox()
    elif conf_browser == "chrome":
        logging.info("initializing Google Chrome browser...")
        driver = webdriver.Chrome()
    elif conf_browser == "chrome --headless":
        logging.info("initializing Google Chrome browser in headless mode...")
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument("disable-gpu")
        option.add_argument("log-level=3")
        driver = webdriver.Chrome(chrome_options=option)
    
    driver.implicitly_wait(40)
    logging.info("initialization of browser has done.")
    return driver

def retrieve_and_switch_window(driver):
    for win in driver.window_handles:
        if win not in windows:
            logging.debug("found new window.")
            driver.switch_to.window(win)
            f = False
            for site in valid_sites:
                if driver.current_url.find(site) >= 0:
                    f = True
                    break
            if not f:
                logging.debug("unknown window, close it.")
                driver.close()
            else:
                windows.append(win)
                logging.debug("register window to list, there are %d windows registered." % (len(windows)))
    if len(windows) >= 1:
        driver.switch_to.window(windows[-1])

def close_current_window(driver):
    for win in windows:
        if win == driver.current_window_handle:
            logging.debug("close the current window.")
            driver.close()
            windows.remove(win)
            logging.debug("remove window from list, there are %d windows registered." % (len(windows)))
    if len(windows) >= 1:
        driver.switch_to.window(windows[-1])

def close_other_windows(driver):
    logging.debug("checking windows list...")
    tmp = []
    for win in driver.window_handles:
        tmp.append(win)
    
    for win in tmp:
        if win not in windows:
            logging.debug("window %s not registered." % win)
            windows.append(win)
    for win in windows:
        if win not in tmp:
            logging.debug("window %s not existed." % win)
            windows.remove(win)
    
    logging.debug("close all windows except the first one.")
    for idx in range(len(windows) - 1, 0, -1):
        driver.switch_to.window(windows[idx])
        driver.close()
        windows.remove(windows[idx])
    driver.switch_to.window(windows[0])

def remove_float():
    ec = 0
    while ec < 3:
        try:
            ems = driver.find_elements_by_xpath("//*[contains(normalize-space(@style), 'position: absolute')]")
            for em in ems:
                driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", em)
            
            ems = driver.find_elements_by_class_name("popMiddle")
            for em in ems:
                driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", em)

            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
def open_main_page():
    logging.info("opening the main page.")
    
    ec = 0
    while ec < 3:
        try:
            driver.get(main_site)
            sleep(3)
            
            remove_float()
            
            windows.clear()
            windows.append(driver.current_window_handle)
            
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)

def login(account_name, account_pass):
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(main_site) < 0:
                open_main_page(driver)
            
            logging.info("logging into the site...")
            
            driver.switch_to.default_content()
            
            cem = driver.find_element_by_id("username")
            ActionChains(driver).move_to_element(cem).click().perform()
            ActionChains(driver).send_keys(account_name).perform()
            
            cem = driver.find_element_by_id("password")
            ActionChains(driver).move_to_element(cem).click().perform()
            ActionChains(driver).send_keys(account_pass).perform()
            
            em = driver.find_element_by_id("ibtnLogin")
            ActionChains(driver).move_to_element(em).click().perform()
            sleep(3)
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            navigate_to_game_list()
        
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)

def logout():
    ec = 0
    while ec < 3:
        try:
            driver.switch_to.default_content()
            ems = driver.find_elements_by_link_text("退出登录")
            if len(ems) > 0:
                ActionChains(driver).move_to_element(ems[0]).click().perform()
                sleep(3)
                
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
def check_login(account_name):
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(main_site) < 0:
                open_main_page(driver)
            else:
                driver.refresh()
                remove_float()
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            driver.switch_to.default_content()
            
            while True:
                ems = driver.find_elements_by_id("headtop")
                if len(ems) == 0:
                    open_main_page()
                else:
                    break
            
            em = driver.find_element_by_id("headtop")
            txtblock = em.get_attribute("innerHTML")
            p1 = txtblock.find("您好,")
            if p1 < 0:
                return {"result": False}
            else:
                p2 = txtblock.find(" 余额：￥", p1 + 3)
                current_name = txtblock[p1 + 3:p2]
                if current_name != account_name:
                    logout()
                    return {"result": False}
                else:
                    p3 = txtblock.find("</div", p2 + 5)
                    return {"result": True, "balance": float(txtblock[p2 + 5:p3])}
            
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
def navigate_to_game_list():
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(main_site) < 0:
                open_main_page()
            
            logging.info("jumping to the football games list...")
            
            driver.switch_to.default_content()
            
            cem = driver.find_element_by_link_text("体育投注")
            ActionChains(driver).move_to_element(cem).click().perform()
            sleep(2)
            
            cem = driver.find_element_by_xpath("//ul[@class='sports-list']//span[text()='皇冠体育']")
            ActionChains(driver).move_to_element(cem).click().perform()
            sleep(2)
            
            remove_float()
            
            driver.switch_to.frame("spshowFrame")
            driver.switch_to.frame("header")
            
            cem = driver.find_element_by_id("rbyshow")
            ActionChains(driver).move_to_element(cem).click().perform()
        
            driver.switch_to.parent_frame()
            driver.switch_to.frame("showFrame")
            
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)

def navigate_to_bill_list():
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(main_site) < 0:
                open_main_page(driver)
            
            logging.info("jumping to the bill list...")
            
            remove_float()
            
            driver.switch_to.default_content()
            
            cem = driver.find_element_by_id("headtop")
            em = cem.find_element_by_link_text("会员中心")
            ActionChains(driver).move_to_element(em).click().perform()
            sleep(2)
            
            em = driver.find_element_by_xpath("//div[@id='layout-top-area']/ul/li[5]/a")
            ActionChains(driver).move_to_element(em).click().perform()
            sleep(2)
            
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
def query_bet_result(team_home, team_away, bet_date):
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(member_url) < 0:
                navigate_to_bill_list()
            
            em = driver.find_element_by_xpath("//div[@id='layout-top-area']/ul/li[5]/a")
            ActionChains(driver).move_to_element(em).click().perform()
            
            selem = Select(driver.find_element_by_xpath("//div[@id='main-container']//form//select[1]"))
            selem.select_by_value("ST")
            
            em = driver.find_element_by_xpath("//div[@id='main-container']//form//input[@name='startTime']")
            ActionChains(driver).move_to_element(em).click().perform()
            ActionChains(driver).send_keys(Keys.CONTROL + 'a').perform()
            ActionChains(driver).send_keys(Keys.CONTROL).perform()
            ActionChains(driver).send_keys(strftime("%Y-%m-%d 0:00:00", localtime(mktime(strptime(bet_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")) - 86400))).perform()
            sleep(1)
            
            em = driver.find_element_by_xpath("//div[@id='main-container']//form//input[@name='endTime']")
            ActionChains(driver).move_to_element(em).click().perform()
            ActionChains(driver).send_keys(Keys.CONTROL + 'a').perform()
            ActionChains(driver).send_keys(Keys.CONTROL).perform()
            ActionChains(driver).send_keys(bet_date + " 23:59:59").perform()
            sleep(1)
            
            em = driver.find_element_by_xpath("//div[@id='main-container']//form//button")
            ActionChains(driver).move_to_element(em).click().perform()
            sleep(2)
            
            doc = html.fromstring(driver.find_element_by_xpath("//div[@id='main-container']").get_attribute("innerHTML"))
            lis = doc.xpath("//ul[@class='list-group']/li")
            for li in lis:
                cell = li.xpath("./div")
                detail_txt = cell[4].text_content()
                if detail_txt.find(team_home) >= 0 and detail_txt.find(team_away) >= 0:
                    result = cell[5].text_content().strip()
                    money = cell[-1].text_content().strip()
                    
                    logging.info("querying bet result, result: %s, money: %s" % (result, money))
                    
                    if result == "系统未接受":
                        return {"result": True, "msg": "系统未接受，投注失败"}
                    elif result == "未结算":
                        return {"result": False, "msg": "投注结果尚未公布"}
                    elif result == "正在确认":
                        return {"result": True, "msg": "正在确认，请稍后查询"}
                    
                    win = 0
                    half = 0
                    
                    if result in ("赢", "赢一半"):
                        win = 1
                        if result == "赢一半":
                            half = 1
                    elif result in ("输", "输一半"):
                        win = -1
                        if result == "输一半":
                            half = 1
                    
                    return {"result": True, "win": win, "half": half, "money": float(money)}
            
            break
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
    return {"error": "指定的投注记录未能找到"}

def detect_handicap(elem):
    handicap, odds, team = None, None, None
    
    span = elem.xpath("./span")
    if len(span) != 0:
        handicap = span[0].text_content().strip()

    a = elem.xpath("./a/@title")
    if len(a) != 0:
        team = a[0]
    
    font = elem.xpath("./a/font")
    if len(font) != 0:
        odds = font[0].text_content().strip()
    
    if team != None and odds != None:
        return {"team": team, "handicap": handicap, "odds": odds}
    else:
        return None

def detect_handicap_alt(elem):
    return detect_handicap(html.fromstring("<td>" + elem.get_attribute("innerHTML") + "</td>"))

def find_game(team_home, team_away, handicap):
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(bet_url) < 0:
                navigate_to_game_list()
            
            game_exists = False
            
            handicaps = []
            handicaps_bak1, handicaps_bak2 = [], []
            found = False
            
            driver.switch_to.default_content()
            driver.switch_to.frame("spshowFrame")
            driver.switch_to.frame("header")
            
            cem = driver.find_element_by_id("rb_btn")
            if cem.get_attribute("class").find("rb_on") < 0:
                ActionChains(driver).move_to_element(cem).click().perform()
                sleep(2)
            
            driver.switch_to.parent_frame()
            driver.switch_to.frame("showFrame")
            
            rems = driver.find_elements_by_class_name("refresh")
            for em in rems:
                driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", em)
            
            tbl = driver.find_elements_by_xpath("//table[@id='data']")
            
            doc = html.fromstring(tbl[0].get_attribute("innerHTML"))
            tem = doc.xpath("//tbody/tr")
            i = 1
            while i < len(tem):
                lem1 = tem[i]
                cem1 = lem1.xpath("./td")
                
                i += 1
                
                if len(cem1) == 1:
                    continue
                
                lem2 = tem[i]
                cem2 = lem2.xpath("./td")
                
                if cem1[1].text_content().find(team_home) >= 0 and cem1[1].text_content().find(team_away) >= 0:
                    game_exists = True
                    
                    handicap1 = detect_handicap(cem1[3])
                    handicap2 = detect_handicap(cem2[1])
                    
                    if handicap1 != None and handicap2 != None:
                        if handicap1["team"].startswith(team_home) and handicap2["team"].startswith(team_away):
                            if handicap1["handicap"] != None:
                                handicap_no = handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = -handicap_to_number(handicap2["handicap"])
                            odds_home = handicap1["odds"]
                            odds_away = handicap2["odds"]
                            r_team_home = handicap1["team"]
                            r_team_away = handicap2["team"]
                        else:
                            if handicap1["handicap"] != None:
                                handicap_no = -handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = handicap_to_number(handicap2["handicap"])
                            odds_home = handicap2["odds"]
                            odds_away = handicap1["odds"]
                            r_team_home = handicap2["team"]
                            r_team_away = handicap1["team"]
                        
                        if handicap == None or handicap_no == handicap:
                            found = True
                            if handicap_no != None:
                                dv = cem1[0].xpath("./div[@class='bf']")
                                if len(dv) > 0:
                                    txt = dv[0].text.strip()
                                    sp = dv[0].xpath("./span")
                                    bf = sp[0].text.strip()
                                
                                handicaps.append({"handicap": handicap_no, "odds_home": odds_home, "odds_away": odds_away, "team_home": r_team_home, "team_away": r_team_away, "score": bf, "time": txt})
                                if handicap_no == handicap:
                                    break
                elif cem1[1].text_content().find(team_home) >= 0:
                    handicap1 = detect_handicap(cem1[3])
                    handicap2 = detect_handicap(cem2[1])
                    
                    if handicap1 != None and handicap2 != None:
                        if handicap1["team"].startswith(team_home):
                            if handicap1["handicap"] != None:
                                handicap_no = handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = -handicap_to_number(handicap2["handicap"])
                            odds_home = handicap1["odds"]
                            odds_away = handicap2["odds"]
                            r_team_home = handicap1["team"]
                            r_team_away = handicap2["team"]
                            
                            if handicap == None or handicap_no == handicap:
                                if handicap_no != None:
                                    dv = cem1[0].xpath("./div[@class='bf']")
                                    if len(dv) > 0:
                                        txt = dv[0].text.strip()
                                        sp = dv[0].xpath("./span")
                                        bf = sp[0].text.strip()
                                    
                                    handicaps_bak1.append({"handicap": handicap_no, "odds_home": odds_home, "odds_away": odds_away, "team_home": r_team_home, "team_away": r_team_away, "score": bf, "time": txt})
                elif cem1[1].text_content().find(team_away) >= 0:
                    handicap1 = detect_handicap(cem1[3])
                    handicap2 = detect_handicap(cem2[1])
                    
                    if handicap1 != None and handicap2 != None:
                        if handicap2["team"].startswith(team_away):
                            if handicap1["handicap"] != None:
                                handicap_no = handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = -handicap_to_number(handicap2["handicap"])
                            odds_home = handicap1["odds"]
                            odds_away = handicap2["odds"]
                            r_team_home = handicap1["team"]
                            r_team_away = handicap2["team"]
                            
                            if handicap == None or handicap_no == handicap:
                                if handicap_no != None:
                                    dv = cem1[0].xpath("./div[@class='bf']")
                                    if len(dv) > 0:
                                        txt = dv[0].text.strip()
                                        sp = dv[0].xpath("./span")
                                        bf = sp[0].text.strip()
                                    
                                    handicaps_bak2.append({"handicap": handicap_no, "odds_home": odds_home, "odds_away": odds_away, "team_home": r_team_home, "team_away": r_team_away, "score": bf, "time": txt})
                
                i += 3
            
            if found:
                return {"result": True, "handicaps": handicaps}
            else:
                if len(handicaps_bak1) > 0:
                    return {"result": True, "handicaps": handicaps_bak1}
                elif len(handicaps_bak2) > 0:
                    return {"result": True, "handicaps": handicaps_bak2}
                
                pg = driver.find_elements_by_id("pg_txt")
                if len(pg) > 0:
                    if pg[0].get_attribute("innerHTML").find("下一页") < 0:
                        if handicap == None and game_exists:
                            return {"result": True, "handicaps": []}
                        else:
                            return {"result": False, "msg": "未找到对应的比赛"}
                    else:
                        em = pg[0].find_element_by_link_text("下一页")
                        ActionChains(driver).move_to_element(em).click().perform()
                        sleep(1)
                else:
                    if handicap == None and game_exists:
                        return {"result": True, "handicaps": []}
                    else:
                        return {"result": False, "msg": "未找到对应的比赛"}
        
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
        
    return {"error": "查找比赛失败，请重试"}

def bet_game(team_home, team_away, handicap, team, money):
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(bet_url) < 0:
                navigate_to_game_list()
            
            driver.switch_to.default_content()
            driver.switch_to.frame("spshowFrame")
            driver.switch_to.frame("header")
            
            cem = driver.find_element_by_id("rb_btn")
            if cem.get_attribute("class").find("rb_on") < 0:
                ActionChains(driver).move_to_element(cem).click().perform()
                sleep(2)
            
            driver.switch_to.parent_frame()
            driver.switch_to.frame("showFrame")
            
            rems = driver.find_elements_by_class_name("refresh")
            for em in rems:
                driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", em)
            
            tem = driver.find_elements_by_xpath("//table[@id='data']/tbody/tr")
            i = 1
            while i < len(tem):
                lem1 = tem[i]
                driver.execute_script("arguments[0].scrollIntoView();", lem1)
                cem1 = lem1.find_elements_by_tag_name("td")
                
                i += 1
                
                if len(cem1) == 1:
                    continue
                
                lem2 = tem[i]
                driver.execute_script("arguments[0].scrollIntoView();", lem2)
                cem2 = lem2.find_elements_by_tag_name("td")
                
                if cem1[1].text.find(team_home) >= 0 and cem1[1].text.find(team_away) >= 0:
                    handicap1 = detect_handicap_alt(cem1[3])
                    handicap2 = detect_handicap_alt(cem2[1])
                    
                    if handicap1 != None and handicap2 != None:
                        if handicap1["team"].startswith(team_home) and handicap2["team"].startswith(team_away):
                            if handicap1["handicap"] != None:
                                handicap_no = handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = -handicap_to_number(handicap2["handicap"])
                            odds_home = handicap1["odds"]
                            odds_away = handicap2["odds"]
                        else:
                            if handicap1["handicap"] != None:
                                handicap_no = -handicap_to_number(handicap1["handicap"])
                            else:
                                handicap_no = handicap_to_number(handicap2["handicap"])
                            odds_home = handicap2["odds"]
                            odds_away = handicap1["odds"]
                        
                        if handicap_no == handicap:
                            bfdoc = html.fromstring(cem1[0].get_attribute("innerHTML"))
                            bf = bfdoc.xpath("//div[@class='bf']//span")
                            
                            target_link = None
                            if (handicap1["team"].startswith(team_home) and team == "home") or (handicap1["team"].startswith(team_away) and team == "away"):
                                target_link = cem1[3].find_element_by_tag_name("a")
                            else:
                                target_link = cem2[1].find_element_by_tag_name("a")
                            
                            driver.execute_script("arguments[0].scrollIntoView();", target_link)
                            ActionChains(driver).move_to_element(target_link).click().perform()
                            
                            driver.switch_to.parent_frame()
                            driver.switch_to.frame("orderFrame")
                            driver.switch_to.frame("orderFrame")
                            sleep(2)
                            
                            em = driver.find_element_by_name("gold")
                            ActionChains(driver).move_to_element(em).send_keys(str(money)).perform()
                            em = driver.find_element_by_id("ordersubmit")
                            ActionChains(driver).move_to_element(em).click().perform()
                            sleep(2)
                            
                            driver.switch_to_alert().accept()
                            
                            try:
                                driver.switch_to.default_content()
                                sleep(3)
                            except:
                                pass
                            
                            try:
                                alert_text = driver.switch_to_alert().text
                                if alert_text.find("失败") >= 0 or alert_text.find("限额") >= 0:
                                    driver.switch_to_alert().accept()
                                    return {"result": False, "message": alert_text}
                                else:
                                    driver.switch_to_alert().accept()
                            except:
                                pass
                            
                            driver.switch_to.default_content()
                            driver.switch_to.frame("spshowFrame")
                            driver.switch_to.frame("orderFrame")
                            driver.switch_to.frame("orderFrame")

                            if len(driver.find_elements_by_name("gold")) > 0:
                                logging.error("submit error, input box still exists.")
                                raise Exception("input box still exists")
                            
                            return {"result": True, "odds_home": odds_home, "odds_away": odds_away}
                    
                i += 3
            
            pg = driver.find_elements_by_id("pg_txt")
            if len(pg) > 0:
                if pg[0].get_attribute("innerHTML").find("下一页") < 0:
                    return {"result": False, "msg": "未找到对应的比赛"}
                else:
                    em = pg[0].find_element_by_link_text("下一页")
                    ActionChains(driver).move_to_element(em).click().perform()
                    sleep(1)
            else:
                return {"result": False, "msg": "未找到对应的比赛"}
        
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
    
    return {"result": False}


def handicap_to_number(handicap):
    num = 0
    
    handicap = handicap.strip()
    
    p = handicap.find("/")
    if p >= 0:
        num += 0.25
        handicap = handicap[:p].strip()
    
    try:
        num += float(handicap)
    except:
        pass
    
    return num


def team_strip(team):
    if team == None:
        return team
    team = team.strip()
    p = team.find("-")
    if p >= 0:
        team = team[0:p].strip()
    return team

def list_all_games():
    ec = 0
    while ec < 3:
        try:
            if driver.current_url.find(bet_url) < 0:
                navigate_to_game_list()
            
            games_collect = {}
            
            driver.switch_to.default_content()
            driver.switch_to.frame("spshowFrame")
            driver.switch_to.frame("header")
            
            cem = driver.find_element_by_id("rb_btn")
            if cem.get_attribute("class").find("rb_on") < 0:
                ActionChains(driver).move_to_element(cem).click().perform()
                sleep(2)
            
            driver.switch_to.parent_frame()
            driver.switch_to.frame("showFrame")
            
            rems = driver.find_elements_by_class_name("refresh")
            for em in rems:
                driver.execute_script("arguments[0].parentNode.removeChild(arguments[0])", em)
            
            tbl = driver.find_elements_by_xpath("//table[@id='data']")
            
            cleaner = Cleaner(kill_tags=["span", "br"])
            
            doc = html.fromstring(tbl[0].get_attribute("innerHTML"))
            tem = doc.xpath("//tbody/tr")
            i = 1
            while i < len(tem):
                lem1 = tem[i]
                cem1 = lem1.xpath("./td")
                
                i += 1
                
                if len(cem1) == 1:
                    continue
                
                lem2 = tem[i]
                cem2 = lem2.xpath("./td")
                
                team_text = html.fromstring(cleaner.clean_html(html.tostring(cem1[1]).decode("utf-8"))).text_content()
                team_arr = team_text.split("\n")
                team_home = team_strip(team_arr[1])
                team_away = team_strip(team_arr[2])
                
                games_collect[team_home + team_away] = {"team_home": team_home, "team_away": team_away}
                
                i += 3
            
            games = []
            for key in games_collect:
                games.append(games_collect[key])
            
            return {"result": True, "games": games}
        
        except UnexpectedAlertPresentException:
            logging.error(traceback.format_exc())
            
            try:
                driver.switch_to_alert().accept()
            except:
                pass
            
            ec += 1
        except:
            logging.error(traceback.format_exc())
            
            ec += 1
            
            driver.refresh()
            remove_float()
            
            sleep(2)
        
    return {"error": "查找比赛失败，请重试"}


def init():
    global driver
    
    driver = get_webdriver()
    
    # driver.maximize_window()
    
    open_main_page()

def close():
    driver.quit()

