'''
颜色约定

引导用户选择: 白色
系统信息输出: 黄色
SUCCESS:  绿色
ERROR:    红色
  

'''


from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from prettytable import PrettyTable


import os,re
import time
import requests
import urllib3
import wasabi
from wasabi import msg
from alive_progress import alive_bar

from retrying import retry

msg.show_color=True
urllib3.disable_warnings()
def waitElementOccur(browser, XPATH, sec=10):
    return WebDriverWait(browser,sec).until(EC.presence_of_element_located((By.XPATH, XPATH)))

def waitElementClickable(browser, XPATH, sec=10):
    return WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, XPATH)))

def showCurPageMange(browser, page_cur, page_total):
    '表格展示当前页漫画'
    manga_table_cur_page = PrettyTable(field_names=['序号','漫画名', '作者'])
    manga_list_ele = browser.find_elements_by_class_name('exemptComicItem')
    for i, manga_item_ele in enumerate(manga_list_ele):
        manga_name, manga_author = manga_item_ele.text.split('\n')
        manga_author = manga_author[3:]
        manga_table_cur_page.add_row([str(i+1), manga_name, manga_author])

    log(manga_table_cur_page.get_string(title=f'''当前漫画页: {page_cur}/{page_total}'''))
    return manga_list_ele


def jumpPage(browser, page_n):
    '跳转漫画页'
    ele_to_page = waitElementOccur(browser, '//*[@id="comic"]/div[2]/ul/div/input')
    ele_to_page.clear()
    ele_to_page.send_keys(str(page_n))
    waitElementClickable(browser, '//*[@id="comic"]/div[2]/ul/li[14]/a').click()


def jumpBack(browser):
    '关闭当前窗口, 切回上一个窗口'
    browser.close()
    browser.switch_to.window(browser.window_handles[-1])

def mangaIdxParser(term):
    '解析是第几话'
    pt1 = r'\d+\.\d+'
    idx_t = re.findall(pt1, term)
    if len(idx_t)>0:
        return float(idx_t[0])
    
    try:
        return int(re.sub('\D', '', term))

    except Exception:
        pass

    return None

    
def scrollBottomToTop(browser, target_xpath):
    '''缓慢从页面底部滑动到页面顶部

    target_xpath: 目标元素,出现则跳出
    100/0.1s
    '''
    step=100
    t = 0.1
    page_height = browser.execute_script('return document.body.scrollHeight')

    # 滑倒底部
    browser.execute_script(f"window.scrollTo(0, {page_height});")
    time.sleep(2)
    while page_height>100:
    
        browser.execute_script(f"window.scrollTo(0, {page_height-step});")
        page_height-=step
        time.sleep(t)

        # 检查目标元素是否出现, 出现则立即跳出
        try:
            browser.find_element(By.XPATH, target_xpath)
            break
        except Exception:
            continue

    


def getMangaStatus(browser, key_word='話'):

    '''获取漫画状态
    
    return:
    {
        num:   数量,
        range: 范围,
        links:  连接元素
        range_name: 范围名
    }
    '''
    status = {}
    xpath_base = f'//*[@id="default{key_word}"]/ul'
    ele_item_box = browser.find_element_by_xpath(xpath_base)
    ele_item_list = ele_item_box.find_elements_by_xpath('a')
    links = []   # 卷/话链接
    ranges = []  # 卷/话范围
    ranges_name = [] # 卷/话范围对应的名字
    for i,ele in enumerate(ele_item_list):
        # 找到链接
        links.append(ele.get_attribute('href'))
        # 填充对应的话/卷/番外标题代表的数字
        vol_name = ele.get_attribute('title')

        # title中没有序号则跳过
        idx = mangaIdxParser(vol_name)
        if idx==None:
            continue

        ranges.append(idx)
        ranges_name.append(vol_name)

    status['num']   = len(ele_item_list)
    status['links'] = links
    status['range'] = ranges
    status['range_name'] = ranges_name

    return status

def cleanScreen():
    '清屏'
    os.system('cls')

def colorStr(s, fg='white', bg=None, bold=True):
    '''给字符串着色.
    s:    目标串
    fg:   前景色
    bg:   背景色
    bold: 是否加粗
    
    '''
    return wasabi.color(s, fg=fg, bg=bg, bold=bold)

def log(s, rank=None):
    '打印日志信息'

    if rank == None:
        s = colorStr(s, fg='yellow')
    print(s)


