# -*- coding: utf-8 -*-
import json
import os
import time
from typing import List, Tuple

import feedparser
import requests

# =========================
# 1. 基本配置
# =========================
TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
SEEN_FILE = "seen.json"

RSS_FEEDS: List[Tuple[str, str]] = [
    ("Fed News", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("IMF News", "https://www.imf.org/en/News/RSS"),
    ("ECB News", "https://www.ecb.europa.eu/rss/press.html"),
]

KEYWORDS = [
    "fed", "federal reserve", "ecb", "boj", "bank of england",
    "interest rate", "rates", "rate hike", "rate cut",
    "inflation", "cpi", "ppi", "pmi", "gdp",
    "policy", "stimulus", "liquidity", "employment", "payrolls",
    "yield", "treasury", "recession", "central bank", "monetary",
    "tariff", "trade", "sanction", "oil", "opec", "economy"
]

DELAY_BETWEEN_MESSAGES = 2


# =========================
# 2. ntfy 推送
# =========================
def send_ntfy(
    topic: str,
    message: str,
    title: str = "Macro Training",
    priority: str = "4",
    tags: str = "money",
) -> None:
    if not topic:
        raise RuntimeError("NTFY_TOPIC is empty")

    url = "https://ntfy.sh/{}".format(topic)
    r = requests.post(
        url,
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": tags,
        },
        timeout=15,
    )
    r.raise_for_status()
    print("ntfy 发送成功:", title)


# =========================
# 3. RSS 抓取
# =========================
def fetch_feed(url: str, timeout: int = 15):
    r = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    r.raise_for_status()
    return feedparser.parse(r.content)


# =========================
# 4. seen.json 去重
# =========================
def load_seen() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            print("seen.json 是空文件，按空记录处理")
            return set()

        data = json.loads(content)

        if isinstance(data, list):
            return set(data)

        print("seen.json 不是列表格式，按空记录处理")
        return set()

    except (json.JSONDecodeError, OSError) as e:
        print("seen.json 读取失败，按空记录处理：", str(e))
        return set()


def save_seen(seen: set) -> None:
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(seen)), f, ensure_ascii=False, indent=2)
    except OSError as e:
        print("保存 seen.json 失败：", str(e))


# =========================
# 5. 关键词过滤
# =========================
def is_policy_news(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in KEYWORDS)


# =========================
# 6. 基础推演
# =========================
def macro_reasoning(text: str) -> str:
    t = (text or "").lower()

    if "inflation" in t or "cpi" in t or "ppi" in t:
        return (
            "【推演】\n\n"
            "→ 通胀压力上升\n"
            "→ 市场提高高利率预期\n"
            "→ 美债收益率倾向上行\n"
            "→ 美元倾向走强\n"
            "→ 黄金承压\n"
            "→ 股市承压，尤其成长股\n\n"
            "【原理】\n"
            "通胀越强，央行越难宽松，资金价格越高。"
        )

    if "rate hike" in t or "raise rates" in t or "hawkish" in t or "higher for longer" in t:
        return (
            "【推演】\n\n"
            "→ 利率预期上升\n"
            "→ 融资成本上升\n"
            "→ 经济活动降温\n"
            "→ 美债收益率上行\n"
            "→ 美元走强\n"
            "→ 黄金与成长股承压\n\n"
            "【原理】\n"
            "利率是资金的价格，价格更高通常不利于风险资产。"
        )

    if "rate cut" in t or "cut rates" in t or "dovish" in t:
        return (
            "【推演】\n\n"
            "→ 利率预期下降\n"
            "→ 流动性改善\n"
            "→ 美债收益率倾向下行\n"
            "→ 美元偏弱\n"
            "→ 黄金和股市通常受支撑\n\n"
            "【原理】\n"
            "资金成本下降，会抬升风险资产估值。"
        )

    if "employment" in t or "payrolls" in t or "jobs" in t or "unemployment" in t:
        return (
            "【推演】\n\n"
            "→ 就业数据会影响央行对经济热度的判断\n"
            "→ 就业过强：高利率预期上升\n"
            "→ 就业转弱：降息预期上升\n"
            "→ 进而影响美元、美债、黄金和股市\n\n"
            "【原理】\n"
            "就业是央行判断经济与通胀压力的重要指标。"
        )

    if "yield" in t or "treasury" in t or "bond" in t:
        return (
            "【推演】\n\n"
            "→ 收益率变化会改变全球资产定价基准\n"
            "→ 收益率上行通常利好美元\n"
            "→ 对黄金和高估值股票不利\n\n"
            "【原理】\n"
            "无风险利率是很多资产估值的锚。"
        )

    if "tariff" in t or "trade" in t or "sanction" in t:
        return (
            "【推演】\n\n"
            "→ 贸易摩擦或制裁会提升不确定性和成本\n"
            "→ 可能推升部分商品价格并压制增长预期\n"
            "→ 对股市、汇率和大宗商品有连锁影响\n\n"
            "【原理】\n"
            "政策改变的是跨境流动和成本结构。"
        )

    if "oil" in t or "opec" in t or "energy" in t:
        return (
            "【推演】\n\n"
            "→ 能源价格上升会增加通胀压力\n"
            "→ 市场可能提高高利率预期\n"
            "→ 连带影响美元、黄金、债券和股市\n\n"
            "【原理】\n"
            "油价是宏观系统的重要输入变量。"
        )

    return (
        "【推演】\n\n"
        "→ 先识别这条新闻改变了哪个变量\n"
        "→ 再判断影响的是利率、增长、通胀还是流动性\n"
        "→ 最后推导美元 / 美债 / 黄金 / 股市\n\n"
        "【原理】\n"
        "宏观分析的重点是因果链，而不是背答案。"
    )


