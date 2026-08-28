import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

# Telegram 频道列表（已去除多余空格）
channels = [
    "https://t.me/s/vmessiran",
    "https://t.me/s/mrsoulb",
    "https://t.me/s/v2xay",
    "https://t.me/s/vpnaloo",
    "https://t.me/s/v2ray_configs_pool",
    "https://t.me/s/V2RAY_VMESS_free",
    "https://t.me/s/FreakConfig",
    "https://t.me/s/v2rayNG_Matsuri",
    "https://t.me/s/meli_proxyy",
    "https://t.me/s/Daily_Configs",
    "https://t.me/s/customv2ray",
    "https://t.me/s/i10VPN",
    "https://t.me/s/ShareCentrePro",
]

# 请求头配置
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

raw_configs = []
supported_protocols = ("vmess://", "vless://", "ss://", "trojan://", "ssr://", "tuic://", "hy2://", "hysteria2://")
proto_pattern = re.compile(r'(?:vmess|vless|ss|trojan|ssr|tuic|hy2|hysteria2)://[^\s\'"<>)]+', re.IGNORECASE)

# 1. 抓取网页并提取节点配置
for url in channels:
    try:
        response = requests.get(url.strip(), headers=headers, timeout=15)
        if response.status_code != 200:
            continue
        page_html = response.text
    except Exception as e:
        print(f"请求失败: {url} -> {e}")
        continue

    soup = BeautifulSoup(page_html, "html.parser")
    found_any = False

    # 优先从 <code> 标签中提取
    for code_tag in soup.find_all("code"):
        text = code_tag.text.strip()
        for line in text.splitlines():
            line = line.strip()
            if any(line.lower().startswith(p) for p in supported_protocols):
                raw_configs.append(line)
                found_any = True

    # 从 <a> 标签的 href 中提取
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if any(href.lower().startswith(p) for p in supported_protocols):
            raw_configs.append(href)
            found_any = True

    # 若标签中未找到，使用正则全文本兜底匹配
    if not found_any:
        matches = proto_pattern.findall(page_html)
        for m in matches:
            raw_configs.append(m.strip())

# 2. 清洗数据（去除原有的 #备注）并进行核心去重
cleaned_configs = []
seen_cores = set()

for config in raw_configs:
    config = config.strip()
    if not config:
        continue

    # 正确去除 # 及后面的备注信息，防止协议头丢失
    base_config = config.split("#")[0].strip()

    # 规范化判断依据（去掉参数等，用于判断是否是同一节点）
    norm_key = base_config.split("?")[0].rstrip("/")

    if norm_key not in seen_cores:
        seen_cores.add(norm_key)
        cleaned_configs.append(base_config)

# 3. 获取北京时间并生成注释
tz = pytz.timezone("Asia/Shanghai")
now = datetime.now(tz)
time_str = now.strftime("%m月%d日 | %H:%M")
date_str = now.strftime("%m月%d日")

# 4. 重新组装并写入 config.txt
final_output = []
for index, config in enumerate(cleaned_configs):
    if index == 0:
        # 第一条写入更新时间
        remark = f"#🌐已更新于 {time_str} | 每15分钟更新一次"
    else:
        # 后续节点按序号命名
        remark = f"#🌐服务器{index} | {date_str} | bin1site1.github.io"
    
    final_output.append(f"{config}{remark}")

with open("config.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(final_output) + ("\n" if final_output else ""))

print(f"处理完成，共生成 {len(final_output)} 个有效节点。")