@retry(stop_max_attempt_number=10)
def downloadImg(img_src, path):
    try:
        image=requests.get(img_src, verify = False)
        with open(path,'wb') as wf:
            wf.write(image.content)
        time.sleep(5)
    except Exception as e:
        time.sleep(3)
        raise e


def Main():
    msg.info('程序初始化中,请稍后...')
    chrome_opt = Options()
    chrome_opt.add_argument('log-level=2')
    chrome_opt.add_argument('--window-size=1920,1080')
    chrome_opt.add_argument('log-level=2')
    chrome_opt.add_argument('--headless')
    chrome_opt.add_experimental_option('excludeSwitches', ['enable-logging'])


    browser = webdriver.Chrome(options=chrome_opt)
    
    browser.get(f'''https://copymanga.org''')
    
    time_cost = 3
    msg.good(f'程序初始化完成!{time_cost}秒后进入搜索页')
    while True:
        time_cost-=1
        if time_cost<0:
            break
        time.sleep(1)
        msg.good(f'\033[A程序初始化完成!{time_cost}秒后进入搜索页')

    while True:
        try:
            cleanScreen()
            manga_search_term = input('请输入要搜索的漫画名,按回车【Enter】结束:')

            # 检查检索串是否合法
            if len(manga_search_term) == 0:
                msg.warn('检索字符串不合法! 按回车返回搜索页')
                input()
                continue
            
            msg.info(f'正在检索【{manga_search_term}】,请稍后...')
            search_ele = waitElementOccur(browser, '/html/body/header/div[2]/div/div[8]/div/div/div/div/input')
            search_ele.clear()
            search_ele.send_keys(manga_search_term)
            search_ele.send_keys(Keys.ENTER)   

            # 涉及跳转，切换窗口
            browser.switch_to.window(browser.window_handles[-1])
            # waitElementClickable(browser, '//*[@id="comic"]/div[2]/ul/li[14]/a')
            browser.refresh()
            time.sleep(3)
            if waitElementOccur(browser, '/html/body/main/div[1]/div[3]/h4/span[2]').text=='0':
                msg.warn(f'未找到与搜索串【{manga_search_term}】相关的漫画,请按任意键后重新搜索!')
                input()
                jumpBack(browser)
                continue
            time_cost = 3
            msg.good(f'检索成功!{time_cost}秒后进入搜索结果页')
            while True:
                time_cost-=1
                if time_cost<0:
                    break
                time.sleep(1)
                msg.good(f'\033[A检索成功!{time_cost}秒后进入搜索结果页')
            try:
                page_total_ele = waitElementOccur(browser, '//*[@id="comic"]/div[2]/ul/li[13]')
            except Exception:
                msg.warn(f'未找到与搜索串【{manga_search_term}】相关的漫画,请按任意键后重新搜索!')
                input()
                jumpBack(browser)
                continue
            page_total = int(page_total_ele.text[1:])
            page_cur = 1
            
            # 进入检索状态
            while True:
                cleanScreen()
                ele_manga_list = showCurPageMange(browser, page_cur=page_cur, page_total=page_total)
                option = input('请选择下一步操作(按回车结束输入):\n[1]直接选择序号\n[2]跳转页\n[3]返回搜索页\n你的选择: ')
                
                if option not in '123':
                    msg.warn('输入非法!输入必须是符合要求的序号,请按任意键重新输入!')
                    input()
                    continue
                
                # 分析选项
                if option == '1':
                    '进入漫画选择状态'
                    # 选择漫画
                    while True:
                        idx_manga = input(f'''请选择漫画序号1~{len(ele_manga_list)}, 按回车【Enter】结束输入:''')
                        if not idx_manga.isdigit() or int(idx_manga) not in range(1, len(ele_manga_list)+1):
                            msg.warn('输入非法!输入的漫画序号必须在表格的序号范围内,请按任意键后重新输入!')
                            input()
                            continue
                        else:
                            break
                    
                    # 获取选择漫画的基本信息

                    msg.info('正在获取漫画信息,请稍后...')
                    manga_name, manga_author = ele_manga_list[int(idx_manga)-1].text.split('\n')
                    manga_author = manga_author[3:]

                    manga_href_xpath = f'//*[@id="comic"]/div[1]/div[{idx_manga}]/div[1]/a' 
                    waitElementClickable(browser, manga_href_xpath).click()
                    
                    # 切换到当前窗口
                    browser.switch_to.window(browser.window_handles[-1])
                    #等待所有可下载选项加载完毕


                    # 检查 话/卷/番外是否可用
                    n_try = 0
                    while True:
                        try:
                            hua_xpath = '/html/body/main/div[2]/div[3]/div[1]/div[1]/ul/li[2]/a'
                            juan_xpath = '/html/body/main/div[2]/div[3]/div[1]/div[1]/ul/li[3]/a'
                            fanwai_xpath = '/html/body/main/div[2]/div[3]/div[1]/div[1]/ul/li[4]/a'

                            hua_flag    = False if 'disabled' in browser.find_element_by_xpath(hua_xpath).get_attribute('class') else True
                            juan_flag   = False if 'disabled' in browser.find_element_by_xpath(juan_xpath).get_attribute('class') else True
                            fanwai_flag = False if 'disabled' in browser.find_element_by_xpath(fanwai_xpath).get_attribute('class') else True
                    
                            break
                        except Exception:
                            if (n_try+1) % 3==0:
                                msg.warn('加载漫画信息失败!你已尝试多次重新加载,是否继续重新加载?(输入y表示继续,其他任何输入都表示退出程序)')
                            else:
                                msg.warn('加载漫画信息失败!是否重新加载?(输入y表示继续,其他任何输入都表示退出程序)')
                            opt = input()
                            n_try+=1
                            if opt=='y':
                                msg.info('正在获取漫画信息,请稍后...')
                                browser.refresh()
                                time.sleep(3)
                                continue
                            else:
                                os.exit(0)




                    # 分析当前话/卷/番外的状态(多少卷)
                    manga_status = {}
                    if hua_flag:
                        manga_status.update({'hua':getMangaStatus(browser)})
                    if juan_flag:
                        manga_status.update({'juan':getMangaStatus(browser, key_word='卷')})
                    if fanwai_flag:
                        manga_status.update({'fanwai':getMangaStatus(browser, key_word='番外')})


                    cleanScreen()
                    log(f'当前选择漫画: 【{manga_name}】')
                    log(f'当前漫画状态:')

                    
                    data = [
                        ('1','话',str(min(manga_status['hua']['range']))+'~'+str(max(manga_status['hua']['range'])) if hua_flag else '不可用'),
                        ('2','卷',str(min(manga_status['juan']['range']))+'~'+str(max(manga_status['juan']['range'])) if juan_flag else '不可用'),
                        ('3','番外',str(min(manga_status['fanwai']['range']))+'~'+str(max(manga_status['fanwai']['range'])) if fanwai_flag else '不可用')
                    ]
                    manga_info = PrettyTable(field_names=['序号','类型', '状态'])
                    manga_info.add_rows(data)

                    log(manga_info.get_string(title=f'''当前漫画状态'''))
                    

                    # log(f'''1.[话]:\t{str(min(manga_status['hua']['range']))+'~'+str(max(manga_status['hua']['range'])) if hua_flag else '不可用'}''')
                    # log(f'''2.[卷]:\t{str(min(manga_status['juan']['range']))+'~'+str(max(manga_status['juan']['range'])) if juan_flag else '不可用'}''')
                    # log(f'''3.[番外]:\t{str(min(manga_status['fanwai']['range']))+'~'+str(max(manga_status['fanwai']['range'])) if fanwai_flag else '不可用'}''')


                    # 选择要下载的类型
                    types = ['话','卷','番外']
                    types_en = ['hua','juan','fanwai']
                    while True:
                        dl_type = input('请选择要下载的类型(话/卷/番外前的序号,请尽量不要选择按【卷】下载),按回车【Enter】结束输入, 按x返回上一层:')
                        if dl_type.lower() == 'x':
                            break
                        if not dl_type.isdigit() or int(dl_type) not in range(1,4):
                            msg.warn('输入非法!输入的序号必须在序号范围内,并且是合法的序号!请按任意键后重新输入!')
                            input()
                            continue
                        if not hua_flag and dl_type == '1' or not juan_flag and dl_type=='2' or not fanwai_flag and dl_type=='3':
                            msg.warn('输入的下载类型不可用!请按任意键后重新输入!')
                            input()
                            continue
                        dl_type = int(dl_type)-1

                        low, high = min(manga_status[types_en[dl_type]]['range']), max(manga_status[types_en[dl_type]]['range'])
                        # idx_input_legal = True   # 序号输入合法性判断
                        
                        while True:
                            dl_range = [] # 下载范围(上下限, 考虑到有.5的存在) 
                            cmd = input(f'''请选择要下载的【{types[dl_type]}】的序号, 也可输入下载的序号范围, 用'-'隔开,例如1-5. 按回车【Enter】结束输入(输入'x'返回上一层下载类型选择):\n''')
                            
                            
                            if cmd.lower() == 'x':
                                break
                            elif re.match(r'^\d+\-\d+$', cmd)!=None:
                                be = cmd.split('-')
                                if len(be)!=2 or not be[0].isdigit() or not be[1].isdigit() or int(be[0])>=int(be[1]) or int(be[0])<low or int(be[1])>high:
                                    msg.warn('请输入合法的序号范围! 请重新选择范围')
                                    continue

                                dl_range.extend([float(be[0]), float(be[1])])
                            elif cmd.isdigit():
                                idx = int(cmd)
                                if idx<low or idx>high:
                                    msg.warn('请确保序号在范围内!请重新选择范围')
                                    continue
                                dl_range.extend([idx,idx])
                            else:
                                msg.warn('请输入合法的序号! 请重新选择范围')
                                continue

                            #### 下载流程 #########
                            msg.info('开始下载...')
                            for i, manga_idx in enumerate(manga_status[types_en[dl_type]]['range']):
                                if manga_idx>=dl_range[0] and manga_idx<=dl_range[1]:
                                    manga_dir = f'./{manga_name}_{manga_idx}_{types[dl_type]}'
                                    if not os.path.exists(manga_dir):
                                        os.mkdir(manga_dir)

                                    msg.info(f'''开始下载【{manga_name}】第{manga_idx}{types[dl_type]}...''')
                                    link = manga_status[types_en[dl_type]]['links'][i]
                                    js = f'''window.open('{link}');'''
                                    browser.execute_script(js)
                                    browser.switch_to.window(browser.window_handles[-1])

                                    # 共 n_jpg 张图片
                                    n_jpg = int(waitElementOccur(browser,'/html/body/div[1]/span[2]').text)

                                    flag=True
                                    
                                    with alive_bar(n_jpg) as bar:
                                        for ct in range(n_jpg):
                                            bar()
                                            # 找下一张图片
                                            n_try=0   # 尝试次数
                                            while True:
                                                # 尝试获取图片
                                                if n_try == 50:
                                                    flag=False
                                                    break
                                                try:
                                                    target_xpath = f'/html/body/div[2]/div/ul/li[{ct+1}]'
                                                    ele_jpg = browser.find_element_by_xpath(target_xpath)
                                                    break
                                                except Exception:
                                                    scrollBottomToTop(browser, target_xpath)
                                                    n_try+=1
                                                    continue
                                                
                                            if flag==False:
                                                break
                                            
                                            img_ele = ele_jpg.find_element_by_xpath('img')
                                            data_src = img_ele.get_attribute('data-src')

                                            # 下载图片
                                            try:
                                                downloadImg(
                                                    img_src=data_src,
                                                    path=manga_dir+'/{0:0>3}.jpg'.format(ct+1)
                                                )

                                            except Exception:
                                                flag=False
                                                break
                                            
                                    if flag == False:
                                        msg.fail('下载失败...')

                                    jumpBack(browser)
                            browser.switch_to.window(browser.window_handles[-1])
                            msg.good('所有任务下载完毕!')
                            while True:
                                opt = input('请选择接下来的操作:\n[1]继续下载\n[2]返回上一层 \n[3]退出程序\n你的选择:')
                                if not opt in ["1","2","3"]:
                                    msg.warn('选项非法,请重新选择')
                                    continue
                                break
                            if opt == '1':
                                continue
                            elif opt=='2':
                                break
                            else:
                                os.exit(0)

                    jumpBack(browser)

                elif option == '2':
                    '跳页'
                    while True:
                        n_page = input(f'''请输入要跳转的页码, 范围为1~{page_total}(当前是第{page_cur}页),按回车【Enter】结束输入:''')
                        if not n_page.isdigit() or int(n_page) not in range(1, page_total+1) or int(n_page)==page_cur:
                            msg.warn('输入非法!输入必须是符合要求的页码范围,且不能是当前页,请按任意键重新输入!')
                            input()
                            continue
                        else:
                            break
                    jumpPage(browser, page_n=n_page)
                    msg.info('正在跳转,请稍后...')
                    time.sleep(3)
                    page_cur = n_page

                elif option == '3':
                    '返回搜索页'
                    jumpBack(browser)
                    break
        except Exception as e:
            msg.fail('程序遇到了错误, 程序即将退出')
            log(colorStr(str(e), fg='red'))
            os.exit(0)

                
if __name__ == '__main__':
    Main()