# =========================
# 7. 消息模板
# =========================
def build_prediction_prompt(source_name: str, title: str, link: str) -> str:
    return (
        "【政策 / 宏观新闻】\n\n"
        "来源：{}\n"
        "标题：{}\n\n"
        "👉 先自己预测：\n"
        "- 利率预期？\n"
        "- 美元？\n"
        "- 美债收益率？\n"
        "- 黄金？\n"
        "- 股市？\n\n"
        "（先想，再看下一条推演）\n\n"
        "链接：{}"
    ).format(source_name, title, link)


def build_reasoning_message(source_name: str, title: str, link: str) -> str:
    reasoning = macro_reasoning(title)
    return (
        "【标准推演】\n\n"
        "来源：{}\n"
        "标题：{}\n\n"
        "{}\n\n"
        "链接：{}"
    ).format(source_name, title, reasoning, link)


# =========================
# 8. 主程序
# =========================
def main():
    print("开始运行 macro_train_ntfy.py")
    print("NTFY_TOPIC =", TOPIC if TOPIC else "[EMPTY]")

    if not TOPIC:
        raise RuntimeError("Missing NTFY_TOPIC secret")

    seen = load_seen()
    pushed_count = 0
    checked_count = 0

    for source_name, feed_url in RSS_FEEDS:
        print("正在抓取:", source_name, feed_url)

        try:
            feed = fetch_feed(feed_url, timeout=15)
        except Exception as e:
            print("抓取失败:", source_name, str(e))
            continue

        print("抓到 entries 数量:", len(feed.entries))

        if not feed.entries:
            continue

        for entry in feed.entries[:5]:
            checked_count += 1

            title = entry.get("title", "No title").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link", "").strip()

            print("检查新闻:", title)

            if not link:
                print("无链接，跳过")
                continue

            if link in seen:
                print("已发送过，跳过")
                continue

            full_text = "{} {}".format(title, summary)

            if not is_policy_news(full_text):
                print("未命中关键词，跳过")
                continue

            msg1 = build_prediction_prompt(source_name, title, link)
            msg2 = build_reasoning_message(source_name, title, link)

            try:
                send_ntfy(
                    TOPIC,
                    msg1,
                    title="Macro Training",
                    priority="4",
                    tags="thinking",
                )
                time.sleep(DELAY_BETWEEN_MESSAGES)
                send_ntfy(
                    TOPIC,
                    msg2,
                    title="Macro Answer",
                    priority="3",
                    tags="chart_with_upwards_trend",
                )
            except Exception as e:
                print("ntfy 发送失败:", str(e))
                continue

            seen.add(link)
            pushed_count += 1
            print("本条已推送")

    save_seen(seen)
    print("检查新闻数:", checked_count)
    print("本次新增推送数:", pushed_count)

    if pushed_count == 0:
        test_msg = (
            "【GitHub Actions 测试】\n\n"
            "脚本已成功运行，但本次没有命中新新闻。\n"
            "这说明 workflow 是通的，后续只需调整 RSS 源或关键词。"
        )
        try:
            send_ntfy(
                TOPIC,
                test_msg,
                title="Macro Bot Test",
                priority="3",
                tags="white_check_mark",
            )
            print("已发送兜底测试消息")
        except Exception as e:
            print("兜底测试消息发送失败:", str(e))


if __name__ == "__main__":
    main()
